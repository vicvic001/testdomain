from __future__ import annotations

import json
import smtplib
from email.message import EmailMessage

import requests

from domain_hunter.config import NotificationConfig


class Notifier:
    def __init__(self, config: NotificationConfig) -> None:
        self._config = config

    def notify(self, domain: str, source_url: str, found_at: str) -> None:
        message = {
            "domain": domain,
            "source_url": source_url,
            "found_at": found_at,
        }
        if self._config.email.enabled:
            self._send_email(message)
        if self._config.webhook.enabled:
            self._send_webhook(message)

    def _send_email(self, message: dict[str, str]) -> None:
        email_cfg = self._config.email
        email = EmailMessage()
        email["Subject"] = f"Available domain found: {message['domain']}"
        email["From"] = email_cfg.from_address
        email["To"] = ", ".join(email_cfg.to_addresses)
        email.set_content(
            "\n".join(
                [
                    f"Domain: {message['domain']}",
                    f"Found at: {message['found_at']}",
                    f"Source: {message['source_url']}",
                ]
            )
        )

        with smtplib.SMTP(email_cfg.smtp_host, email_cfg.smtp_port) as server:
            server.starttls()
            if email_cfg.smtp_user:
                server.login(email_cfg.smtp_user, email_cfg.smtp_password)
            server.send_message(email)

    def _send_webhook(self, message: dict[str, str]) -> None:
        webhook_cfg = self._config.webhook
        requests.post(webhook_cfg.url, data=json.dumps(message), timeout=10)
