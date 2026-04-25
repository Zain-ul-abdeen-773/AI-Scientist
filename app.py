"""
The AI Scientist — Gradio Web Application
===========================================
Full demo UI with 4 tabs:
    1. Input & Literature QC — Enter hypothesis, see novelty check
    2. Experiment Plan — Full plan with protocol, materials, budget,
       timeline, and validation
    3. Scientist Review — Rate, correct, and annotate plan sections
    4. System Info — Architecture, status, feedback stats

Hack-Nation × World Bank Youth Summit · Global AI Hackathon 2026
"""

import json
from typing import Optional, Tuple
from loguru import logger

import gradio as gr

from config import get_config, AppConfig
from llm.llm_client import LLMClient
from literature.novelty_checker import NoveltyChecker
from planner.experiment_planner import ExperimentPlanner
from feedback.feedback_store import FeedbackStore
from feedback.feedback_learner import FeedbackLearner


# ═══════════════════════════════════════════════════════════════
# Application State (shared across tabs)
# ═══════════════════════════════════════════════════════════════
class AppState:
    """Holds shared state between UI tabs."""

    def __init__(self, config: AppConfig):
        # Initialize all modules
        self.config = config
        self.llm = LLMClient(config.llm)
        self.novelty_checker = NoveltyChecker(config.literature, self.llm)
        self.feedback_store = FeedbackStore(config.feedback)
        self.feedback_learner = FeedbackLearner(
            self.feedback_store, config.feedback
        )
        self.planner = ExperimentPlanner(self.llm, self.feedback_learner)

        # State tracking
        self.last_hypothesis = ""
        self.last_novelty_result = {}
        self.last_plan = {}

        logger.info("AppState initialized — all modules ready")


# ═══════════════════════════════════════════════════════════════
# UI Event Handlers
# ═══════════════════════════════════════════════════════════════

def run_literature_qc(hypothesis: str, state: AppState):
    """
    Run literature QC and return novelty signal + references.

    Args:
        hypothesis: User's scientific hypothesis
        state: Shared application state

    Returns:
        Tuple of (novelty_badge, assessment_text, references_text)
    """
    if not hypothesis.strip():
        return (
            "⚠️ Please enter a hypothesis.",
            "",
            "",
        )

    state.last_hypothesis = hypothesis

    try:
        result = state.novelty_checker.check(hypothesis)
        state.last_novelty_result = result

        # Format novelty badge with color
        signal = result.get("signal", "unknown")
        badge_map = {
            "not found": "🟢 **NOT FOUND** — This appears to be novel!",
            "similar work exists": "🟡 **SIMILAR WORK EXISTS** — Related experiments found.",
            "exact match found": "🔴 **EXACT MATCH FOUND** — This has been done before.",
        }
        badge = badge_map.get(signal, f"⚪ {signal}")

        # Format assessment
        assessment = result.get("assessment_text", "")

        # Format references
        references = ""
        for i, ref in enumerate(result.get("references", [])[:3], 1):
            title = ref.get("title", "Untitled")
            url = ref.get("url", "")
            authors = ", ".join(ref.get("authors", [])[:3])
            year = ref.get("year") or ref.get("published", "")
            references += (
                f"**{i}.** [{title}]({url})\n"
                f"   {authors} ({year})\n\n"
            )

        if not references:
            references = "No references found."

        return badge, assessment, references

    except Exception as e:
        logger.error(f"Literature QC failed: {e}")
        return f"❌ Error: {str(e)}", "", ""


def generate_plan(
    hypothesis: str, mode: str, state: AppState
):
    """
    Generate the full experiment plan.

    Args:
        hypothesis: User's scientific hypothesis
        mode: "single_shot" or "modular"
        state: Shared application state

    Returns:
        Full plan markdown text
    """
    if not hypothesis.strip():
        return "⚠️ Please enter a hypothesis first."

    # Use stored hypothesis if available
    hyp = hypothesis or state.last_hypothesis
    state.last_hypothesis = hyp

    try:
        # Get literature context from last QC run
        lit_context = state.last_novelty_result.get("papers_summary", "")

        # Generate plan
        result = state.planner.generate_full_plan(
            hypothesis=hyp,
            literature_context=lit_context,
            mode=mode,
        )

        state.last_plan = result
        return result.get("full_plan", "No plan generated.")

    except Exception as e:
        logger.error(f"Plan generation failed: {e}")
        return f"❌ Error: {str(e)}"


