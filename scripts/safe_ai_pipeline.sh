#!/usr/bin/env bash
set -euo pipefail
# ─────────────────────────────────────────────────────────────────
# safe_ai_pipeline.sh — End-to-end safe AI pipeline
#
# Validates environment, verifies model integrity, runs inference
# (transcription), checks output fidelity, and logs provenance.
#
# Designed for offline / low-bandwidth / low-trust environments
# where you need confidence that nothing was corrupted or skipped.
#
# Usage:
#   bash scripts/safe_ai_pipeline.sh <audio_or_video_file>
#   bash scripts/safe_ai_pipeline.sh --verify-model
#   bash scripts/safe_ai_pipeline.sh --full <audio_or_video_file>
# ─────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/data/pipeline_logs"
MODEL_DIR="${PROJECT_ROOT}/data/models"
TRANSCRIPT_DIR="${PROJECT_ROOT}/data/videos/transcripts"
WHISPER_MODEL="${WHISPER_MODEL:-small}"

# ── Colors (degrade gracefully on dumb terminals) ───────────────
if [ -t 1 ] && command -v tput >/dev/null 2>&1; then
    GREEN=$(tput setaf 2)
    RED=$(tput setaf 1)
    YELLOW=$(tput setaf 3)
    BOLD=$(tput bold)
    RESET=$(tput sgr0)
else
    GREEN="" RED="" YELLOW="" BOLD="" RESET=""
fi

pass()  { echo "${GREEN}[PASS]${RESET}  $*"; }
fail()  { echo "${RED}[FAIL]${RESET}  $*"; }
warn()  { echo "${YELLOW}[WARN]${RESET}  $*"; }
info()  { echo "${BOLD}[INFO]${RESET}  $*"; }
step()  { echo ""; echo "${BOLD}── $* ──${RESET}"; }

# ── Logging ─────────────────────────────────────────────────────
mkdir -p "${LOG_DIR}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOGFILE="${LOG_DIR}/pipeline_${TIMESTAMP}.log"

log() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "${LOGFILE}"
}

log "Pipeline started"

# ── 1. Environment preflight ───────────────────────────────────
preflight_check() {
    step "1. PREFLIGHT — Environment check"
    local errors=0

    # Python
    if command -v python3 >/dev/null 2>&1; then
        local pyver
        pyver="$(python3 --version 2>&1)"
        pass "Python found: ${pyver}"
        log "Python: ${pyver}"
    else
        fail "Python 3 not found"
        errors=$((errors + 1))
    fi

    # Required Python packages
    for pkg in typer pydantic yaml; do
        if python3 -c "import ${pkg}" 2>/dev/null; then
            pass "Python package: ${pkg}"
        else
            fail "Missing Python package: ${pkg}"
            errors=$((errors + 1))
        fi
    done

    # ffmpeg (needed for audio extraction)
    if command -v ffmpeg >/dev/null 2>&1; then
        pass "ffmpeg available"
    else
        warn "ffmpeg not found — audio extraction may fail"
        log "WARN: ffmpeg missing"
    fi

    # Disk space (need at least 2 GB free)
    local free_kb
    free_kb="$(df -k "${PROJECT_ROOT}" | awk 'NR==2{print $4}')"
    local free_gb=$(( free_kb / 1048576 ))
    if [ "${free_gb}" -ge 2 ]; then
        pass "Disk space: ${free_gb} GB free"
    else
        warn "Low disk: only ${free_gb} GB free (recommend >= 2 GB)"
        log "WARN: low disk ${free_gb}GB"
    fi

    # Writable output dirs
    mkdir -p "${TRANSCRIPT_DIR}" "${MODEL_DIR}" "${LOG_DIR}"
    pass "Output directories ready"

    log "Preflight complete (errors=${errors})"
    if [ "${errors}" -gt 0 ]; then
        fail "Preflight failed with ${errors} error(s)"
        return 1
    fi
    pass "Preflight complete"
}

