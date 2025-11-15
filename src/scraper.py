"""Google PAA Scraper using Firecrawl API"""

import os
import re
from typing import List, Dict, Any
from firecrawl import FirecrawlApp
from bs4 import BeautifulSoup


class GooglePAAScraper:
    """Scrapes People Also Ask (PAA) questions from Google search results"""

    def __init__(self, api_key: str = None):
        """
        Initialize the scraper with Firecrawl API key

        Args:
            api_key: Firecrawl API key (defaults to FIRECRAWL_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Firecrawl API key not provided. "
                "Set FIRECRAWL_API_KEY environment variable or pass api_key parameter."
            )
        self.app = FirecrawlApp(api_key=self.api_key)

    def scrape_paa(self, query: str) -> Dict[str, Any]:
        """
        Scrape People Also Ask section from Google search results for a given query

        Args:
            query: Search query to look up on Google

        Returns:
            Dictionary containing:
            - query: The original search query
            - paa_questions: List of PAA questions and their details
            - raw_html: Raw HTML content from the page (optional)
            - success: Whether scraping was successful
        """
        try:
            # Build Google search URL
            search_url = f"https://www.google.com/search?q={query}"

            print(f"Scraping Google search results for: {query}")
            print(f"URL: {search_url}")

            # Use Firecrawl to scrape the page
            result = self.app.scrape_url(search_url)

            # Extract PAA questions from the scraped content
            paa_data = self._extract_paa_from_content(result)

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

    def _extract_paa_from_content(self, scraped_content: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract People Also Ask questions from scraped content

        Args:
            scraped_content: Content returned from Firecrawl scrape_url

        Returns:
            List of PAA questions with their text
        """
        paa_questions = []

        # Try to extract from markdown first (easier to parse)
        if "markdown" in scraped_content:
            paa_questions = self._extract_from_markdown(scraped_content["markdown"])

        # If markdown extraction didn't work, try HTML
        if not paa_questions and "html" in scraped_content:
            paa_questions = self._extract_from_html(scraped_content["html"])

        return paa_questions

    def _extract_from_markdown(self, markdown_content: str) -> List[Dict[str, str]]:
        """
        Extract PAA questions from markdown content using pattern matching

        Args:
            markdown_content: Markdown text from Firecrawl

        Returns:
            List of PAA questions
        """
        paa_questions = []

        # Look for "People also ask" section
        if "People also ask" not in markdown_content:
            return paa_questions

        # Find the section after "People also ask"
        paa_section = markdown_content.split("People also ask")[1] if "People also ask" in markdown_content else ""

        # Extract questions - they typically appear as list items or numbered items
        # Look for various patterns of question formatting
        patterns = [
            r"^[\*\-\•]\s+(.+?)$",  # Bullet points
            r"^\d+\.\s+(.+?)$",  # Numbered
            r"^#{1,6}\s+(.+?)$",  # Headers
        ]

        lines = paa_section.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Stop if we hit another major section
            if re.match(r"^#+\s", line) and "People also ask" not in line:
                break

            # Try to match question patterns
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    question = match.group(1).strip()
                    # Filter out noise - questions usually have "?" or are reasonable length
                    if len(question) > 5 and len(question) < 500:
                        paa_questions.append({"question": question})
                    break

        return paa_questions

    def _extract_from_html(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extract PAA questions from HTML content

        Args:
            html_content: HTML text from Firecrawl

        Returns:
            List of PAA questions
        """
        paa_questions = []

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Look for elements that typically contain PAA questions
            # Google uses various div structures - look for common patterns
            question_selectors = [
                "div[data-sokoban-container] span",  # Google's PAA container
                'g-scrolling-carousel div[role="option"]',  # Carousel items
                "div.related-question-pair span",  # Related questions
            ]

            for selector in question_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        for element in elements:
                            text = element.get_text(strip=True)
                            if text and len(text) > 5 and len(text) < 500:
                                paa_questions.append({"question": text})
                except:
                    continue

            # If no questions found with specific selectors, try a broader approach
            if not paa_questions:
                paa_questions = self._extract_paa_generic(soup)

        except Exception as e:
            print(f"Error parsing HTML: {e}")

        return paa_questions

    def _extract_paa_generic(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Generic extraction of PAA questions by looking for text near "People also ask"

        Args:
            soup: BeautifulSoup object

        Returns:
            List of PAA questions
        """
        paa_questions = []

        # Find text "People also ask" in the page
        for element in soup.find_all(string=re.compile("People also ask", re.IGNORECASE)):
            # Navigate to parent container
            parent = element.parent
            while parent and len(paa_questions) < 10:
                # Look for sibling elements that might contain questions
                for sibling in parent.find_next_siblings():
                    text = sibling.get_text(strip=True)
                    # Filter for question-like text
                    if "?" in text and len(text) > 5 and len(text) < 500:
                        paa_questions.append({"question": text})
                        if len(paa_questions) >= 10:
                            break
                parent = parent.parent

        return paa_questions
