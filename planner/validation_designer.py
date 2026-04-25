"""
Validation Designer — Success Criteria and Statistical Plan
=============================================================
Defines how experiment success or failure will be measured,
including endpoints, controls, statistical tests, sample
sizes, and confounders.
"""

from typing import Optional
from loguru import logger

from llm.prompts import VALIDATION_PROMPT, SYSTEM_PROMPT


class ValidationDesigner:
    """
    Designs validation approaches for experiments.

    Produces:
        - Primary endpoints with quantitative thresholds
        - Statistical analysis plan
        - Positive and negative controls
        - Sample size justification
        - Confounder mitigation strategies
    """

    def __init__(self, llm_client):
        """
        Initialize validation designer.

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
        Generate a validation approach.

        Args:
            hypothesis: The scientific hypothesis
            protocol_summary: Summary of the protocol for context

        Returns:
            Formatted markdown validation plan
        """
        logger.info("Generating validation approach...")

        prompt = VALIDATION_PROMPT.format(
            hypothesis=hypothesis,
            protocol_summary=protocol_summary or "Not yet generated.",
        )

        result = self.llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,
        )

        logger.info("Validation design complete")
        return result
