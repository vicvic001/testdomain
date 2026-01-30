# Bitcointalk Domain Hunter

This app monitors Bitcointalk posts for domain names mentioned between 2009 and 2016, checks whether those domains are available for registration, and notifies you when a candidate is available.

## Features
- Crawls Bitcointalk board pages and/or a curated list of topic URLs.
- Filters posts by year (default: 2009–2016).
- Extracts domain names and normalizes them.
- Checks availability via RDAP.
- Sends notifications through email (SMTP) or an HTTP webhook.
- Stores progress in SQLite to avoid reprocessing.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python -m domain_hunter --config config.yaml --once
```

## Testing

This project does not yet have automated tests. You can run a quick manual sanity check by pointing the config at a small set of Bitcointalk topics and running a single pass:

```bash
python -m domain_hunter --config config.yaml --once
```

To validate notifications, enable either the email or webhook settings in `config.yaml` and re-run the command.

## Viewing results

Available domains are surfaced in two ways:

1. **Notifications** (recommended): enable email or webhook notifications in `config.yaml`. When a domain is detected as available, you will receive a message with the domain and the Bitcointalk source URL.
2. **SQLite database**: every discovered domain is stored in the SQLite database defined by `storage.sqlite_path` (default: `domain_hunter.db`). The `available` column is `1` for available domains. You can query it directly:

```bash
sqlite3 domain_hunter.db "SELECT domain, first_seen_url, first_seen_at FROM domains WHERE available = 1 ORDER BY first_seen_at DESC;"
```

> **Note:** you need to run the crawler at least once to populate the database and trigger notifications:
>
> ```bash
> python -m domain_hunter --config config.yaml --once
> ```

## Configuration
See `config.example.yaml` for all options.

## Notes
- Bitcointalk HTML structures can change; you may need to adjust selectors in `domain_hunter/crawler.py` if the forum markup changes.
- RDAP availability checks can rate-limit or differ by TLD. The app treats HTTP 404 as “available.”
- This app does **not** buy domains automatically; it only notifies you so you can purchase them.
