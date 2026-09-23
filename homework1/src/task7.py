import requests

def fetch_website_status(url):
    # Fetches a URL and returns its HTTP status code 
    try:
        response = requests.get(url, timeout=5)
        return response.status_code
    except requests.RequestException:
        # Returns None if there is a network error or timeout
        return None