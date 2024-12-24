import requests

class GitHubClient:
    def __init__(self, token):
        self.token = token
    
    def fetch_updates(self, subscriptions):
        headers = {
            'Authorization': f'token {self.token}'
        }
        updates = {}
        for repo in subscriptions:
            response = requests.get(f'https://api.github.com/repos/{repo}/events', headers=headers)
            if response.status_code == 200:
                updates[repo] = response.json()
        return updates
