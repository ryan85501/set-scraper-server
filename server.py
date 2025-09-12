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
    
    The selectors have been updated to reflect recent changes to the
    SET website's HTML structure. The old selectors no longer worked.
    """
    url = "https://www.set.or.th/en/market/index/set/overview"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Use updated selectors to find the SET Index and Value
        # The main stock information container
        main_info_container = soup.find("div", class_="market-set-overview__stock-info")
        
        set_result = None
        value = None

        if main_info_container:
            # Find the SET Index value within its specific class
            set_value_div = main_info_container.find("div", class_="stock-info__value")
            if set_value_div and set_value_div.text.strip():
                set_result = set_value_div.text.strip().replace(",", "")

            # Find the Value (Baht) value within its specific class
            value_div = main_info_container.find("div", class_="value__value")
            if value_div and value_div.text.strip():
                value = value_div.text.strip().replace(",", "")

        if not set_result or not value:
            # If the specific containers are not found, fallback to searching for generic classes.
            # This is a good practice to handle minor layout changes.
            set_div = soup.find("div", class_="value text-white mb-0 me-2 lh-1 stock-info")
            if set_div:
                set_result = set_div.text.strip().replace(",", "")

            value_span = soup.find("span", class_="ms-2 ms-xl-4")
            if value_span:
                value = value_span.text.strip().replace(",", "")

        return set_result, value

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        return None, None


def calculate_live_result(set_result, value):
    """
    Calculate live_result using:
    - last digit of set_result (including decimals)
    - last digit of value (integer part only, no decimals)
    """
    try:
        # last digit of SET (handles both integer and decimal values)
        set_str = str(set_result)
        last_digit_set = set_str[-1]

        # last digit of Value (ignore decimals)
        value_str = str(value).split(".")[0].replace(",", "")
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

    in_morning = morning_start <= now <= morning_end
    in_evening = evening_start <= now <= evening_end

    try:
        if in_morning or in_evening:
            # Live trading → fetch fresh data
            set_result, value = fetch_set_data()

            if set_result and value:
                live_result = calculate_live_result(set_result, value)

                last_official_data = {
                    "set_result": set_result,
                    "value": value,
                    "live_result": live_result,
                    "time": current_time,
                }
                return jsonify(last_official_data)
            else:
                # If fetching live data fails, fall back to frozen data if available
                if last_official_data:
                    return jsonify(last_official_data)
                return jsonify({"error": "Failed to fetch live data"})


        # Outside trading → return last frozen result
        if last_official_data:
            return jsonify(last_official_data)

        # If no frozen data yet
        return jsonify({"error": "No official data yet"})

    except Exception as e:
        if last_official_data:
            return jsonify(last_official_data)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server running on: http://{local_ip}:5000")
    app.run(host="0.0.0.0", port=5000)
