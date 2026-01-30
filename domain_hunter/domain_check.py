from __future__ import annotations

import requests


def check_domain_availability(domain: str, user_agent: str) -> bool:
    url = f"https://rdap.org/domain/{domain}"
    response = requests.get(url, headers={"User-Agent": user_agent}, timeout=20)
    if response.status_code == 404:
        return True
    if response.status_code == 200:
        return False
    return False
