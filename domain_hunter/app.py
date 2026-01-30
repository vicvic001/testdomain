from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable

from domain_hunter.config import Config
from domain_hunter.crawler import crawl_bitcointalk
from domain_hunter.domain_check import check_domain_availability
from domain_hunter.notifier import Notifier
from domain_hunter.storage import DomainStore


@dataclass(frozen=True)
class CandidateDomain:
    domain: str
    source_url: str
    found_at: str


def _discover_domains(config: Config) -> Iterable[CandidateDomain]:
    for post in crawl_bitcointalk(config):
        for domain in post.domains:
            yield CandidateDomain(domain=domain, source_url=post.url, found_at=post.posted_at)


def _process_domains(config: Config, store: DomainStore, notifier: Notifier) -> None:
    for candidate in _discover_domains(config):
        if store.domain_seen(candidate.domain):
            continue

        available = check_domain_availability(candidate.domain, config.app.user_agent)
        store.record_domain(candidate.domain, candidate.source_url, candidate.found_at, available)

        if available:
            notifier.notify(candidate.domain, candidate.source_url, candidate.found_at)
            store.mark_notified(candidate.domain)


def run(config: Config, run_once: bool = False) -> None:
    store = DomainStore(config.storage.sqlite_path)
    notifier = Notifier(config.notifications)

    while True:
        _process_domains(config, store, notifier)
        if run_once:
            break
        time.sleep(config.app.poll_interval_seconds)