def save_feedback(
    hypothesis: str,
    experiment_type: str,
    overall_rating: int,
    protocol_rating: int,
    protocol_correction: str,
    materials_rating: int,
    materials_correction: str,
    timeline_rating: int,
    timeline_correction: str,
    validation_rating: int,
    validation_correction: str,
    notes: str,
    state: AppState,
):
    """
    Save scientist feedback to the store.

    Returns:
        Status message
    """
    if not hypothesis.strip():
        return "⚠️ Please provide the hypothesis that was evaluated."

    feedback = {
        "hypothesis": hypothesis,
        "experiment_type": experiment_type,
        "domain": "",  # Could be auto-detected
        "overall_rating": int(overall_rating),
        "sections": {
            "protocol": {
                "rating": int(protocol_rating),
                "correction": protocol_correction,
                "original": state.last_plan.get("protocol", "")[:500],
            },
            "materials_budget": {
                "rating": int(materials_rating),
                "correction": materials_correction,
                "original": state.last_plan.get("materials_budget", "")[:500],
            },
            "timeline": {
                "rating": int(timeline_rating),
                "correction": timeline_correction,
                "original": state.last_plan.get("timeline", "")[:500],
            },
            "validation": {
                "rating": int(validation_rating),
                "correction": validation_correction,
                "original": state.last_plan.get("validation", "")[:500],
            },
        },
        "notes": notes,
    }

    try:
        feedback_id = state.feedback_store.save(feedback)
        stats = state.feedback_store.get_stats()
        return (
            f"✅ **Feedback saved!** (ID: `{feedback_id}`)\n\n"
            f"Total feedback items: {stats['total_count']}\n"
            f"Average rating: {stats['avg_rating']:.1f}/5\n\n"
            f"_This feedback will improve future plans for "
            f"similar {experiment_type} experiments._"
        )
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        return f"❌ Error saving feedback: {str(e)}"


# ═══════════════════════════════════════════════════════════════
# Build Gradio Application
# ═══════════════════════════════════════════════════════════════

