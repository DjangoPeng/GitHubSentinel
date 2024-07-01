class ReportGenerator:
    def generate(self, updates):
        # Implement report generation logic
        report = ""
        for repo, events in updates.items():
            report += f"Repository: {repo}\n"
            for event in events:
                report += f"- {event['type']} at {event['created_at']}\n"
        return report
