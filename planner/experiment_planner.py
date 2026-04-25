"""
Experiment Planner — Main Orchestrator for Plan Generation
============================================================
Coordinates all sub-modules (protocol, materials, timeline,
validation) to produce a complete experiment plan. Optionally
integrates scientist feedback from the feedback store.

This is the central brain of the planning pipeline.
"""

from typing import Dict, Optional
from loguru import logger

from llm.llm_client import LLMClient
from llm.prompts import FULL_PLAN_PROMPT, SYSTEM_PROMPT, FEEDBACK_CONTEXT_TEMPLATE
from planner.protocol_generator import ProtocolGenerator
from planner.materials_budget import MaterialsBudgetGenerator
from planner.timeline_builder import TimelineBuilder
from planner.validation_designer import ValidationDesigner


class ExperimentPlanner:
    """
    Main orchestrator that builds complete experiment plans.

    Supports two generation modes:
        1. Single-shot: One LLM call for the entire plan (faster)
        2. Modular: Separate LLM calls per section (higher quality)

    Integrates prior scientist feedback when available.
    """

    def __init__(self, llm_client: LLMClient, feedback_learner=None):
        """
        Initialize the experiment planner.

        Args:
            llm_client: LLMClient for LLM generation
            feedback_learner: Optional FeedbackLearner for past corrections
        """
        self.llm = llm_client
        self.feedback_learner = feedback_learner

        # Sub-module generators
        self.protocol_gen = ProtocolGenerator(llm_client)
        self.materials_gen = MaterialsBudgetGenerator(llm_client)
        self.timeline_gen = TimelineBuilder(llm_client)
        self.validation_gen = ValidationDesigner(llm_client)

        logger.info("ExperimentPlanner initialized")

    def generate_full_plan(
        self,
        hypothesis: str,
        literature_context: str = "",
        mode: str = "single_shot",
    ) -> Dict[str, str]:
        """
        Generate a complete experiment plan.

        Args:
            hypothesis: The scientific hypothesis
            literature_context: Formatted literature QC results
            mode: "single_shot" (one call) or "modular" (per section)

        Returns:
            Dict with keys:
                - full_plan: Complete formatted plan
                - protocol: Protocol section
                - materials_budget: Materials & budget section
                - timeline: Timeline section
                - validation: Validation section
                - mode: Generation mode used
        """
        logger.info(f"Generating experiment plan (mode: {mode})")

        # Get feedback context if available
        feedback_context = self._get_feedback_context(hypothesis)

        if mode == "modular":
            return self._generate_modular(
                hypothesis, literature_context, feedback_context
            )
        else:
            return self._generate_single_shot(
                hypothesis, literature_context, feedback_context
            )

    def _generate_single_shot(
        self,
        hypothesis: str,
        literature_context: str,
        feedback_context: str,
    ) -> Dict[str, str]:
        """
        Generate entire plan in one LLM call.
        Faster but may have lower per-section quality.

        Args:
            hypothesis: Scientific hypothesis
            literature_context: Literature QC results
            feedback_context: Past scientist feedback

        Returns:
            Dict with full plan and empty individual sections
        """
        prompt = FULL_PLAN_PROMPT.format(
            hypothesis=hypothesis,
            literature_context=literature_context or "No literature search performed.",
            feedback_context=feedback_context,
        )

        full_plan = self.llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=4096,
        )

        logger.info("Single-shot plan generation complete")

        return {
            "full_plan": full_plan,
            "protocol": "",
            "materials_budget": "",
            "timeline": "",
            "validation": "",
            "mode": "single_shot",
        }

    def _generate_modular(
        self,
        hypothesis: str,
        literature_context: str,
        feedback_context: str,
    ) -> Dict[str, str]:
        """
        Generate plan section-by-section for higher quality.
        Each section gets its own focused LLM call.

        Args:
            hypothesis: Scientific hypothesis
            literature_context: Literature QC results
            feedback_context: Past scientist feedback

        Returns:
            Dict with individual sections and assembled full plan
        """
        # Step 1: Generate protocol first (others depend on it)
        protocol = self.protocol_gen.generate(hypothesis)
        protocol_summary = self.protocol_gen.summarize(protocol)

        # Step 2: Generate remaining sections with protocol context
        materials_budget = self.materials_gen.generate(
            hypothesis, protocol_summary
        )
        timeline = self.timeline_gen.generate(
            hypothesis, protocol_summary
        )
        validation = self.validation_gen.generate(
            hypothesis, protocol_summary
        )

        # Assemble full plan
        full_plan = self._assemble_plan(
            hypothesis=hypothesis,
            literature_context=literature_context,
            protocol=protocol,
            materials_budget=materials_budget,
            timeline=timeline,
            validation=validation,
        )

        logger.info("Modular plan generation complete (4 sections)")

        return {
            "full_plan": full_plan,
            "protocol": protocol,
            "materials_budget": materials_budget,
            "timeline": timeline,
            "validation": validation,
            "mode": "modular",
        }

    def _assemble_plan(
        self,
        hypothesis: str,
        literature_context: str,
        protocol: str,
        materials_budget: str,
        timeline: str,
        validation: str,
    ) -> str:
        """
        Assemble individual sections into a complete plan document.

        Args:
            All plan sections as strings

        Returns:
            Complete formatted markdown plan
        """
        sections = [
            f"# 🔬 Experiment Plan\n",
            f"## Hypothesis\n{hypothesis}\n",
            f"---\n",
            f"## 1. Protocol\n{protocol}\n",
            f"---\n",
            f"## 2. Materials & Budget\n{materials_budget}\n",
            f"---\n",
            f"## 3. Timeline\n{timeline}\n",
            f"---\n",
            f"## 4. Validation Approach\n{validation}\n",
        ]

        if literature_context:
            sections.insert(2, f"## Literature Context\n{literature_context}\n")

        return "\n".join(sections)

    def _get_feedback_context(self, hypothesis: str) -> str:
        """
        Retrieve relevant past feedback to inject as few-shot context.

        Args:
            hypothesis: Current hypothesis for similarity matching

        Returns:
            Formatted feedback context string (empty if none found)
        """
        if self.feedback_learner is None:
            return ""

        try:
            feedback_items = self.feedback_learner.get_relevant_feedback(
                hypothesis
            )

            if not feedback_items:
                return ""

            # Format feedback for injection
            items_text = ""
            for i, item in enumerate(feedback_items, 1):
                items_text += (
                    f"\n**Correction {i}** "
                    f"(from: {item.get('experiment_type', 'N/A')}):\n"
                    f"- Section: {item.get('section', 'N/A')}\n"
                    f"- Original: {item.get('original', 'N/A')}\n"
                    f"- Correction: {item.get('correction', 'N/A')}\n"
                )

            return FEEDBACK_CONTEXT_TEMPLATE.format(
                feedback_items=items_text
            )

        except Exception as e:
            logger.warning(f"Failed to retrieve feedback: {e}")
            return ""
