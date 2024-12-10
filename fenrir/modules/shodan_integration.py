
import logging
import requests

class ShodanIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        self.logger = logging.getLogger("ShodanIntegration")
        self.base_url = "https://api.shodan.io"

    def query_shodan(self, target):
        try:
            url = f"{self.base_url}/shodan/host/{target}?key={self.api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error querying Shodan: {str(e)}")
            return {"error": str(e)}

    def run(self, target):
        self.logger.info(f"Querying Shodan for target: {target}")
        return self.query_shodan(target)