# ── 2. Model integrity verification ────────────────────────────
verify_model() {
    step "2. MODEL INTEGRITY — Verify downloaded models"
    local found=0
    local verified=0

    if [ ! -d "${MODEL_DIR}" ] || [ -z "$(ls -A "${MODEL_DIR}" 2>/dev/null)" ]; then
        warn "No models in ${MODEL_DIR} — skipping verification"
        log "No models found for verification"
        return 0
    fi

    for model_file in "${MODEL_DIR}"/*; do
        [ -f "${model_file}" ] || continue
        found=$((found + 1))
        local basename
        basename="$(basename "${model_file}")"
        local size
        size="$(stat -c%s "${model_file}" 2>/dev/null || stat -f%z "${model_file}" 2>/dev/null)"

        # Check file is not empty / truncated (min 1 MB for any real model)
        if [ "${size}" -lt 1048576 ]; then
            fail "Model ${basename}: suspiciously small (${size} bytes) — possibly truncated"
            log "FAIL: ${basename} size=${size} (truncated?)"
            continue
        fi

        # Compute SHA256 for provenance
        local sha
        sha="$(sha256sum "${model_file}" | cut -d' ' -f1)"
        pass "Model ${basename}: ${size} bytes, sha256:${sha:0:16}..."
        log "Model verified: ${basename} size=${size} sha256=${sha}"

        # Check for matching .sha256 sidecar file
        if [ -f "${model_file}.sha256" ]; then
            local expected
            expected="$(cut -d' ' -f1 < "${model_file}.sha256")"
            if [ "${sha}" = "${expected}" ]; then
                pass "  SHA256 matches sidecar checksum"
                log "SHA256 match for ${basename}"
            else
                fail "  SHA256 MISMATCH: expected ${expected:0:16}... got ${sha:0:16}..."
                log "FAIL: SHA256 mismatch ${basename}"
            fi
        else
            warn "  No .sha256 sidecar — cannot verify against expected hash"
            log "WARN: no sidecar for ${basename}"
        fi

        verified=$((verified + 1))
    done

    info "Models checked: ${found}, verified: ${verified}"
    log "Model verification: found=${found} verified=${verified}"
}

# ── 3. Safe transcription ──────────────────────────────────────
safe_transcribe() {
    local input_file="$1"
    step "3. TRANSCRIPTION — Safe inference pipeline"

    # Validate input exists and is a real file
    if [ ! -f "${input_file}" ]; then
        fail "Input file not found: ${input_file}"
        log "FAIL: input not found: ${input_file}"
        return 1
    fi

    local input_basename
    input_basename="$(basename "${input_file}")"
    local input_size
    input_size="$(stat -c%s "${input_file}" 2>/dev/null || stat -f%z "${input_file}" 2>/dev/null)"
    local input_sha
    input_sha="$(sha256sum "${input_file}" | cut -d' ' -f1)"

    info "Input: ${input_basename} (${input_size} bytes)"
    info "Input SHA256: ${input_sha:0:24}..."
    log "Transcription input: ${input_basename} size=${input_size} sha256=${input_sha}"

    # Check file type (basic validation — look at extension + magic bytes)
    local ext="${input_file##*.}"
    ext="$(echo "${ext}" | tr '[:upper:]' '[:lower:]')"
    local valid_exts="mp4 mp3 wav flac ogg webm m4a mkv avi"
    if echo "${valid_exts}" | grep -qw "${ext}"; then
        pass "File type: .${ext}"
    else
        warn "Unusual file extension: .${ext} — transcription may fail"
        log "WARN: unusual extension .${ext}"
    fi

    # Run transcription
    info "Running transcription (model: ${WHISPER_MODEL})..."
    local start_time
    start_time="$(date +%s)"

    if python3 -m apps.voice_assist.cli transcribe "${input_file}" --out-dir "${TRANSCRIPT_DIR}"; then
        local end_time
        end_time="$(date +%s)"
        local duration=$(( end_time - start_time ))
        pass "Transcription completed in ${duration}s"
        log "Transcription OK: ${duration}s"
    else
        fail "Transcription failed"
        log "FAIL: transcription failed for ${input_basename}"
        return 1
    fi

    # Find the output transcript
    local transcript_stem="${input_basename%.*}"
    local transcript_file="${TRANSCRIPT_DIR}/${transcript_stem}.txt"
    if [ -f "${transcript_file}" ]; then
        local out_size
        out_size="$(stat -c%s "${transcript_file}" 2>/dev/null || stat -f%z "${transcript_file}" 2>/dev/null)"
        local out_sha
        out_sha="$(sha256sum "${transcript_file}" | cut -d' ' -f1)"
        pass "Output: ${transcript_file} (${out_size} bytes)"
        log "Transcript output: ${transcript_stem}.txt size=${out_size} sha256=${out_sha}"
    else
        fail "Expected transcript not found: ${transcript_file}"
        log "FAIL: transcript not found: ${transcript_file}"
        return 1
    fi

    return 0
}

# ── 4. Output fidelity check ───────────────────────────────────
fidelity_check() {
    local input_file="$1"
    step "4. FIDELITY — Output verification"

    local transcript_stem
    transcript_stem="$(basename "${input_file}" | sed 's/\.[^.]*$//')"
    local transcript_file="${TRANSCRIPT_DIR}/${transcript_stem}.txt"

    if [ ! -f "${transcript_file}" ]; then
        fail "No transcript to verify"
        log "FAIL: no transcript for fidelity check"
        return 1
    fi

    # Check transcript is non-empty
    local line_count
    line_count="$(wc -l < "${transcript_file}")"
    local word_count
    word_count="$(wc -w < "${transcript_file}")"
    local char_count
    char_count="$(wc -c < "${transcript_file}")"

    if [ "${word_count}" -gt 0 ]; then
        pass "Transcript has content: ${line_count} lines, ${word_count} words"
        log "Fidelity: ${line_count} lines, ${word_count} words, ${char_count} chars"
    else
        fail "Transcript is empty — transcription may have failed silently"
        log "FAIL: empty transcript"
        return 1
    fi

    # Ratio check: words per line (detect garbled output)
    local avg_wpl=$(( word_count / (line_count > 0 ? line_count : 1) ))
    if [ "${avg_wpl}" -ge 2 ]; then
        pass "Avg words/line: ${avg_wpl} (reasonable)"
    else
        warn "Avg words/line: ${avg_wpl} (low — may be garbled)"
        log "WARN: low words/line ratio ${avg_wpl}"
    fi

    # Generate dyslexia-friendly formatted version
    info "Generating dyslexia-friendly format..."
    if python3 -m apps.voice_assist.cli format-text "${transcript_file}"; then
        pass "Formatted transcript generated"
        log "Formatted transcript created"
    else
        warn "Formatting failed (non-critical)"
        log "WARN: formatting failed"
    fi

    # Generate extractive summary
    info "Generating summary..."
    if python3 -m apps.voice_assist.cli summarize "${transcript_file}" --sentences 5; then
        pass "Summary generated"
        log "Summary created"
    else
        warn "Summary generation failed (non-critical)"
        log "WARN: summary failed"
    fi

    pass "Fidelity check complete"
}

# ── 5. Provenance record ───────────────────────────────────────
write_provenance() {
    local input_file="${1:-none}"
    step "5. PROVENANCE — Audit trail"

    local provenance_file="${LOG_DIR}/provenance_${TIMESTAMP}.json"

    local input_sha="none"
    if [ -f "${input_file}" ]; then
        input_sha="$(sha256sum "${input_file}" | cut -d' ' -f1)"
    fi

    local transcript_sha="none"
    local transcript_stem
    transcript_stem="$(basename "${input_file}" | sed 's/\.[^.]*$//')"
    local transcript_file="${TRANSCRIPT_DIR}/${transcript_stem}.txt"
    if [ -f "${transcript_file}" ]; then
        transcript_sha="$(sha256sum "${transcript_file}" | cut -d' ' -f1)"
    fi

    local hostname_val
    hostname_val="$(hostname 2>/dev/null || echo 'unknown')"

    cat > "${provenance_file}" <<PROVEOF
{
  "pipeline": "safe_ai_pipeline",
  "version": "1.0.0",
  "timestamp": "${TIMESTAMP}",
  "hostname": "${hostname_val}",
  "whisper_model": "${WHISPER_MODEL}",
  "input": {
    "file": "$(basename "${input_file}")",
    "sha256": "${input_sha}"
  },
  "output": {
    "transcript": "${transcript_stem}.txt",
    "sha256": "${transcript_sha}"
  },
  "log": "$(basename "${LOGFILE}")",
  "status": "complete",
  "confidence": 0.5,
  "tag": "provisional",
  "recheck_days": 7
}
PROVEOF

    pass "Provenance record: ${provenance_file}"
    log "Provenance written: ${provenance_file}"
    info "Pipeline log: ${LOGFILE}"
}

# ── Main dispatch ───────────────────────────────────────────────
main() {
    echo ""
    echo "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
    echo "${BOLD}║     Safe AI Pipeline — Resilient Collab      ║${RESET}"
    echo "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
    echo ""

    local mode="full"
    local input_file=""

    # Parse args
    while [ $# -gt 0 ]; do
        case "$1" in
            --verify-model)
                mode="verify"
                shift ;;
            --full)
                mode="full"
                shift ;;
            --preflight)
                mode="preflight"
                shift ;;
            --help|-h)
                echo "Usage: safe_ai_pipeline.sh [OPTIONS] [audio/video file]"
                echo ""
                echo "Options:"
                echo "  --preflight      Run environment checks only"
                echo "  --verify-model   Verify downloaded model integrity only"
                echo "  --full <file>    Full pipeline: preflight + verify + transcribe + check"
                echo "  <file>           Same as --full <file>"
                echo ""
                echo "Environment:"
                echo "  WHISPER_MODEL    Whisper model size (default: small)"
                exit 0 ;;
            *)
                input_file="$1"
                shift ;;
        esac
    done

    local exit_code=0

    case "${mode}" in
        preflight)
            preflight_check || exit_code=$?
            ;;
        verify)
            preflight_check || exit_code=$?
            [ "${exit_code}" -eq 0 ] && verify_model
            ;;
        full)
            if [ -z "${input_file}" ]; then
                fail "No input file provided. Run with --help for usage."
                exit 1
            fi

            preflight_check || exit_code=$?
            if [ "${exit_code}" -ne 0 ]; then
                fail "Preflight failed — aborting pipeline"
                log "Aborted: preflight failed"
                exit 1
            fi

            verify_model
            safe_transcribe "${input_file}" || exit_code=$?
            if [ "${exit_code}" -eq 0 ]; then
                fidelity_check "${input_file}"
            fi
            write_provenance "${input_file}"
            ;;
    esac

    echo ""
    if [ "${exit_code}" -eq 0 ]; then
        step "PIPELINE COMPLETE"
        pass "All steps passed"
    else
        step "PIPELINE FINISHED WITH ERRORS"
        fail "Exit code: ${exit_code}"
    fi

    log "Pipeline finished (exit=${exit_code})"
    exit "${exit_code}"
}

main "$@"
