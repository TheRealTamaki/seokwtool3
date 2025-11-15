#!/usr/bin/env python
"""
Example script showing how to use the Google PAA Scraper programmatically
"""

import os
from dotenv import load_dotenv
from src.scraper import GooglePAAScraper


def main():
    # Load environment variables
    load_dotenv()

    # Initialize scraper with API key from environment
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("Error: FIRECRAWL_API_KEY environment variable not set")
        print("Please create a .env file with your Firecrawl API key")
        return

    scraper = GooglePAAScraper(api_key=api_key)

    # Example queries
    queries = [
        "how to learn python programming",
        "best practices for web development",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)

        result = scraper.scrape_paa(query)

        if result["success"]:
            print(f"Status: {result.get('message', 'Success')}")
            print(f"Found {len(result['paa_questions'])} questions:\n")

            for i, item in enumerate(result["paa_questions"], 1):
                print(f"{i}. {item['question']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