def create_app(config: Optional[AppConfig] = None) -> gr.Blocks:
    """
    Build the full Gradio demo application.

    Args:
        config: Application configuration (uses default if None)

    Returns:
        Gradio Blocks application
    """
    config = config or get_config()
    state = AppState(config)

    # ── CSS for premium look ─────────────────────────────────
    custom_css = """
    .main-header {
        text-align: center;
        padding: 20px 0 10px 0;
    }
    .novelty-badge {
        font-size: 1.2em;
        padding: 10px 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .section-header {
        border-bottom: 2px solid #6366f1;
        padding-bottom: 5px;
        margin-top: 20px;
    }
    .feedback-saved {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 15px;
        border-radius: 10px;
    }
    """

    with gr.Blocks(
        title="The AI Scientist",
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="violet",
            neutral_hue="slate",
        ),
        css=custom_css,
    ) as app:

        # ── Header ──────────────────────────────────────────
        gr.Markdown(
            """
            <div class="main-header">

            # 🔬 The AI Scientist

            **Generate complete, operationally-grounded experiment plans from scientific hypotheses.**

            `Literature QC → Protocol → Materials & Budget → Timeline → Validation`

            </div>
            """,
        )

        with gr.Tabs():

            # ══════════════════════════════════════════════════
            # TAB 1: Input & Literature QC
            # ══════════════════════════════════════════════════
            with gr.Tab("📝 Input & Literature QC", id="input_tab"):
                gr.Markdown("### Enter your scientific hypothesis")
                gr.Markdown(
                    "_Write your hypothesis as a specific, testable statement "
                    "with measurable outcomes._"
                )

                hypothesis_input = gr.Textbox(
                    label="Scientific Hypothesis",
                    placeholder=(
                        "e.g., Supplementing C57BL/6 mice with Lactobacillus "
                        "rhamnosus GG for 4 weeks will reduce intestinal "
                        "permeability by at least 30% compared to controls, "
                        "measured by FITC-dextran assay..."
                    ),
                    lines=5,
                    elem_id="hypothesis_input",
                )

                with gr.Row():
                    qc_btn = gr.Button(
                        "🔍 Check Literature",
                        variant="primary",
                        scale=2,
                        elem_id="qc_button",
                    )
                    clear_btn = gr.Button(
                        "🗑️ Clear",
                        variant="secondary",
                        scale=1,
                    )

                # Sample inputs
                with gr.Accordion("💡 Sample Hypotheses", open=False):
                    gr.Markdown(
                        """
**Diagnostics:** A paper-based electrochemical biosensor functionalized with anti-CRP antibodies will detect C-reactive protein in whole blood at concentrations below 0.5 mg/L within 10 minutes, matching laboratory ELISA sensitivity without requiring sample preprocessing.

**Gut Health:** Supplementing C57BL/6 mice with Lactobacillus rhamnosus GG for 4 weeks will reduce intestinal permeability by at least 30% compared to controls, measured by FITC-dextran assay, due to upregulation of tight junction proteins claudin-1 and occludin.

**Cell Biology:** Replacing sucrose with trehalose as a cryoprotectant in the freezing medium will increase post-thaw viability of HeLa cells by at least 15 percentage points compared to the standard DMSO protocol.

**Climate:** Introducing Sporomusa ovata into a bioelectrochemical system at a cathode potential of −400mV vs SHE will fix CO₂ into acetate at a rate of at least 150 mmol/L/day, outperforming current biocatalytic carbon capture benchmarks by at least 20%.
                        """
                    )

                gr.Markdown("---")
                gr.Markdown("### 📊 Novelty Assessment")

                novelty_badge = gr.Markdown(
                    value="*Enter a hypothesis and click 'Check Literature' to begin.*",
                    elem_id="novelty_badge",
                )

                with gr.Accordion("📄 Detailed Assessment", open=False):
                    assessment_text = gr.Markdown()

                with gr.Accordion("📚 References", open=False):
                    references_text = gr.Markdown()

                # Wire events
                qc_btn.click(
                    fn=lambda h: run_literature_qc(h, state),
                    inputs=[hypothesis_input],
                    outputs=[novelty_badge, assessment_text, references_text],
                )
                clear_btn.click(
                    fn=lambda: ("", "", "", ""),
                    inputs=[],
                    outputs=[
                        hypothesis_input, novelty_badge,
                        assessment_text, references_text,
                    ],
                )

            # ══════════════════════════════════════════════════
            # TAB 2: Experiment Plan
            # ══════════════════════════════════════════════════
            with gr.Tab("🧪 Experiment Plan", id="plan_tab"):
                gr.Markdown("### Generate a Complete Experiment Plan")
                gr.Markdown(
                    "_Run Literature QC first, then generate the plan. "
                    "The plan includes: protocol, materials, budget, "
                    "timeline, and validation approach._"
                )

                with gr.Row():
                    plan_hypothesis = gr.Textbox(
                        label="Hypothesis (auto-filled from Tab 1)",
                        lines=3,
                        elem_id="plan_hypothesis",
                    )

                with gr.Row():
                    mode_select = gr.Radio(
                        choices=["single_shot", "modular"],
                        value="single_shot",
                        label="Generation Mode",
                        info=(
                            "Single-shot: One fast LLM call. "
                            "Modular: Separate calls per section (higher quality)."
                        ),
                    )

                generate_btn = gr.Button(
                    "🚀 Generate Experiment Plan",
                    variant="primary",
                    elem_id="generate_button",
                )

                plan_output = gr.Markdown(
                    value="*Click 'Generate Experiment Plan' to create your plan.*",
                    elem_id="plan_output",
                )

                # Wire events
                generate_btn.click(
                    fn=lambda h, m: generate_plan(h, m, state),
                    inputs=[plan_hypothesis, mode_select],
                    outputs=[plan_output],
                )

                # Auto-fill hypothesis from Tab 1
                qc_btn.click(
                    fn=lambda h: h,
                    inputs=[hypothesis_input],
                    outputs=[plan_hypothesis],
                )

            # ══════════════════════════════════════════════════
            # TAB 3: Scientist Review (Stretch Goal)
            # ══════════════════════════════════════════════════
            with gr.Tab("👨‍🔬 Scientist Review", id="review_tab"):
                gr.Markdown("### Rate and Correct the Generated Plan")
                gr.Markdown(
                    "_Your feedback improves future plans for similar "
                    "experiments. Every correction becomes a learning signal._"
                )

                review_hypothesis = gr.Textbox(
                    label="Hypothesis Being Reviewed",
                    lines=2,
                    elem_id="review_hypothesis",
                )

                experiment_type = gr.Dropdown(
                    choices=[
                        "diagnostics",
                        "gut_health",
                        "cell_biology",
                        "climate",
                        "chemistry",
                        "physics",
                        "neuroscience",
                        "genomics",
                        "other",
                    ],
                    value="other",
                    label="Experiment Type",
                    elem_id="experiment_type",
                )

                overall_rating = gr.Slider(
                    minimum=1, maximum=5, step=1, value=3,
                    label="Overall Plan Quality (1=Poor, 5=Excellent)",
                    elem_id="overall_rating",
                )

                gr.Markdown("---")
                gr.Markdown("#### Section-by-Section Review")

                # Protocol review
                with gr.Accordion("📋 Protocol Review", open=True):
                    protocol_rating = gr.Slider(
                        minimum=1, maximum=5, step=1, value=3,
                        label="Protocol Rating",
                    )
                    protocol_correction = gr.Textbox(
                        label="Corrections (leave blank if none)",
                        placeholder="e.g., Step 3 should use 37°C not 25°C...",
                        lines=3,
                    )

                # Materials review
                with gr.Accordion("🧫 Materials & Budget Review", open=False):
                    materials_rating = gr.Slider(
                        minimum=1, maximum=5, step=1, value=3,
                        label="Materials & Budget Rating",
                    )
                    materials_correction = gr.Textbox(
                        label="Corrections",
                        placeholder="e.g., Use Cat# T1503 from Sigma instead...",
                        lines=3,
                    )

                # Timeline review
                with gr.Accordion("📅 Timeline Review", open=False):
                    timeline_rating = gr.Slider(
                        minimum=1, maximum=5, step=1, value=3,
                        label="Timeline Rating",
                    )
                    timeline_correction = gr.Textbox(
                        label="Corrections",
                        placeholder="e.g., Cell culture phase needs 2 weeks not 1...",
                        lines=3,
                    )

                # Validation review
                with gr.Accordion("✅ Validation Review", open=False):
                    validation_rating = gr.Slider(
                        minimum=1, maximum=5, step=1, value=3,
                        label="Validation Rating",
                    )
                    validation_correction = gr.Textbox(
                        label="Corrections",
                        placeholder="e.g., Need n=10 per group minimum...",
                        lines=3,
                    )

                notes = gr.Textbox(
                    label="Additional Notes",
                    placeholder="Any general comments or suggestions...",
                    lines=3,
                )

                submit_feedback_btn = gr.Button(
                    "💾 Submit Feedback",
                    variant="primary",
                    elem_id="submit_feedback",
                )

                feedback_status = gr.Markdown()

                # Wire events
                submit_feedback_btn.click(
                    fn=lambda *args: save_feedback(*args, state=state),
                    inputs=[
                        review_hypothesis, experiment_type, overall_rating,
                        protocol_rating, protocol_correction,
                        materials_rating, materials_correction,
                        timeline_rating, timeline_correction,
                        validation_rating, validation_correction,
                        notes,
                    ],
                    outputs=[feedback_status],
                )

                # Auto-fill hypothesis from other tabs
                qc_btn.click(
                    fn=lambda h: h,
                    inputs=[hypothesis_input],
                    outputs=[review_hypothesis],
                )

            # ══════════════════════════════════════════════════
            # TAB 4: System Info
            # ══════════════════════════════════════════════════
            with gr.Tab("ℹ️ System Info", id="info_tab"):
                # LLM status
                llm_status = state.llm.status()
                status_lines = []
                for provider, available in llm_status.items():
                    icon = "✅" if available else "❌"
                    status_lines.append(f"- {icon} **{provider.title()}**")

                feedback_stats = state.feedback_store.get_stats()

                gr.Markdown(
                    f"""
### 🏗️ Architecture

```
User Input (Hypothesis)
       │
       ▼
┌─────────────────┐
│  Literature QC  │ ── ArXiv + Semantic Scholar
│  (Novelty Check)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Experiment Planner        │
│  ┌──────────┐ ┌───────────┐│
│  │ Protocol │ │ Materials ││
│  └──────────┘ └───────────┘│
│  ┌──────────┐ ┌───────────┐│
│  │ Timeline │ │Validation ││
│  └──────────┘ └───────────┘│
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────┐
│ Scientist Review│ ── Feedback Store
│ (Learning Loop) │
└─────────────────┘
```

### 🔌 LLM Providers
{chr(10).join(status_lines)}

Active provider: **{state.llm.provider_name}**

### 📊 Feedback Stats
- Total feedback items: **{feedback_stats['total_count']}**
- Average rating: **{feedback_stats['avg_rating']:.1f}/5**
- Experiment types: {json.dumps(feedback_stats.get('types', {}), indent=2) if feedback_stats.get('types') else 'None yet'}

### 🔗 Data Sources
- **ArXiv** — REST API (no key needed)
- **Semantic Scholar** — Graph API (no key needed)
- **protocols.io** — Referenced in generated protocols
- **Bio-protocol** — Referenced in generated protocols

### 🏆 Hack-Nation × World Bank Youth Summit
Global AI Hackathon 2026 — FULCRUM × Hack-Nation Challenge
                    """
                )

    return app
