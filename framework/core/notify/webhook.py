import os
import json
import urllib.request


class WebhookNotifier:
    """
    Minimal generic webhook notifier.
    Reads ORG_WEBHOOK_URL from environment; if not set, no-ops.
    Payload is JSON with keys: type, org_name, org_domain, email, token
    """

    def __init__(self):
        self.url = os.getenv("ORG_WEBHOOK_URL")

    def is_configured(self) -> bool:
        return bool(self.url)

    def notify_verification(self, org_name: str, org_domain: str, email: str, token: str) -> None:
        if not self.is_configured():
            return
        payload = {
            "type": "org_verification",
            "org_name": org_name,
            "org_domain": org_domain,
            "email": email,
            "token": token,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as _:
            pass