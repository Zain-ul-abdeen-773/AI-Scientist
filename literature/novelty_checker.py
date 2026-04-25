"""
Novelty Checker — Assess Hypothesis Novelty Against Literature
===============================================================
Orchestrates ArXiv and Semantic Scholar searches, then uses LLM
to compare the hypothesis against found papers and produce a
novelty signal: "not found", "similar work exists", or "exact match found".
"""

from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

from literature.arxiv_search import ArxivSearchClient
from literature.semantic_scholar import SemanticScholarClient
from llm.prompts import NOVELTY_ASSESSMENT_PROMPT


class NoveltyChecker:
    """
    Checks whether a scientific hypothesis has been done before.

    Combines results from ArXiv and Semantic Scholar, deduplicates,
    and uses an LLM to assess novelty. Works without an LLM by
    falling back to a simple keyword-overlap heuristic.

    Improvement: searches ArXiv and S2 in parallel via ThreadPoolExecutor.
    """

    def __init__(self, literature_config, llm_client=None):
        """
        Initialize novelty checker.

        Args:
            literature_config: LiteratureConfig with search settings
            llm_client: Optional LLMClient for LLM-based assessment
        """
        self.arxiv = ArxivSearchClient(literature_config)
        self.s2 = SemanticScholarClient(literature_config)
        self.llm = llm_client
        self.config = literature_config

    def check(self, hypothesis: str) -> Dict:
        """
        Run full novelty check on a hypothesis.

        Steps:
            1. Search ArXiv and Semantic Scholar IN PARALLEL
            2. Deduplicate results by title similarity
            3. Use LLM (or heuristic) to assess novelty
            4. Return signal + references

        Args:
            hypothesis: The scientific hypothesis to check

        Returns:
            Dict with keys:
                - signal: "not found" | "similar work exists" | "exact match found"
                - justification: Explanation of the assessment
                - references: List of 1-3 relevant paper dicts
                - all_papers: All papers found
                - papers_summary: Formatted summary for display
        """
        logger.info(f"Checking novelty: '{hypothesis[:80]}...'")

        # ── Step 1: Search both sources in parallel ──────────
        search_query = self._build_search_query(hypothesis)

        arxiv_papers = []
        s2_papers = []

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_arxiv = executor.submit(self.arxiv.search, search_query)
            future_s2 = executor.submit(self.s2.search, search_query)

            try:
                arxiv_papers = future_arxiv.result(timeout=20)
            except Exception as e:
                logger.warning(f"ArXiv search failed: {e}")

            try:
                s2_papers = future_s2.result(timeout=20)
            except Exception as e:
                logger.warning(f"Semantic Scholar search failed: {e}")

        # ── Step 2: Combine and deduplicate ──────────────────
        all_papers = self._deduplicate(arxiv_papers + s2_papers)
        logger.info(
            f"Found {len(all_papers)} unique papers "
            f"(ArXiv: {len(arxiv_papers)}, S2: {len(s2_papers)})"
        )

        # ── Step 3: Format papers summary ────────────────────
        papers_summary = self._format_combined(all_papers)

        # ── Step 4: Assess novelty ───────────────────────────
        if self.llm and self.llm.is_available and all_papers:
            result = self._llm_assessment(hypothesis, papers_summary)
        else:
            result = self._heuristic_assessment(hypothesis, all_papers)

        # Attach paper data
        result["all_papers"] = all_papers
        result["papers_summary"] = papers_summary
        result["references"] = all_papers[:3]  # Top 3 most relevant

        logger.info(f"Novelty signal: {result['signal']}")
        return result

    def _build_search_query(self, hypothesis: str) -> str:
        """
        Extract key terms from hypothesis for search.

        Simple approach: remove common words and use the
        most informative terms.

        Args:
            hypothesis: Full hypothesis text

        Returns:
            Cleaned search query string
        """
        # Common words to filter out
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "will",
            "would", "could", "should", "can", "may", "might",
            "be", "been", "being", "have", "has", "had", "do",
            "does", "did", "and", "or", "but", "if", "then",
            "that", "this", "these", "those", "it", "its",
            "by", "for", "with", "from", "to", "in", "on",
            "at", "of", "as", "than", "more", "most", "less",
            "very", "just", "only", "not", "no", "we", "our",
            "whether", "due", "compared", "measured",
        }

        words = hypothesis.lower().split()
        key_terms = [w for w in words if w not in stopwords and len(w) > 2]

        # Limit to first 15 key terms to keep search focused
        return " ".join(key_terms[:15])

    def _deduplicate(self, papers: List[Dict]) -> List[Dict]:
        """
        Remove duplicate papers by title similarity.

        Args:
            papers: Combined list from multiple sources

        Returns:
            Deduplicated list
        """
        seen_titles = set()
        unique = []

        for paper in papers:
            # Normalize title for comparison
            normalized = paper["title"].lower().strip()
            # Simple dedup: check if title is too similar to any seen
            if normalized not in seen_titles:
                seen_titles.add(normalized)
                unique.append(paper)

        return unique

    def _format_combined(self, papers: List[Dict]) -> str:
        """
        Format all papers into a single summary string.

        Args:
            papers: List of paper dicts

        Returns:
            Formatted markdown string
        """
        if not papers:
            return "No papers found in literature search."

        lines = []
        for i, paper in enumerate(papers[:10], 1):  # Limit to 10 for LLM
            authors = ", ".join(paper.get("authors", [])[:3])
            year = paper.get("year") or paper.get("published", "N/A")
            abstract = paper.get("abstract", "")[:250]

            lines.append(
                f"**Paper {i}:** {paper['title']}\n"
                f"  Authors: {authors}\n"
                f"  Year: {year}\n"
                f"  Abstract: {abstract}...\n"
            )

        return "\n".join(lines)

    def _llm_assessment(
        self, hypothesis: str, papers_summary: str
    ) -> Dict:
        """
        Use LLM to assess novelty by comparing hypothesis vs. papers.

        Args:
            hypothesis: The scientific hypothesis
            papers_summary: Formatted summary of found papers

        Returns:
            Dict with signal, justification, assessment_text
        """
        prompt = NOVELTY_ASSESSMENT_PROMPT.format(
            hypothesis=hypothesis,
            papers_summary=papers_summary,
        )

        from llm.prompts import SYSTEM_PROMPT
        response = self.llm.generate(prompt, system_prompt=SYSTEM_PROMPT)

        # Parse the LLM response for the novelty signal
        signal = self._extract_signal(response)

        return {
            "signal": signal,
            "justification": response,
            "assessment_text": response,
        }

    def _heuristic_assessment(
        self, hypothesis: str, papers: List[Dict]
    ) -> Dict:
        """
        Simple heuristic novelty check (when no LLM available).

        Uses keyword overlap between hypothesis and paper titles/abstracts
        to estimate similarity.

        Args:
            hypothesis: The scientific hypothesis
            papers: List of paper dicts

        Returns:
            Dict with signal, justification
        """
        if not papers:
            return {
                "signal": "not found",
                "justification": (
                    "No related papers were found in ArXiv or "
                    "Semantic Scholar databases."
                ),
                "assessment_text": "**Novelty Signal: not found**\n\n"
                    "No matching papers were found in the literature search.",
            }

        # Compute keyword overlap scores
        hyp_words = set(hypothesis.lower().split())
        scores = []

        for paper in papers:
            paper_text = (
                paper.get("title", "") + " " + paper.get("abstract", "")
            ).lower()
            paper_words = set(paper_text.split())
            overlap = len(hyp_words & paper_words) / max(len(hyp_words), 1)
            scores.append(overlap)

        max_score = max(scores) if scores else 0.0

        # Determine signal based on overlap
        if max_score > self.config.similarity_threshold_exact:
            signal = "exact match found"
        elif max_score > self.config.similarity_threshold_similar:
            signal = "similar work exists"
        else:
            signal = "not found"

        justification = (
            f"Keyword overlap analysis found maximum similarity of "
            f"{max_score:.1%} with existing papers. "
            f"Based on threshold analysis, the novelty signal is: {signal}."
        )

        return {
            "signal": signal,
            "justification": justification,
            "assessment_text": (
                f"### Novelty Signal\n{signal}\n\n"
                f"### Justification\n{justification}"
            ),
        }

    def _extract_signal(self, llm_response: str) -> str:
        """
        Extract the novelty signal from LLM response text.

        Args:
            llm_response: Full LLM response text

        Returns:
            One of: "not found", "similar work exists", "exact match found"
        """
        response_lower = llm_response.lower()

        if "exact match found" in response_lower:
            return "exact match found"
        elif "similar work exists" in response_lower:
            return "similar work exists"
        elif "not found" in response_lower:
            return "not found"
        else:
            # Default to "similar work exists" if signal is ambiguous
            return "similar work exists"
