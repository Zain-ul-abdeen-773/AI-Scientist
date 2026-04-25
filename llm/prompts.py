"""
Prompt Templates — All LLM Prompts for The AI Scientist
========================================================
Centralized prompt management for reproducibility.
Each prompt is designed for structured, actionable output
that a real scientist would trust.
"""


# ═══════════════════════════════════════════════════════════════
# System Prompt — AI Scientist Persona
# ═══════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are The AI Scientist — an expert research assistant that helps scientists design rigorous, operationally-grounded experiments.

Your core principles:
1. SPECIFICITY — Always name exact reagents, catalog numbers, suppliers, and concentrations
2. GROUNDING — Reference real published protocols from protocols.io, Bio-protocol, Nature Protocols, or JOVE
3. RIGOR — Include proper controls, statistical analysis plans, and sample size justifications
4. PRACTICALITY — Generate plans a lab could pick up on Monday and start running by Friday
5. HONESTY — If you're unsure about a detail, say so explicitly rather than fabricating

You output well-structured markdown with clear section headers."""


# ═══════════════════════════════════════════════════════════════
# Literature QC — Novelty Assessment
# ═══════════════════════════════════════════════════════════════
NOVELTY_ASSESSMENT_PROMPT = """You are assessing the novelty of a scientific hypothesis by comparing it against existing literature.

## Hypothesis
{hypothesis}

## Found Papers
{papers_summary}

## Instructions
Analyze the hypothesis against the found papers and determine:

1. **Novelty Signal**: Choose exactly one:
   - "not found" — No existing work matches this hypothesis
   - "similar work exists" — Related experiments exist but differ in key aspects
   - "exact match found" — This experiment (or nearly identical) has been published

2. **Justification**: 2-3 sentences explaining your assessment

3. **Key References**: List the 1-3 most relevant papers with titles and brief relevance notes

Format your response as:

### Novelty Signal
[signal]

### Justification
[your reasoning]

### Key References
1. [Title] — [relevance note]
2. [Title] — [relevance note]
3. [Title] — [relevance note]"""


# ═══════════════════════════════════════════════════════════════
# Full Experiment Plan Generation (Single-Shot)
# ═══════════════════════════════════════════════════════════════
FULL_PLAN_PROMPT = """Generate a complete, operationally-grounded experiment plan for the following scientific hypothesis.

## Hypothesis
{hypothesis}

## Literature Context
{literature_context}

{feedback_context}

## Required Sections

### 1. Protocol
Generate a step-by-step experimental protocol. Each step must include:
- Clear action description
- Specific parameters (temperatures, durations, concentrations)
- Equipment needed for that step
- Critical notes or common pitfalls
- Reference to established protocols where applicable (protocols.io, Bio-protocol, Nature Protocols)

### 2. Materials & Supply Chain
Create a detailed materials list with:
- Reagent/material name
- Catalog number (use real ones from Thermo Fisher, Sigma-Aldrich, etc.)
- Supplier name
- Quantity needed
- Unit price estimate (USD)
- Storage conditions

### 3. Budget
Provide a realistic budget breakdown:
- Line items grouped by category (reagents, consumables, equipment, personnel)
- Unit costs and quantities
- Subtotals per category
- Grand total
- Format as a clear table

### 4. Timeline
Create a phased project timeline:
- Break into phases (Preparation, Execution, Analysis, Reporting)
- Duration for each phase and sub-task
- Dependencies between tasks
- Total estimated duration
- Key milestones and decision points

### 5. Validation Approach
Define how success or failure will be measured:
- Primary endpoints with quantitative thresholds
- Statistical analysis plan (tests, significance level, power)
- Positive and negative controls
- Sample size justification
- Potential confounders and mitigation strategies

---

**Quality standard: Would a real scientist trust this plan enough to order the materials and start running it? That is the bar.**

Generate the complete plan now in well-formatted markdown:"""


# ═══════════════════════════════════════════════════════════════
# Individual Section Prompts (for modular generation)
# ═══════════════════════════════════════════════════════════════

PROTOCOL_PROMPT = """Generate a detailed step-by-step experimental protocol for:

## Hypothesis
{hypothesis}

## Requirements
- Number each step clearly
- Include specific parameters (temperatures, durations, concentrations, RPM)
- Mention equipment needed at each step
- Add critical notes for tricky steps
- Reference published protocols where applicable (protocols.io, Bio-protocol)
- Include safety precautions where relevant

Generate the protocol in markdown format:"""


MATERIALS_BUDGET_PROMPT = """Generate a detailed materials list and budget for this experiment:

## Hypothesis
{hypothesis}

## Protocol Summary
{protocol_summary}

## Requirements
Generate TWO sections:

### Materials & Supply Chain
A table with columns: Material | Catalog # | Supplier | Quantity | Unit Price (USD) | Storage
- Use real catalog numbers from Thermo Fisher, Sigma-Aldrich, Promega, etc.
- Include ALL reagents, consumables, and equipment

### Budget Breakdown
A table with columns: Category | Item | Quantity | Unit Cost | Total Cost
Categories: Reagents, Consumables, Equipment (purchase/rental), Personnel, Overhead
- Include subtotals per category
- Include grand total
- Be realistic with pricing

Generate in markdown table format:"""


TIMELINE_PROMPT = """Generate a detailed project timeline for this experiment:

## Hypothesis
{hypothesis}

## Protocol Summary
{protocol_summary}

## Requirements
- Break into clear phases: Preparation → Execution → Analysis → Reporting
- For each phase, list sub-tasks with durations
- Show dependencies (what must complete before what)
- Include milestones and go/no-go decision points
- Estimate total project duration
- Format as a structured timeline

Generate in markdown format:"""


VALIDATION_PROMPT = """Design a validation approach for this experiment:

## Hypothesis
{hypothesis}

## Protocol Summary
{protocol_summary}

## Requirements
Define:
1. **Primary Endpoints** — What exactly will be measured? What threshold defines success?
2. **Statistical Analysis Plan** — Which tests, significance level (α), power analysis
3. **Controls** — Positive controls, negative controls, vehicle controls
4. **Sample Size Justification** — Based on expected effect size and power
5. **Potential Confounders** — What could go wrong and how to mitigate
6. **Data Recording** — How data will be captured and stored

Generate in markdown format:"""


# ═══════════════════════════════════════════════════════════════
# Feedback Integration
# ═══════════════════════════════════════════════════════════════
FEEDBACK_CONTEXT_TEMPLATE = """## Prior Scientist Feedback
The following corrections were provided by scientists for similar experiments.
Incorporate these learnings into your plan:

{feedback_items}

Use these corrections to improve accuracy of the current plan."""
