import os
import smtplib
from email.message import EmailMessage


class Emailer:
    """
    Minimal SMTP emailer. Reads settings from environment variables:

    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_TLS (optional, default: true)
    ORG_VERIFY_BASE_URL (optional): if set, include clickable verification link in email.

    If SMTP_HOST is not set, send_verification will no-op (and caller may display the token).
    """

    def __init__(self):
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASS")
        self.sender = os.getenv("SMTP_FROM", self.user or "no-reply@example.com")
        self.tls = os.getenv("SMTP_TLS", "true").lower() in {"1", "true", "yes"}
        self.verify_base = os.getenv("ORG_VERIFY_BASE_URL")

    def is_configured(self) -> bool:
        return bool(self.host)

    def send_verification(self, to_email: str, org_name: str, token: str) -> None:
        if not self.is_configured():
            return
        subject = f"[Approval Required] Verify access for {org_name}"
        link = ""
        if self.verify_base:
            sep = "&" if "?" in self.verify_base else "?"
            link = f"\nVerification link:\n  {self.verify_base}{sep}token={token}\n"
        body = (
            f"Hello,\n\n"
            f"A request was made to enable access for organization '{org_name}'.\n"
            f"Verification token:\n\n"
            f"  {token}\n"
            f"{link}\n"
            f"To authorize, you may click the link above (if reachable) or\n"
            f"enter the token into the CLI on an authorized machine:\n\n"
            f"  framework org verify --token {token}\n\n"
            f"If you did not request this, please ignore this email.\n"
        )

        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(self.host, self.port, timeout=20) as server:
            if self.tls:
                server.starttls()
            if self.user and self.password:
                server.login(self.user, self.password)
            server.send_message(msg)