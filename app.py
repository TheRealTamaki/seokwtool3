"""Flask web application for Google PAA Scraper"""

import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from src.scraper import GooglePAAScraper


# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)


@app.route("/")
def index():
    """Serve the main page"""
    return render_template("index.html")


@app.route("/api/scrape", methods=["POST"])
def scrape_paa():
    """
    API endpoint to scrape PAA questions

    Expects JSON:
    {
        "query": "search query",
        "api_key": "firecrawl API key"
    }

    Returns JSON with PAA questions
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        query = data.get("query", "").strip()
        api_key = data.get("api_key", "").strip()

        # Validate inputs
        if not query:
            return jsonify({"success": False, "error": "Query is required"}), 400

        if not api_key:
            return jsonify({"success": False, "error": "API key is required"}), 400

        if len(query) > 500:
            return jsonify({"success": False, "error": "Query too long (max 500 characters)"}), 400

        # Initialize scraper with provided API key
        scraper = GooglePAAScraper(api_key=api_key)

        # Scrape PAA
        result = scraper.scrape_paa(query)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 401
    except Exception as e:
        return jsonify({"success": False, "error": f"Error: {str(e)}"}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Google PAA Scraper is running"})


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Get port from environment or default to 5000
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"

    print(f"Starting Google PAA Scraper on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
