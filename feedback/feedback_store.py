"""
Feedback Store — Persist Scientist Corrections as Structured JSON
==================================================================
Saves, loads, and queries scientist corrections tagged by
experiment type and domain. Each correction captures the
section, original text, corrected text, and metadata.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger


class FeedbackStore:
    """
    File-based store for scientist feedback and corrections.

    Each feedback item is saved as a JSON file in the feedback
    directory, tagged by experiment type for retrieval.

    Structure of a feedback item:
        {
            "id": "uuid",
            "timestamp": "ISO datetime",
            "hypothesis": "original hypothesis",
            "experiment_type": "auto-detected or user-specified",
            "domain": "biology / chemistry / physics / etc.",
            "sections": {
                "protocol": {"rating": 1-5, "correction": "...", "original": "..."},
                "materials": {"rating": 1-5, "correction": "...", "original": "..."},
                ...
            },
            "overall_rating": 1-5,
            "notes": "free-text scientist notes"
        }
    """

    def __init__(self, config):
        """
        Initialize feedback store.

        Args:
            config: FeedbackConfig with feedback_dir path
        """
        self.feedback_dir = Path(config.feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"FeedbackStore initialized: {self.feedback_dir}")

    def save(self, feedback: Dict) -> str:
        """
        Save a feedback item to disk.

        Args:
            feedback: Feedback dict with hypothesis, sections, ratings

        Returns:
            Feedback ID (UUID string)
        """
        # Generate unique ID and timestamp
        feedback_id = str(uuid.uuid4())[:8]
        feedback["id"] = feedback_id
        feedback["timestamp"] = datetime.now().isoformat()

        # Save to file
        filepath = self.feedback_dir / f"feedback_{feedback_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(feedback, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Feedback saved: {feedback_id} "
            f"(type: {feedback.get('experiment_type', 'unknown')})"
        )
        return feedback_id

    def load_all(self) -> List[Dict]:
        """
        Load all feedback items from disk.

        Returns:
            List of feedback dicts, sorted by timestamp (newest first)
        """
        items = []

        for filepath in self.feedback_dir.glob("feedback_*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    item = json.load(f)
                    items.append(item)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load {filepath}: {e}")

        # Sort by timestamp (newest first)
        items.sort(
            key=lambda x: x.get("timestamp", ""),
            reverse=True,
        )

        logger.info(f"Loaded {len(items)} feedback items")
        return items

    def load_by_id(self, feedback_id: str) -> Optional[Dict]:
        """
        Load a specific feedback item by ID.

        Args:
            feedback_id: UUID string of the feedback

        Returns:
            Feedback dict or None if not found
        """
        filepath = self.feedback_dir / f"feedback_{feedback_id}.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def search_by_type(self, experiment_type: str) -> List[Dict]:
        """
        Find all feedback for a specific experiment type.

        Args:
            experiment_type: Type to filter by (e.g., "diagnostics")

        Returns:
            List of matching feedback items
        """
        all_items = self.load_all()
        return [
            item for item in all_items
            if item.get("experiment_type", "").lower() == experiment_type.lower()
        ]

    def search_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """
        Find feedback items that match any of the given keywords.

        Args:
            keywords: List of search terms

        Returns:
            List of matching feedback items with match scores
        """
        all_items = self.load_all()
        scored_items = []

        for item in all_items:
            # Search in hypothesis and notes
            text = (
                item.get("hypothesis", "") + " " +
                item.get("notes", "") + " " +
                item.get("experiment_type", "")
            ).lower()

            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                item["_match_score"] = score
                scored_items.append(item)

        # Sort by match score (highest first)
        scored_items.sort(key=lambda x: x["_match_score"], reverse=True)
        return scored_items

    def get_stats(self) -> Dict:
        """
        Get summary statistics of stored feedback.

        Returns:
            Dict with count, types, average ratings
        """
        items = self.load_all()

        if not items:
            return {"total_count": 0, "types": {}, "avg_rating": 0.0}

        types = {}
        ratings = []

        for item in items:
            exp_type = item.get("experiment_type", "unknown")
            types[exp_type] = types.get(exp_type, 0) + 1

            rating = item.get("overall_rating", 0)
            if rating > 0:
                ratings.append(rating)

        return {
            "total_count": len(items),
            "types": types,
            "avg_rating": sum(ratings) / len(ratings) if ratings else 0.0,
        }
