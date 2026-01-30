from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class AppConfig:
    start_year: int
    end_year: int
    poll_interval_seconds: int
    max_pages_per_topic: int
    user_agent: str


@dataclass(frozen=True)
class BitcointalkConfig:
    base_url: str
    topic_urls: list[str]
    board_ids: list[int]
    board_start_page: int
    board_end_page: int


@dataclass(frozen=True)
class StorageConfig:
    sqlite_path: str


@dataclass(frozen=True)
class EmailConfig:
    enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_address: str
    to_addresses: list[str]


@dataclass(frozen=True)
class WebhookConfig:
    enabled: bool
    url: str


@dataclass(frozen=True)
class NotificationConfig:
    email: EmailConfig
    webhook: WebhookConfig


@dataclass(frozen=True)
class Config:
    app: AppConfig
    bitcointalk: BitcointalkConfig
    storage: StorageConfig
    notifications: NotificationConfig


def _require(data: dict[str, Any], key: str, context: str) -> Any:
    if key not in data:
        raise KeyError(f"Missing config key '{context}.{key}'")
    return data[key]


def load_config(path: str | Path) -> Config:
    raw = yaml.safe_load(Path(path).read_text())

    app_raw = _require(raw, "app", "root")
    app = AppConfig(
        start_year=int(_require(app_raw, "start_year", "app")),
        end_year=int(_require(app_raw, "end_year", "app")),
        poll_interval_seconds=int(_require(app_raw, "poll_interval_seconds", "app")),
        max_pages_per_topic=int(_require(app_raw, "max_pages_per_topic", "app")),
        user_agent=str(_require(app_raw, "user_agent", "app")),
    )

    bitcointalk_raw = _require(raw, "bitcointalk", "root")
    bitcointalk = BitcointalkConfig(
        base_url=str(_require(bitcointalk_raw, "base_url", "bitcointalk")),
        topic_urls=list(bitcointalk_raw.get("topic_urls", [])),
        board_ids=[int(value) for value in bitcointalk_raw.get("board_ids", [])],
        board_start_page=int(bitcointalk_raw.get("board_start_page", 0)),
        board_end_page=int(bitcointalk_raw.get("board_end_page", 0)),
    )

    storage_raw = _require(raw, "storage", "root")
    storage = StorageConfig(
        sqlite_path=str(_require(storage_raw, "sqlite_path", "storage")),
    )

    notifications_raw = _require(raw, "notifications", "root")
    email_raw = notifications_raw.get("email", {})
    email = EmailConfig(
        enabled=bool(email_raw.get("enabled", False)),
        smtp_host=str(email_raw.get("smtp_host", "")),
        smtp_port=int(email_raw.get("smtp_port", 0)),
        smtp_user=str(email_raw.get("smtp_user", "")),
        smtp_password=str(email_raw.get("smtp_password", "")),
        from_address=str(email_raw.get("from_address", "")),
        to_addresses=list(email_raw.get("to_addresses", [])),
    )

    webhook_raw = notifications_raw.get("webhook", {})
    webhook = WebhookConfig(
        enabled=bool(webhook_raw.get("enabled", False)),
        url=str(webhook_raw.get("url", "")),
    )

    notifications = NotificationConfig(email=email, webhook=webhook)

    return Config(
        app=app,
        bitcointalk=bitcointalk,
        storage=storage,
        notifications=notifications,
    )
