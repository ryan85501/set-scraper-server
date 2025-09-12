import requests
from bs4 import BeautifulSoup
import re

def scrape_set_index():
    """
    Scrapes the current SET Index value from the set.or.th website.

    This script targets the specific HTML element containing the market value
    and cleans the data to ensure it is in the correct numerical format.
    """
    url = "https://www.set.or.th/en/market/index/set/overview"

    # Define headers to mimic a web browser request, which can help prevent some blocks.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        # Fetch the HTML content of the page
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the specific span element that contains the market value.
        # Based on the HTML you provided, the value is in a span with a specific class.
        market_value_element = soup.find("span", class_="quote-market-value")

        if market_value_element:
            # Extract the text from the element
            market_value_text = market_value_element.text.strip()
            print(f"Raw text extracted: '{market_value_text}'")

            # Clean the text: remove commas and other non-digit, non-decimal characters.
            # This is a crucial step to correctly convert the string to a number.
            cleaned_value = re.sub(r'[^\d.]', '', market_value_text.replace(',', ''))
            
            # Convert the cleaned string to a float
            set_index_value = float(cleaned_value)
            
            print(f"The current SET Index value is: {set_index_value}")
            return set_index_value
        else:
            print("Could not find the element with class 'quote-market-value'.")
            print("The website's HTML structure may have changed.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
        return None

if __name__ == "__main__":
    scrape_set_index()
