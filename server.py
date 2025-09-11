# --- Flask Server for SET Scraping with Frozen Results ---
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import socket
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

# Store the last official data
last_official_data = None  

# Myanmar TimeZone
myanmar_tz = pytz.timezone("Asia/Yangon")


def fetch_set_data():
    """
    Scrape the SET website to get SET Index and Value.
    """
    url = "https://www.set.or.th/en/market/index/set/overview"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Get SET Index
    set_div = soup.find("div", class_="value text-white mb-0 me-2 lh-1 stock-info")
    set_result = set_div.text.strip().replace(",", "") if set_div else None

    # Get Value (Baht)
    value_span = soup.find("span", class_="ms-2 ms-xl-4")
    value = value_span.text.strip().replace(",", "") if value_span else None

    if not set_result or not value:
        return None, None

    return set_result, value


def calculate_live_result(set_result, value):
    """
    Calculate live_result using:
    - last digit of set_result (including decimals)
    - last digit of value (integer part only, no decimals)
    """
    try:
        # last digit of SET
        set_str = set_result.replace(",", "")
        last_digit_set = set_str[-1]

        # last digit of Value (ignore decimals)
        value_str = value.split(".")[0].replace(",", "")
        last_digit_value = value_str[-1]

        return last_digit_set + last_digit_value
    except Exception:
        return None


@app.route("/get_set_data", methods=["GET"])
def get_set_data():
    global last_official_data

    now = datetime.now(myanmar_tz)
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Trading windows (Myanmar time)
    morning_start = now.replace(hour=11, minute=30, second=0, microsecond=0)
    morning_end = now.replace(hour=12, minute=1, second=0, microsecond=0)
    evening_start = now.replace(hour=15, minute=30, second=0, microsecond=0)
    evening_end = now.replace(hour=16, minute=30, second=0, microsecond=0)

    in_morning = morning_start <= now <= morning
