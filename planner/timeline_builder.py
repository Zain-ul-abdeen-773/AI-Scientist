"""
Timeline Builder — Phased Project Timeline with Dependencies
==============================================================
Generates a structured timeline with phases, milestones,
dependencies, and duration estimates for the experiment.
"""

from typing import Optional
from loguru import logger

from llm.prompts import TIMELINE_PROMPT, SYSTEM_PROMPT


class TimelineBuilder:
    """
    Generates phased project timelines.

    Produces:
        - Phases: Preparation → Execution → Analysis → Reporting
        - Sub-tasks with durations
        - Dependencies between tasks
        - Milestones and go/no-go decision points
        - Total project duration
    """

    def __init__(self, llm_client):
        """
        Initialize timeline builder.

        Args:
            llm_client: LLMClient instance for text generation
        """
        self.llm = llm_client

    def generate(
        self,
        hypothesis: str,
        protocol_summary: str = "",
    ) -> str:
        """
        Generate a phased project timeline.

        Args:
            hypothesis: The scientific hypothesis
            protocol_summary: Summary of the protocol for context

        Returns:
            Formatted markdown timeline with phases and dependencies
        """
        logger.info("Generating project timeline...")

        prompt = TIMELINE_PROMPT.format(
            hypothesis=hypothesis,
            protocol_summary=protocol_summary or "Not yet generated.",
        )

        result = self.llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,
        )

        logger.info("Timeline generation complete")
        return result
