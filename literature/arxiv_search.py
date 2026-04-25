"""
ArXiv Search Client — Query arXiv for Scientific Papers
========================================================
Uses the arXiv REST API (no API key needed) to search for
papers related to a scientific hypothesis.

Rate-limited to 3 seconds between requests per arXiv policy.
"""

import time
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from loguru import logger

import requests


# ArXiv API XML namespace
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


class ArxivSearchClient:
    """
    Client for the arXiv REST API.

    Searches arXiv papers by keyword/query and returns
    structured results with title, abstract, authors, and URL.
    """

    def __init__(self, config):
        """
        Initialize ArXiv search client.

        Args:
            config: LiteratureConfig with base_url and max_results
        """
        self.base_url = config.arxiv_base_url
        self.max_results = config.arxiv_max_results
        self.delay = config.arxiv_delay_seconds
        self._last_request_time = 0.0

    def _rate_limit(self) -> None:
        """Enforce rate limiting between API calls."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            wait_time = self.delay - elapsed
            logger.debug(f"ArXiv rate limit: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
        self._last_request_time = time.time()

    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
    ) -> List[Dict]:
        """
        Search arXiv for papers matching the query.

        Args:
            query: Search query (natural language or arXiv query syntax)
            max_results: Override default max results

        Returns:
            List of paper dicts with keys:
                - title, abstract, authors, published, url, arxiv_id, source
        """
        self._rate_limit()

        n_results = max_results or self.max_results

        # Build query parameters
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": n_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            logger.info(f"ArXiv search: '{query[:80]}...' (max {n_results})")
            response = requests.get(
                self.base_url, params=params, timeout=15
            )
            response.raise_for_status()

            # Parse XML response
            papers = self._parse_response(response.text)
            logger.info(f"ArXiv returned {len(papers)} papers")
            return papers

        except requests.exceptions.RequestException as e:
            logger.error(f"ArXiv API error: {e}")
            return []

    def _parse_response(self, xml_text: str) -> List[Dict]:
        """
        Parse arXiv Atom XML response into paper dicts.

        Args:
            xml_text: Raw XML response from arXiv API

        Returns:
            List of parsed paper dictionaries
        """
        papers = []

        try:
            root = ET.fromstring(xml_text)

            for entry in root.findall("atom:entry", ARXIV_NS):
                paper = self._parse_entry(entry)
                if paper:
                    papers.append(paper)

        except ET.ParseError as e:
            logger.error(f"Failed to parse ArXiv XML: {e}")

        return papers

    def _parse_entry(self, entry) -> Optional[Dict]:
        """
        Parse a single arXiv entry element.

        Args:
            entry: XML element for one paper

        Returns:
            Paper dict or None if parsing fails
        """
        try:
            # Extract title (clean up whitespace)
            title_elem = entry.find("atom:title", ARXIV_NS)
            title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else ""

            # Extract abstract
            summary_elem = entry.find("atom:summary", ARXIV_NS)
            abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""

            # Extract authors
            authors = []
            for author in entry.findall("atom:author", ARXIV_NS):
                name_elem = author.find("atom:name", ARXIV_NS)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())

            # Extract URL and arXiv ID
            arxiv_id = ""
            url = ""
            for link in entry.findall("atom:link", ARXIV_NS):
                if link.get("type") == "text/html":
                    url = link.get("href", "")
                elif link.get("rel") == "alternate":
                    url = url or link.get("href", "")

            id_elem = entry.find("atom:id", ARXIV_NS)
            if id_elem is not None:
                arxiv_id = id_elem.text.strip().split("/")[-1]
                url = url or id_elem.text.strip()

            # Extract published date
            published_elem = entry.find("atom:published", ARXIV_NS)
            published = published_elem.text[:10] if published_elem is not None else ""

            return {
                "title": title,
                "abstract": abstract[:500],  # Truncate long abstracts
                "authors": authors[:5],       # Limit author list
                "published": published,
                "url": url,
                "arxiv_id": arxiv_id,
                "source": "arxiv",
            }

        except Exception as e:
            logger.warning(f"Failed to parse arXiv entry: {e}")
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
            return "No papers found on arXiv."

        lines = []
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper["authors"][:3])
            if len(paper["authors"]) > 3:
                authors_str += " et al."

            lines.append(
                f"**[{i}]** {paper['title']}\n"
                f"   Authors: {authors_str}\n"
                f"   Published: {paper['published']}\n"
                f"   URL: {paper['url']}\n"
                f"   Abstract: {paper['abstract'][:300]}...\n"
            )

        return "\n".join(lines)
