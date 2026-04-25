"""
Materials & Budget Generator — Reagents, Supplies, and Cost Estimates
=====================================================================
Generates a comprehensive materials list with real catalog numbers
from major suppliers (Thermo Fisher, Sigma-Aldrich, etc.) and a
realistic budget breakdown.
"""

from typing import Optional
from loguru import logger

from llm.prompts import MATERIALS_BUDGET_PROMPT, SYSTEM_PROMPT


class MaterialsBudgetGenerator:
    """
    Generates materials lists and budget estimates.

    Produces:
        - Materials table with catalog numbers and suppliers
        - Budget breakdown by category
        - Grand total with realistic pricing
    """

    def __init__(self, llm_client):
        """
        Initialize materials & budget generator.

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
        Generate materials list and budget breakdown.

        Args:
            hypothesis: The scientific hypothesis
            protocol_summary: Summary of the protocol for context

        Returns:
            Formatted markdown with materials table and budget
        """
        logger.info("Generating materials list and budget...")

        prompt = MATERIALS_BUDGET_PROMPT.format(
            hypothesis=hypothesis,
            protocol_summary=protocol_summary or "Not yet generated.",
        )

        result = self.llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,
        )

        logger.info("Materials & budget generation complete")
        return result
