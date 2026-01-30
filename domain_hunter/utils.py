from __future__ import annotations

import re

DOMAIN_PATTERN = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def extract_domains(text: str) -> list[str]:
    candidates = DOMAIN_PATTERN.findall(text)
    cleaned: list[str] = []
    for domain in candidates:
        normalized = domain.strip("'\"()[]{}<>.,:;!").lower()
        if normalized and normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned
