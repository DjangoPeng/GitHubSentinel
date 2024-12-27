import json

class SubscriptionManager:
    def __init__(self, subscriptions_file):
        self.subscriptions_file = subscriptions_file
    
    def get_subscriptions(self):
        with open(self.subscriptions_file, 'r') as f:
            return json.load(f)
