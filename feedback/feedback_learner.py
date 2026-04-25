"""
Feedback Learner — Retrieve and Apply Past Scientist Corrections
=================================================================
Finds relevant past corrections using keyword matching and
formats them as few-shot examples for LLM prompt injection.

This closes the learning loop: every scientist review makes
the next plan for a similar experiment type visibly better.
"""

from typing import List, Dict, Optional
from loguru import logger

from feedback.feedback_store import FeedbackStore


class FeedbackLearner:
    """
    Retrieves relevant past feedback and formats it for LLM injection.

    When generating a new plan, this module searches stored feedback
    for similar experiment types and extracts corrections to inject
    as few-shot examples, improving plan quality over time.
    """

    def __init__(self, feedback_store: FeedbackStore, config):
        """
        Initialize feedback learner.

        Args:
            feedback_store: FeedbackStore instance
            config: FeedbackConfig with retrieval settings
        """
        self.store = feedback_store
        self.max_examples = config.max_few_shot_examples
        self.min_score = config.min_similarity_score

    def get_relevant_feedback(
        self, hypothesis: str
    ) -> List[Dict]:
        """
        Find past corrections relevant to the current hypothesis.

        Uses keyword overlap to find similar experiments, then
        extracts structured corrections from those feedback items.

        Args:
            hypothesis: Current hypothesis being planned

        Returns:
            List of correction dicts with:
                - experiment_type, section, original, correction
        """
        # Extract keywords from hypothesis
        keywords = self._extract_keywords(hypothesis)

        if not keywords:
            return []

        # Search feedback store
        matches = self.store.search_by_keywords(keywords)

        if not matches:
            logger.debug("No relevant past feedback found")
            return []

        # Extract corrections from matched feedback items
        corrections = []
        for item in matches[: self.max_examples]:
            item_corrections = self._extract_corrections(item)
            corrections.extend(item_corrections)

        logger.info(
            f"Found {len(corrections)} relevant corrections "
            f"from {len(matches)} past reviews"
        )
        return corrections[: self.max_examples]

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from text.

        Args:
            text: Input text to extract keywords from

        Returns:
            List of keyword strings
        """
        # Simple keyword extraction: remove stopwords
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "will",
            "would", "could", "can", "may", "and", "or", "but",
            "if", "then", "that", "this", "it", "its", "by", "for",
            "with", "from", "to", "in", "on", "at", "of", "as",
            "be", "been", "being", "have", "has", "had", "do",
            "does", "did", "not", "no", "we", "our", "than",
        }

        words = text.lower().split()
        keywords = [
            w.strip(".,;:!?()[]{}\"'")
            for w in words
            if w not in stopwords and len(w) > 2
        ]

        return keywords

    def _extract_corrections(self, feedback_item: Dict) -> List[Dict]:
        """
        Extract structured corrections from a feedback item.

        Args:
            feedback_item: Full feedback dict from store

        Returns:
            List of correction dicts
        """
        corrections = []
        sections = feedback_item.get("sections", {})

        for section_name, section_data in sections.items():
            # Only include sections that have actual corrections
            correction_text = section_data.get("correction", "").strip()
            if correction_text:
                corrections.append({
                    "experiment_type": feedback_item.get(
                        "experiment_type", "unknown"
                    ),
                    "section": section_name,
                    "original": section_data.get("original", "")[:200],
                    "correction": correction_text[:300],
                    "rating": section_data.get("rating", 0),
                })

        return corrections

    def get_improvement_summary(self) -> Dict:
        """
        Summarize how feedback has been used across plans.

        Returns:
            Dict with usage statistics
        """
        stats = self.store.get_stats()
        return {
            "total_feedback_items": stats["total_count"],
            "experiment_types_covered": len(stats["types"]),
            "types_breakdown": stats["types"],
            "average_rating": stats["avg_rating"],
        }
