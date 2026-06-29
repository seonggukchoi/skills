---
name: watercrawl
description: >-
  Scrape, crawl, and web-search through a self-hosted WaterCrawl API instance.
  Use this skill when the built-in WebFetch is blocked or fails (HTTP 403, bot
  detection, Cloudflare, empty/garbled body), when a page needs JavaScript
  rendering, when you must crawl a whole site or many pages, when you need web
  (SERP) search results, or when the user explicitly mentions "watercrawl",
  crawling, scraping a site, capturing a screenshot/PDF of a page, or extracting
  a page as markdown. It returns clean markdown (plus optional HTML, links,
  screenshots, PDFs) via the WaterCrawl REST API. For a simple single-page fetch
  where WebFetch already works, prefer WebFetch; reach for this skill in the
  situations above.
---

# WaterCrawl

WaterCrawl is a self-hosted web crawling/scraping service with a REST API. This skill
calls that API to turn web pages into clean markdown, crawl entire sites, and run web
searches — useful when `WebFetch` can't get the content (anti-bot, JS rendering) or when
you need more than one page.

## When to use this vs. WebFetch / WebSearch

- **Single page, no blocking** → `WebFetch` is fine. Don't reach for WaterCrawl.
- **WebFetch returned a block page / 403 / empty body, or the page is JS-rendered** → use `scrape` here.
- **Need many pages or a whole site** → use `crawl`.
- **Need search-engine results (SERP) with snippets** → use `search`.
- **User explicitly asks for watercrawl / a screenshot / a PDF capture** → use the matching command.

## Setup (required)

The helper reads two environment variables. The user has already exported these; verify
before first use:

```bash
[ -n "$WATERCRAWL_BASE_URL" ] && [ -n "$WATERCRAWL_API_KEY" ] && echo "ok" || echo "missing env"
```

- `WATERCRAWL_BASE_URL` — instance host, e.g. `https://watercrawl.example.com` (no `/api/v1` suffix).
- `WATERCRAWL_API_KEY` — sent as the `X-API-Key` header. (Note: the API key uses
  `X-API-Key`, **not** `Authorization: Bearer` — that header is for dashboard JWT sessions.)

Never print the key. Pass it via the environment; the helper picks it up automatically.

## How it works (why a helper script)

Every WaterCrawl job is **asynchronous**: a `POST` returns a `uuid`, then you poll the
job until `status == finished` and fetch the result with `?prefetched=true` to get the
page content inlined. `scripts/watercrawl.py` wraps that whole loop (standard library
only, no install) so you get markdown back in one command.

Run it with the system `python3` (call `/usr/bin/python3` if `python3` isn't on PATH —
this shell's PATH can be inconsistent):

```bash
python3 ~/.claude/skills/watercrawl/scripts/watercrawl.py <command> [options]
```

## Commands

### scrape — one page → markdown

```bash
# basic: prints the page as markdown to stdout
python3 .../watercrawl.py scrape https://example.com

# include raw HTML + links, or capture a screenshot/PDF (returned as attachment URLs)
python3 .../watercrawl.py scrape https://example.com --html --links
python3 .../watercrawl.py scrape https://example.com --screenshot --json

# wait for JS to render before extracting
python3 .../watercrawl.py scrape https://spa.example.com --wait-time 2000
```

### crawl — a site / many pages

```bash
# crawl up to depth 2, max 50 pages, staying on one domain
python3 .../watercrawl.py crawl https://example.com --max-depth 2 --page-limit 50 \
  --allowed-domains example.com

# restrict to a section
python3 .../watercrawl.py crawl https://example.com --include-paths "/docs/*"
```

Output is each page as `# <url>` followed by its markdown, separated by `---`. Use
`--json` to get the structured array (url, result, attachments per page).

### search — web (SERP) search

```bash
python3 .../watercrawl.py search "self-hosted crawler" --limit 5
python3 .../watercrawl.py search "data residency regulations" --limit 10 --depth advanced --language en --country us
```

### status / quota — inspect

```bash
python3 .../watercrawl.py status <uuid>            # crawl job state
python3 .../watercrawl.py status <uuid> --kind search
python3 .../watercrawl.py quota                    # plan credits / limits (+ auth health check)
```

`quota` is also the simplest auth/connectivity check — a 200 means the key works. (Don't
use `/core/usage/` for this: it's dashboard-JWT-only and returns 401 to API keys.)

## Common options

| Option | Applies to | Meaning |
| --- | --- | --- |
| `--json` | all | raw JSON instead of markdown/text |
| `--quiet` | all | suppress progress lines on stderr |
| `--max-wait N` | scrape/crawl/search | give up after N seconds (default 300) |
| `--poll-interval N` | scrape/crawl/search | seconds between status checks (default 2) |
| `--html` / `--links` | scrape/crawl | include raw HTML / extracted links |
| `--screenshot` / `--pdf` | scrape/crawl | capture media (returned as attachment URLs) |
| `--wait-time MS` | scrape/crawl | wait for JS render before extracting |
| `--no-main-content` | scrape/crawl | keep full page instead of main content only |

The full option set, request/response schemas, raw `curl` equivalents, and the official
SDKs are in [references/api.md](references/api.md). Read it when a needed option isn't
exposed as a flag, when debugging a non-2xx response, or when you'd rather call the API
directly.

## Interpreting results

- Page content comes back in the result JSON's **`markdown`** field (always present).
  `--html` adds `html`, `--links` adds `links`, and screenshots/PDFs come as
  `attachments[]` with downloadable URLs (printed to stderr in non-JSON mode).
- A job can end `failed` or `canceled` — the helper exits non-zero and reports the status.
- If a crawl finishes but returns few pages, the site may block crawlers or the depth/limit
  was too low — raise `--max-depth` / `--page-limit` or check `--allowed-domains`.

## Troubleshooting

- **HTTP 401/403** → key/header problem. Confirm `WATERCRAWL_API_KEY` is set; the API uses
  `X-API-Key`. The helper adds a hint on these codes. Note: `/core/usage/` returns 401 to API
  keys *by design* (it's dashboard-only) — that's not a key problem; use `quota` to verify auth.
- **search returns 0 results** → the instance likely has no SERP/search provider configured.
  `scrape` and `crawl` don't need one; `search` does. Verify on the WaterCrawl server side.
- **`python3: command not found`** → use `/usr/bin/python3` explicitly.
- **Timeout** → large crawls take time; raise `--max-wait`, or create the job and poll later
  with `status`.
- **Connection refused / DNS** → check `WATERCRAWL_BASE_URL` reachability.
