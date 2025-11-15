# Google PAA Scraper Tool

A simple, focused tool that scrapes **People Also Ask** (PAA) questions from Google search results using the Firecrawl API.

## Features

- 🎯 **One-purpose tool**: Scrapes only "People Also Ask" questions from Google search results
- 🔥 **Firecrawl powered**: Uses the Firecrawl API for reliable web scraping
- 📋 **Multiple output formats**: Text, JSON, or save to file
- 🚀 **Easy to use**: Simple CLI interface
- 🔧 **Minimal dependencies**: Only essential packages included

## Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd seokwtool3
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Firecrawl API key:
```bash
# Create a .env file
echo "FIRECRAWL_API_KEY=your_api_key_here" > .env
```

You can get a Firecrawl API key from [https://firecrawl.dev](https://firecrawl.dev)

## Usage

### Basic usage (display in terminal):
```bash
python -m src.cli "how to make pizza"
```

### Output as JSON:
```bash
python -m src.cli "best programming languages" --json
```

### Save results to file:
```bash
python -m src.cli "SEO tips" --output results.json
```

### Using a specific API key (without .env file):
```bash
python -m src.cli "machine learning" --api-key your_api_key_here
```

## Output Format

### Text Output (default):
```
✓ Query: how to make pizza
✓ Successfully scraped 5 PAA questions

People Also Ask Questions:
--------------------------------------------------
1. How do you make pizza dough from scratch?
2. What is the best pizza sauce?
3. How long does pizza take to cook?
4. Can you freeze pizza dough?
5. What temperature should pizza be cooked at?
```

### JSON Output:
```json
{
  "query": "how to make pizza",
  "success": true,
  "paa_questions": [
    {
      "question": "How do you make pizza dough from scratch?"
    },
    {
      "question": "What is the best pizza sauce?"
    }
  ],
  "message": "Successfully scraped 5 PAA questions"
}
```

## Project Structure

```
seokwtool3/
├── src/
│   ├── __init__.py
│   ├── scraper.py      # Main scraper logic
│   └── cli.py          # Command-line interface
├── .env                # Environment variables (create this)
├── .gitignore
├── requirements.txt
└── README.md
```

## How It Works

1. **URL Construction**: Builds a Google search URL for the provided query
2. **Web Scraping**: Uses Firecrawl API to scrape the search results page
3. **Content Extraction**: Parses the HTML/Markdown to find "People Also Ask" section
4. **Question Extraction**: Identifies and extracts individual PAA questions
5. **Output**: Returns results in requested format (text/JSON)

## API Details

The tool uses the [Firecrawl API](https://firecrawl.dev) which provides:
- Reliable JavaScript rendering
- HTML and Markdown output
- Automatic content extraction

## Troubleshooting

### "Firecrawl API key not provided"
Make sure you have set the `FIRECRAWL_API_KEY` environment variable:
```bash
export FIRECRAWL_API_KEY=your_key_here
# Or create a .env file with: FIRECRAWL_API_KEY=your_key_here
```

### "No PAA questions found"
- The query might not have PAA results on Google
- Try a different, more common search query
- Check if Google is blocking the request

### Module not found errors
Make sure you're in the virtual environment and have installed dependencies:
```bash
pip install -r requirements.txt
```

## License

MIT License

## Contributing

This tool is designed to be simple and focused. It does one thing well: scrape Google PAA questions.
