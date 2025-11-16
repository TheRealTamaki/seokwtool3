"""Google PAA Scraper using Firecrawl API"""

import os
import re
from typing import List, Dict, Any
from firecrawl import Firecrawl
from bs4 import BeautifulSoup


class GooglePAAScraper:
    """Scrapes People Also Ask (PAA) questions from Google search results"""

    def __init__(self, api_key: str = None):
        """Initialize the scraper with Firecrawl API key"""
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Firecrawl API key not provided. "
                "Set FIRECRAWL_API_KEY environment variable or pass api_key parameter."
            )
        self.app = Firecrawl(api_key=self.api_key)

    def scrape_paa(self, query: str, depth: int = 1) -> Dict[str, Any]:
        """
        Scrape People Also Ask section from Google search results

        Args:
            query: Search query
            depth: How many levels of PAA to scrape (1-3, default 1)
        """
        try:
            depth = max(1, min(3, int(depth)))  # Clamp between 1-3
            search_url = f"https://www.google.com/search?q={query}"
            print(f"Scraping Google search results for: {query}")
            print(f"URL: {search_url}")

            result = self.app.scrape(search_url)
            paa_data = self._extract_paa_from_content(result, depth=depth)

            return {
                "query": query,
                "paa_questions": paa_data,
                "success": True,
                "message": f"Successfully scraped {len(paa_data)} PAA questions",
            }
        except Exception as e:
            return {
                "query": query,
                "paa_questions": [],
                "success": False,
                "error": str(e),
            }

    def _extract_paa_from_content(self, scraped_content: Any, depth: int = 1) -> List[Dict[str, str]]:
        """Extract PAA questions from scraped content"""
        paa_questions = []

        if hasattr(scraped_content, '__dict__'):
            content_dict = scraped_content.__dict__
        else:
            content_dict = scraped_content

        markdown = content_dict.get("markdown") or getattr(scraped_content, "markdown", None)
        if markdown:
            paa_questions = self._extract_from_markdown(markdown, depth=depth)

        if not paa_questions:
            html = content_dict.get("html") or getattr(scraped_content, "html", None)
            if html:
                paa_questions = self._extract_from_html(html, depth=depth)

        return paa_questions

    def _extract_from_markdown(self, markdown_content: str, depth: int = 1) -> List[Dict[str, str]]:
        """Extract only PAA questions from markdown, filtering out noise"""
        paa_questions = []

        if "People also ask" not in markdown_content:
            return paa_questions

        # Split and find the PAA section
        parts = markdown_content.split("People also ask")
        if len(parts) < 2:
            return paa_questions

        paa_section = parts[1]

        # Find where the next major section starts
        next_section_match = re.search(r"\n#+\s", paa_section)
        if next_section_match:
            paa_section = paa_section[:next_section_match.start()]

        lines = paa_section.split("\n")

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip lines that are clearly not questions
            # Skip URLs, bold text, lists of multiple items
            if line.startswith("[") and line.endswith("]"):  # Links
                continue
            if line.startswith("http"):  # URLs
                continue
            if " | " in line:  # Separator lines
                continue
            if line.startswith("#"):  # Headers
                continue

            # Check if it looks like a question
            # PAA questions are typically:
            # - Short lines (under 200 chars)
            # - Contain a question mark OR
            # - Start with question words
            looks_like_question = (
                ("?" in line) or
                re.match(r"^(what|how|why|when|where|which|who|can|does|do|is|are|will|would|could|should|has|have)\s", line, re.IGNORECASE)
            )

            if looks_like_question and len(line) < 200 and len(line) > 5:
                # Remove leading numbers, bullets, and bold markers
                clean_question = re.sub(r"^[\*\-\•\d+\.\s]+", "", line)
                clean_question = clean_question.replace("**", "").strip()

                # Only add if we haven't seen it before (avoid duplicates)
                if clean_question and not any(q["question"] == clean_question for q in paa_questions):
                    paa_questions.append({"question": clean_question})

                    # Stop if we've reached the depth limit
                    if len(paa_questions) >= depth * 4:
                        break

        return paa_questions[:depth * 4]  # Limit by depth

    def _extract_from_html(self, html_content: str, depth: int = 1) -> List[Dict[str, str]]:
        """Extract PAA questions from HTML content"""
        paa_questions = []

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Look for PAA container
            question_selectors = [
                "div[data-sokoban-container] span",
                'g-scrolling-carousel div[role="option"]',
                "div.related-question-pair span",
            ]

            for selector in question_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        for element in elements:
                            text = element.get_text(strip=True)
                            # Filter for actual questions
                            if (text and len(text) > 5 and len(text) < 200 and
                                ("?" in text or re.match(r"^(what|how|why|when|where|which|who|can|does)", text, re.IGNORECASE))):
                                if not any(q["question"] == text for q in paa_questions):
                                    paa_questions.append({"question": text})

                                    if len(paa_questions) >= depth * 4:
                                        return paa_questions[:depth * 4]
                except:
                    continue

            if not paa_questions:
                paa_questions = self._extract_paa_generic(soup, depth=depth)

        except Exception as e:
            print(f"Error parsing HTML: {e}")

        return paa_questions[:depth * 4]

    def _extract_paa_generic(self, soup: BeautifulSoup, depth: int = 1) -> List[Dict[str, str]]:
        """Generic extraction of PAA questions"""
        paa_questions = []

        for element in soup.find_all(string=re.compile("People also ask", re.IGNORECASE)):
            parent = element.parent
            while parent and len(paa_questions) < depth * 4:
                for sibling in parent.find_next_siblings():
                    text = sibling.get_text(strip=True)
                    if (text and "?" in text and len(text) > 5 and len(text) < 200 and
                        not text.startswith("http") and not text.startswith("[")):
                        if not any(q["question"] == text for q in paa_questions):
                            paa_questions.append({"question": text})

                            if len(paa_questions) >= depth * 4:
                                return paa_questions[:depth * 4]
                parent = parent.parent

        return paa_questions[:depth * 4]
