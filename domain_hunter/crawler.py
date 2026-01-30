from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from domain_hunter.config import Config
from domain_hunter.utils import extract_domains, normalize_text


@dataclass(frozen=True)
class Post:
    url: str
    posted_at: str
    domains: list[str]


def _build_headers(user_agent: str) -> dict[str, str]:
    return {"User-Agent": user_agent}


def _fetch(url: str, user_agent: str) -> str:
    response = requests.get(url, headers=_build_headers(user_agent), timeout=30)
    response.raise_for_status()
    return response.text


def _extract_post_date(raw_text: str) -> datetime | None:
    if "on:" not in raw_text:
        return None
    _, _, trailing = raw_text.partition("on:")
    trimmed = trailing.strip()
    try:
        return date_parser.parse(trimmed, fuzzy=True)
    except (ValueError, TypeError):
        return None


def _within_years(posted_at: datetime, start_year: int, end_year: int) -> bool:
    return start_year <= posted_at.year <= end_year


def _normalize_post_url(base: str, link: str) -> str:
    joined = urljoin(base, link)
    parsed = urlparse(joined)
    sanitized = parsed._replace(fragment="")
    return urlunparse(sanitized)


def _iter_topic_urls(config: Config) -> Iterable[str]:
    for url in config.bitcointalk.topic_urls:
        yield url

    base = config.bitcointalk.base_url
    for board_id in config.bitcointalk.board_ids:
        for page in range(config.bitcointalk.board_start_page, config.bitcointalk.board_end_page + 1):
            offset = page * 40
            board_url = f"{base}?board={board_id}.{offset}"
            html = _fetch(board_url, config.app.user_agent)
            soup = BeautifulSoup(html, "html.parser")
            for anchor in soup.select("a"):
                href = anchor.get("href")
                if not href or "topic=" not in href:
                    continue
                if "#" in href:
                    href = href.split("#", 1)[0]
                yield _normalize_post_url(base, href)


def _iter_topic_pages(topic_url: str, config: Config) -> Iterable[str]:
    html = _fetch(topic_url, config.app.user_agent)
    soup = BeautifulSoup(html, "html.parser")
    yield topic_url

    page_links = [
        _normalize_post_url(topic_url, anchor.get("href"))
        for anchor in soup.select("a")
        if anchor.get("href") and "topic=" in anchor.get("href")
    ]

    seen: set[str] = {topic_url}
    for link in page_links:
        if link in seen:
            continue
        if len(seen) >= config.app.max_pages_per_topic:
            break
        seen.add(link)
        yield link


def _extract_posts(html: str, config: Config, page_url: str) -> Iterable[Post]:
    soup = BeautifulSoup(html, "html.parser")
    for container in soup.select("div.post"):
        date_node = container.find("div", class_="smalltext")
        if not date_node:
            continue
        posted_at_dt = _extract_post_date(date_node.get_text(" ", strip=True))
        if not posted_at_dt:
            continue
        if not _within_years(posted_at_dt, config.app.start_year, config.app.end_year):
            continue

        body = container.find("div", class_="post") or container
        text = normalize_text(body.get_text(" ", strip=True))
        domains = extract_domains(text)
        if not domains:
            continue

        yield Post(url=page_url, posted_at=posted_at_dt.isoformat(), domains=domains)


def crawl_bitcointalk(config: Config) -> Iterable[Post]:
    for topic_url in _iter_topic_urls(config):
        for page_url in _iter_topic_pages(topic_url, config):
            html = _fetch(page_url, config.app.user_agent)
            for post in _extract_posts(html, config, page_url):
                yield post
