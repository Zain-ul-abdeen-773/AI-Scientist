"""
Semantic Scholar Search Client — Query S2 for Scientific Papers
================================================================
Uses the Semantic Scholar Graph API (free, no key needed) to
find relevant papers. Provides citation counts and structured
metadata not available from arXiv.
"""

import time
from typing import List, Dict, Optional
from loguru import logger

import requests


class SemanticScholarClient:
    """
    Client for the Semantic Scholar Graph API.

    Searches papers by relevance and returns structured metadata
    including citation counts, year, and external IDs.
    """

    def __init__(self, config):
        """
        Initialize Semantic Scholar client.

        Args:
            config: LiteratureConfig with S2 base_url and fields
        """
        self.base_url = config.s2_base_url
        self.max_results = config.s2_max_results
        self.fields = ",".join(config.s2_fields)

    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
    ) -> List[Dict]:
        """
        Search Semantic Scholar for papers matching the query.

        Args:
            query: Natural language search query
            max_results: Override default max results

        Returns:
            List of paper dicts with keys:
                - title, abstract, year, citation_count, url,
                  authors, doi, source
        """
        n_results = max_results or self.max_results

        # Build API URL
        url = f"{self.base_url}/paper/search"
        params = {
            "query": query,
            "limit": n_results,
            "fields": self.fields,
        }

        try:
            logger.info(
                f"Semantic Scholar search: '{query[:80]}...' "
                f"(max {n_results})"
            )
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            papers = self._parse_response(data)
            logger.info(f"Semantic Scholar returned {len(papers)} papers")
            return papers

        except requests.exceptions.RequestException as e:
            logger.error(f"Semantic Scholar API error: {e}")
            return []

    def _parse_response(self, data: Dict) -> List[Dict]:
        """
        Parse S2 API JSON response into paper dicts.

        Args:
            data: Raw JSON response from S2 API

        Returns:
            List of parsed paper dictionaries
        """
        papers = []
        raw_papers = data.get("data", [])

        for raw in raw_papers:
            paper = self._parse_paper(raw)
            if paper:
                papers.append(paper)

        return papers

    def _parse_paper(self, raw: Dict) -> Optional[Dict]:
        """
        Parse a single paper from S2 response.

        Args:
            raw: Single paper dict from S2 API

        Returns:
            Structured paper dict or None
        """
        try:
            # Extract author names
            authors = []
            for author in raw.get("authors", []):
                name = author.get("name", "")
                if name:
                    authors.append(name)

            # Build URL (prefer DOI, fallback to S2 URL)
            external_ids = raw.get("externalIds", {}) or {}
            doi = external_ids.get("DOI", "")
            url = raw.get("url", "")
            if doi:
                url = f"https://doi.org/{doi}"

            # Get abstract (may be None)
            abstract = raw.get("abstract", "") or ""

            return {
                "title": raw.get("title", "Untitled"),
                "abstract": abstract[:500],
                "year": raw.get("year"),
                "citation_count": raw.get("citationCount", 0),
                "url": url,
                "authors": authors[:5],
                "doi": doi,
                "source": "semantic_scholar",
            }

        except Exception as e:
            logger.warning(f"Failed to parse S2 paper: {e}")
            return None

    def format_results(self, papers: List[Dict]) -> str:
        """
        Format paper results into a readable summary for LLM input.

        Args:
            papers: List of paper dicts from search()

        Returns:
            Formatted string summary of all papers
        """
        if not papers:
            return "No papers found on Semantic Scholar."

        lines = []
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper["authors"][:3])
            if len(paper["authors"]) > 3:
                authors_str += " et al."

            year_str = str(paper["year"]) if paper["year"] else "N/A"
            cite_str = str(paper["citation_count"]) if paper["citation_count"] else "0"

            lines.append(
                f"**[{i}]** {paper['title']}\n"
                f"   Authors: {authors_str}\n"
                f"   Year: {year_str} | Citations: {cite_str}\n"
                f"   URL: {paper['url']}\n"
                f"   Abstract: {paper['abstract'][:300]}...\n"
            )

        return "\n".join(lines)
