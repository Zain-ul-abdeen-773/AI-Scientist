"""
Protocol Generator — Step-by-Step Experimental Methodology
============================================================
Generates detailed, operationally-grounded protocols using
LLM with structured prompt engineering. References real
protocol repositories (protocols.io, Bio-protocol, etc.).
"""

from typing import Optional
from loguru import logger

from llm.prompts import PROTOCOL_PROMPT, SYSTEM_PROMPT


class ProtocolGenerator:
    """
    Generates step-by-step experimental protocols.

    Each protocol includes:
        - Numbered steps with specific parameters
        - Equipment requirements per step
        - Critical notes and common pitfalls
        - References to published protocols
        - Safety precautions
    """

    def __init__(self, llm_client):
        """
        Initialize protocol generator.

        Args:
            llm_client: LLMClient instance for text generation
        """
        self.llm = llm_client

    def generate(self, hypothesis: str) -> str:
        """
        Generate a detailed experimental protocol.

        Args:
            hypothesis: The scientific hypothesis to design a protocol for

        Returns:
            Formatted markdown string with the complete protocol
        """
        logger.info("Generating experimental protocol...")

        prompt = PROTOCOL_PROMPT.format(hypothesis=hypothesis)

        protocol = self.llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,  # Low temp for factual output
        )

        logger.info("Protocol generation complete")
        return protocol

    def summarize(self, protocol: str) -> str:
        """
        Create a brief summary of the protocol for use by other modules.

        Args:
            protocol: Full protocol text

        Returns:
            Condensed summary (key steps only)
        """
        # Extract first 500 chars as summary for downstream use
        # This avoids hitting token limits in subsequent prompts
        lines = protocol.strip().split("\n")
        summary_lines = []
        char_count = 0

        for line in lines:
            if char_count + len(line) > 800:
                break
            summary_lines.append(line)
            char_count += len(line)

        return "\n".join(summary_lines)
