import requests
import json

class NotifierService:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send(self, message):
        payload = {"message": message}
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            self.webhook_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        response.raise_for_status()
