# server.py
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import socket
import os
import logging

app = Flask(__name__)
CORS(app)  # allow browser fetches from other origins

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("set-scraper")


def text_of(el):
    return el.get_text(strip=True) if el else None


@app.route("/")
def index():
    return (
        "SET scraper server running. Use GET /get_set_data to fetch SET index & value.",
        200,
    )


@app.route("/get_set_data", methods=["GET"])
def get_set_data():
    """
    Scrape the SET overview page and return:
      - set_result: the main SET index number (e.g. "1,278.05")
      - value: the Value (M.Baht) number (e.g. "42,552.94")
      - live_result: placeholder (you can add lottery scraping later)
    """
    # Prefer English page (change to /th/ if you want the Thai page)
    url = "https://www.set.or.th/en/market/index/set/overview"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.exception("Failed to fetch SET page")
        return jsonify({"error": f"Failed to fetch external page: {str(e)}"}), 502

    soup = BeautifulSoup(resp.text, "html.parser")

    # 1) Try direct CSS selectors for the main index number
    # Many SET pages show the main number inside something like:
    #   <div class="quote-header"> ... <div class="quote-info-left-values"> <div class="value ... stock-info">1,278.05</div>
    set_el = soup.select_one("div.quote-header div.quote-info-left-values div.value")
    if not set_el:
        # fallback: look for an element with both 'value' and 'stock-info' classes
        set_el = soup.find(
            lambda t: t.name in ("div", "span")
            and t.get("class")
            and ("value" in t.get("class") and "stock-info" in t.get("class"))
        )

    set_result = text_of(set_el) if set_el else None

    # 2) Find the "Value (M.Baht)" numeric span
    # The value is often in: <div class="d-block quote-market-cost ..."> ... <span class="ms-2 ms-xl-4">42,552.94</span>
    value_el = soup.select_one("div.quote-header div.quote-market-cost span")
    if not value_el:
        # fallback: try to find the label text "Value" and then grab a nearby span
        label = soup.find(lambda t: t.string and "Value" in t.get_text())
        if label:
            # find first span inside same parent or parent->next elements
            parent = label.parent
            if parent:
                value_el = parent.find("span") or parent.find_next("span")

    value = text_of(value_el) if value_el else None

    # normalise whitespace / non-breaking spaces
    def normalize(s):
        if not s:
            return None
        return s.replace("\xa0", " ").strip()

    set_result = normalize(set_result)
    value = normalize(value)

    # live_result placeholder — add your own scraping logic for lottery results here
    live_result = "N/A"

    # If both are missing, return an error so you'll see it in the logs
    if (not set_result) and (not value):
        logger.warning("Could not find set_result or value; returning error")
        return jsonify({"error": "Couldn't locate expected data on the page"}), 500

    return jsonify({"set_result": set_result or "N/A", "value": value or "N/A", "live_result": live_result})


if __name__ == "__main__":
    # Print local IP for convenience when running locally
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logger.info(f"Server will be running on: http://{local_ip}:5000 (or http://127.0.0.1:5000)")
    except Exception:
        logger.info("Could not determine local IP")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
