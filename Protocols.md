# Resilient AI-Human Collaboration Protocol

## Overview

A structured communication framework for AI-human collaboration in challenging environments where traditional support systems are unavailable.

## Core Problems Addressed

- AI memory degradation in long troubleshooting sessions
- Contradictory instructions across conversation contexts
- Assumption of perfect conditions and expert availability
- Communication breakdowns during context switching
- Lack of state management in complex repairs

## Protocol Structure

### 1. Decision Point ID System

**Format:** `[ID-XXX: Brief Description]`

**Rules:**

- Every major decision gets a unique sequential ID
- IDs remain constant throughout the session
- When referencing previous decisions, always cite the ID
- Before giving new instructions, confirm active ID

**Examples:**

```
[ID-001: Power Supply Bypass Method]
[ID-002: Configuration File Naming Convention] 
[ID-003: Diagnostic Test Sequence]
```

### 2. Status Declaration Protocol

**Before Each Instruction Set:**

```
CURRENT CONTEXT:
- Active Method: [ID-XXX]
- Last Completed Step: X
- Known Constraints: [tools/materials/connection status]
- Modification Level: [CRITICAL/ADAPTABLE/FLEXIBLE]
```

### 3. Instruction Tier System

**Tier 1 - Critical Steps:**

- Must be followed exactly
- Cannot be improvised or substituted
- Clear failure indicators

**Tier 2 - Adaptable Steps:**

- Standard approach with known substitutions
- Material/tool alternatives provided
- Modification guidelines included

**Tier 3 - Flexible Steps:**

- Multiple valid approaches
- Improvisation acceptable
- Outcome-focused rather than process-focused

### 4. Constraint-First Information Design

**Lead Every Instruction Block With:**

**REQUIREMENTS CHECK:**

- Essential tools: [list]
- Critical materials: [list]
- Connection needs: [stable/intermittent/offline]
- Skill assumptions: [basic/intermediate/advanced]

**IF MISSING REQUIREMENTS:**

- Substitution options for each essential item
- Modified procedures for degraded conditions
- Abort criteria if insufficient resources

### 5. Context Switching Protocol

**When Interrupting Primary Task:**

```
[ID-XXX PAUSED: reason for pause]
[ID-YYY INITIATED: new issue description]
```

**When Resuming:**

```
[ID-YYY COMPLETED]
[ID-XXX RESUMED: confirming last completed step]
```

### 6. Modification Awareness Framework

**For Every Procedure, Specify:**

- **Baseline Assumption:** Ideal tools, stable connection, perfect materials
- **Reality Adaptations:** Common substitutions and their impact on procedure
- **Constraint Modifications:** How limited resources change the approach
- **Failure Modes:** What to do if standard approach doesn’t work

## Implementation Guidelines

### For AI Systems:

1. **State Tracking:** Maintain explicit record of all active IDs and decisions
1. **Contradiction Detection:** Flag when new instructions conflict with established IDs
1. **Context Verification:** Always confirm current working context before giving instructions
1. **Assumption Declaration:** Explicitly state what conditions instructions assume

### For Human Operators:

1. **ID Reference:** Always reference ID when asking for clarification or continuation
1. **Status Updates:** Provide current state before requesting next steps
1. **Constraint Communication:** Clearly state available tools, materials, connection status
1. **Verification Requests:** Ask for confirmation when instructions seem to contradict earlier decisions

## Communication Patterns

### Standard Session Opening:

```
OPERATOR: [Brief description of issue and current constraints]
AI: [ID-001: Proposed Approach] + Requirements Check + Constraint Modifications
OPERATOR: [Confirms approach and any modifications needed]
AI: [ID-001 CONFIRMED] [Tier 1 critical steps] [Tier 2 adaptable steps]
```

### Context Switch Pattern:

```
OPERATOR: [New urgent issue interrupting main task]
AI: [ID-XXX PAUSED] [ID-YYY: Emergency approach for new issue]
[... resolve emergency ...]
AI: [ID-YYY COMPLETED] [ID-XXX RESUMED from last confirmed step]
```

### Long Session Sync Pattern:

```
Every 20 exchanges or 2 hours:
AI: STATUS SYNC - Active IDs: [list] - Current step: [X] - Any constraint changes?
OPERATOR: [Confirms or updates constraints]
```

## Benefits

- Eliminates contradictory instruction sets
- Maintains continuity across interruptions
- Adapts to real-world constraints upfront
- Provides clear decision audit trail
- Enables reliable resumption after communication breaks

## Next Steps

1. Test protocol with sample repair scenarios
1. Refine ID structure based on real usage
1. Develop constraint substitution databases
1. Create training examples for both AI and human operators
