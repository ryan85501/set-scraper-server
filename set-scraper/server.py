# --- Corrected Flask Server Code for Render ---
# This server proxies SET data scraping and serves JSON to the frontend.

from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/")
def home():
    """Default route for testing"""
    return {"message": "Flask server is running on Render!"}

@app.route("/health")
def health():
    """Health check endpoint for Render"""
    return {"status": "ok"}

@app.route('/get_set_data', methods=['GET'])
def get_set_data():
    """
    Fetches live SET data from the SET.or.th website by scraping.
    This function is a proxy to bypass CORS issues when fetching data directly from the browser.
    """
    try:
        url = "https://www.set.or.th/th/market/index/set/overview"
        
        # Mimic a real browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the SET Index value
        set_index_div = soup.find('div', class_='value text-white mb-0 me-2 lh-1 stock-info')
        set_result = set_index_div.text.strip() if set_index_div else "N/A"

        # Find the "Value" number
        value_div = soup.find('span', class_='ms-2 ms-xl-4')
        value = value_div.text.strip() if value_div else "N/A"
        
        # Placeholder for 2D lottery data scraping
        live_result = "N/A"
        
        # Return results
        if set_result != "N/A" and value != "N/A":
            return jsonify({
                'set_result': set_result,
                'value': value,
                'live_result': live_result
            })
        else:
            print("Could not find the necessary data on the page.")
            return jsonify({'error': 'Data not found on the page'}), 500

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return jsonify({'error': 'Failed to connect to the external website.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': f'Unexpected error: {e}'}), 500


if __name__ == '__main__':
    # Run on Render-compatible settings
    app.run(host='0.0.0.0', port=5000)
