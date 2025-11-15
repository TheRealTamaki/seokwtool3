"""Command-line interface for Google PAA Scraper"""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import click

from .scraper import GooglePAAScraper


# Load environment variables from .env file
load_dotenv()


@click.command()
@click.argument("query")
@click.option(
    "--api-key",
    envvar="FIRECRAWL_API_KEY",
    help="Firecrawl API key (can also set FIRECRAWL_API_KEY env var)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (JSON format)",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
def scrape(query: str, api_key: str, output: str, output_json: bool):
    """
    Scrape People Also Ask (PAA) questions from Google search results

    Example:
        python -m src.cli "how to make pizza"
        python -m src.cli "best programming languages" --json
        python -m src.cli "SEO tips" --output results.json
    """
    if not api_key:
        click.echo(
            "Error: Firecrawl API key is required.",
            err=True,
        )
        click.echo(
            "Please set FIRECRAWL_API_KEY environment variable or use --api-key option.",
            err=True,
        )
        sys.exit(1)

    try:
        # Initialize scraper
        scraper = GooglePAAScraper(api_key=api_key)

        # Scrape PAA
        click.echo(f"Scraping PAA for query: '{query}'", err=True)
        result = scraper.scrape_paa(query)

        # Format output
        if output_json or output:
            output_data = {
                "query": result["query"],
                "success": result["success"],
                "paa_questions": result["paa_questions"],
            }
            if "message" in result:
                output_data["message"] = result["message"]
            if "error" in result:
                output_data["error"] = result["error"]

            json_output = json.dumps(output_data, indent=2)

            if output:
                # Write to file
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(json_output)
                click.echo(f"Results saved to: {output}")
            else:
                # Print to stdout
                click.echo(json_output)
        else:
            # Pretty print text output
            click.echo(f"\n✓ Query: {result['query']}")
            click.echo(f"✓ {result.get('message', 'Done')}\n")

            if result["paa_questions"]:
                click.echo("People Also Ask Questions:")
                click.echo("-" * 50)
                for i, q in enumerate(result["paa_questions"], 1):
                    click.echo(f"{i}. {q['question']}")
            else:
                click.echo("No PAA questions found.")

            if not result["success"] and "error" in result:
                click.echo(f"\nError: {result['error']}", err=True)

        sys.exit(0 if result["success"] else 1)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    scrape()
