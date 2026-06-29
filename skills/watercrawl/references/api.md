# WaterCrawl API reference

Detailed reference for the WaterCrawl REST API, for when `scripts/watercrawl.py` doesn't
expose an option you need, when debugging a non-2xx response, or when calling the API
directly. Verified against the OpenAPI 3.0.3 schema (`<base>/api/schema/`, `info.version 1.0.0`)
and the official Python (`watercrawl-py`) and Node (`@watercrawl/nodejs`) SDK sources.

## Contents
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Async model: poll vs SSE vs prefetched](#async-model)
- [Endpoints](#endpoints)
- [Request options](#request-options)
- [Response shapes](#response-shapes)
- [Raw curl examples](#raw-curl-examples)
- [Official SDKs](#official-sdks)
- [Known issues / unverified](#known-issues--unverified)

## Authentication

API-key auth uses the **`X-API-Key`** header:

```
X-API-Key: <YOUR_API_KEY>
```

The instance's **external-API** OpenAPI doc (`WaterCrawl API.yaml`, the Team-API-Key spec)
defines exactly one security scheme — `ApiKeyAuth` (`type: apiKey, in: header, name:
X-API-Key`) — and a live `GET /core/crawl-requests/` returned **200** with it. Confirmed.
The auto-generated full docs sometimes show `Authorization: Bearer <key>` — that is the
**dashboard JWT/session** scheme (`jwtAuth` / `cookieAuth`), *not* API-key auth. Use `X-API-Key`.

Keys are created/revoked in the dashboard's **API Keys** page and are scoped to a team.
The SDKs also send `Content-Type: application/json` and `Accept: application/json`.

## Base URL

- Cloud default: `https://app.watercrawl.dev` (the SDK default).
- Self-hosted: same path layout, just a different host. Set `WATERCRAWL_BASE_URL` to the
  instance origin (e.g. `https://watercrawl.example.com`) with **no** `/api/v1` suffix.
- Path prefixes: `/api/v1/core/` (crawl, search, sitemap, usage), `/api/v1/plan/` (subscription/quota),
  `/api/v1/user/` (profile, API keys, teams).
- List endpoints use DRF pagination: response has `count`, `next`, `previous`, `results`;
  query params `page`, `page_size`.

<a name="async-model"></a>
## Async model: poll vs SSE vs prefetched

**No endpoint returns content synchronously.** A `POST` creates a job and returns its
`uuid` with `status: "new"`. Three ways to get the result:

1. **Poll (what the helper does):** `GET /{uuid}/` (or `/{uuid}/status/`) until
   `status == "finished"`, then `GET .../results/?prefetched=true`. Simple and robust.
2. **SSE:** open `GET /{uuid}/status/` as an event stream for live events
   (`type` = `feed` progress / `state` status / `result` page payload). The SDK's
   `monitor_crawl_request` uses this. More complex; the helper avoids it.
3. **`prefetched=true`:** by default `result` fields are **download URLs**; with
   `?prefetched=true` the JSON body (markdown/html/links/metadata) is inlined. Always pass
   it when you want content in-band.

Status values (`StatusEnum`): `new` → `running` → `finished` | `canceling` | `canceled` | `failed`.

## Endpoints

All paths are under the base URL. `core` = `/api/v1/core`.

### Crawl requests
| Method | Path | Purpose |
| --- | --- | --- |
| GET | `core/crawl-requests/` | list crawl jobs (paginated) |
| POST | `core/crawl-requests/` | create a crawl/scrape job → returns `uuid` |
| GET | `core/crawl-requests/{id}/` | job detail (includes `status`) |
| DELETE | `core/crawl-requests/{id}/` | cancel/delete a job |
| GET | `core/crawl-requests/{id}/status/` | status (poll) or SSE stream; query `prefetched` |
| GET | `core/crawl-requests/{id}/download/` | bundle download of all results; query `output_format=json\|markdown` (default `json`) |
| GET | `core/crawl-requests/{id}/sitemap/graph/` | crawl-derived sitemap as graph JSON |
| GET | `core/crawl-requests/{id}/sitemap/markdown/` | crawl-derived sitemap as markdown |
| POST | `core/crawl-requests/batch/` | batch crawl of multiple URLs |

### Crawl results
| Method | Path | Purpose |
| --- | --- | --- |
| GET | `core/crawl-requests/{crawl_request_uuid}/results/` | per-page results; query `prefetched`, `page`, `page_size`, `url`, `created_at` |
| GET | `core/crawl-requests/{crawl_request_uuid}/results/{id}/` | a single page result |

### Search
| Method | Path | Purpose |
| --- | --- | --- |
| GET | `core/search/` | list search jobs |
| POST | `core/search/` | create a SERP search job → `uuid` |
| GET | `core/search/{id}/` | detail; `?prefetched=true` inlines results |
| GET | `core/search/{id}/status/` | status (poll); query `prefetched` |
| DELETE | `core/search/{id}/` | cancel |

### Sitemaps (standalone) & misc
| Method | Path | Purpose |
| --- | --- | --- |
| GET / POST | `core/sitemaps/` | list / create a sitemap job |
| GET / DELETE | `core/sitemaps/{id}/` | detail / cancel |
| GET | `core/sitemaps/{id}/status/` | status; query `prefetched` |
| GET | `core/sitemaps/{id}/graph/` · `/markdown/` | sitemap output formats |
| GET | `core/proxy-servers/list-all/` | available proxies |
| GET | `core/usage/` | usage report — **dashboard JWT only; 401 with API keys** |
| GET | `/api/v1/plan/subscriptions/current/` | plan credits/limits — **works with API keys** (`-1` = unlimited) |

> **There is no dedicated single-page `scrape` endpoint.** Scraping one page = `POST
> core/crawl-requests/` with `spider_options.page_limit = 1` (the SDK's `scrape_url` does
> exactly this, then waits on the SSE stream for the one result).

## Request options

`POST core/crawl-requests/` body — the `options` wrapper **must** contain both
`spider_options` and `page_options` keys (values may be `{}` to take defaults):

```json
{
  "url": "https://example.com",
  "options": {
    "spider_options": {},
    "page_options": {},
    "plugin_options": {}
  }
}
```

### page_options (content extraction)
| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `only_main_content` | bool | `true` | extract main content only |
| `include_html` | bool | `false` | adds `html` to the result |
| `include_links` | bool | `false` | adds `links` to the result |
| `exclude_tags` | string[] | `[]` | tags to strip |
| `include_tags` | string[] | `[]` | tags to keep |
| `wait_time` | int (ms) | `100` | wait before extraction (JS render) |
| `timeout` | int (ms) | `15000` | per-page timeout |
| `accept_cookies_selector` | string\|null | null | click selector to dismiss cookie banner |
| `locale` | string\|null | `en-US` | locale |
| `extra_headers` | object | — | headers sent to the target site |
| `actions` | Action[] | `[]` | `{"type":"screenshot"}` or `{"type":"pdf"}` → `attachments[]` |
| `ignore_rendering` | bool | `false` | skip JS rendering |

### spider_options (crawl scope)
| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `max_depth` | int | `1` | crawl depth |
| `page_limit` | int | `1` | max pages (set 1 for single-page scrape) |
| `concurrent_requests` | int (1–16) | `16` | concurrency |
| `allowed_domains` | string[] | `[]` | allowed domains (wildcards ok) |
| `include_paths` | string[] | `[]` | only-crawl path patterns |
| `exclude_paths` | string[] | `[]` | skip path patterns |
| `proxy_server` | string\|null | null | named proxy |

`plugin_options`: string map of per-plugin config (keys depend on installed plugins).

### search_options (POST `core/search/`)
- `query` (string, required, ≤255), `result_limit` (int 1–20, default 5).
- `search_options`: `language` (≤8, nullable), `country` (≤8, nullable),
  `search_type` (enum: `web`), `depth` (enum: `basic`|`advanced`|`ultimate`, default `basic`),
  **`time_renge`** (sic — enum: `any`|`day`|`week`|`month`|`year`, default `any`).

### sitemap_options (POST `core/sitemaps/`)
`url` + `options`: `include_subdomains` (default true), `ignore_sitemap_xml` (default false),
`search` (nullable), `include_paths`/`exclude_paths` (`[]`), `proxy_server`.

## Response shapes

- **Job (CrawlRequest):** `uuid`, `url`, `urls` (batch), `crawl_type` (`single`|`batch`),
  `status`, `options`, `created_at`, `updated_at`, `duration`, `number_of_documents`, `sitemap` (URI).
- **Page result (CrawlResult):** `uuid`, `url`, `result` (download URI by default; the page
  JSON when `prefetched=true`), `attachments[]` (`{uuid, attachment (URI), attachment_type:
  pdf|screenshot, filename}`), `created_at`, `updated_at`.
- **Result JSON keys** (when prefetched): `markdown` (always), `html` (if requested),
  `links` (if requested), `metadata` (e.g. `metadata.title`; full metadata schema lives in
  the external result file, not the OpenAPI spec).
- **Search result item:** `title`, `url`, `description`, `order`, `depth`.

## Raw curl examples

```bash
# scrape one page (async create → poll → fetch)
curl -X POST "$WATERCRAWL_BASE_URL/api/v1/core/crawl-requests/" \
  -H "X-API-Key: $WATERCRAWL_API_KEY" -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","options":{"spider_options":{"page_limit":1},"page_options":{"only_main_content":true},"plugin_options":{}}}'
# → {"uuid":"...","status":"new",...}

curl "$WATERCRAWL_BASE_URL/api/v1/core/crawl-requests/<uuid>/"            -H "X-API-Key: $WATERCRAWL_API_KEY"   # poll status
curl "$WATERCRAWL_BASE_URL/api/v1/core/crawl-requests/<uuid>/results/?prefetched=true" -H "X-API-Key: $WATERCRAWL_API_KEY"  # content

# crawl a site
curl -X POST "$WATERCRAWL_BASE_URL/api/v1/core/crawl-requests/" \
  -H "X-API-Key: $WATERCRAWL_API_KEY" -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","options":{"spider_options":{"max_depth":2,"page_limit":50,"allowed_domains":["example.com"]},"page_options":{},"plugin_options":{}}}'

# search
curl -X POST "$WATERCRAWL_BASE_URL/api/v1/core/search/" \
  -H "X-API-Key: $WATERCRAWL_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"self hosted crawler","result_limit":5,"search_options":{"depth":"basic"}}'
```

## Official SDKs

Reach for these only if a project already uses them; the standard-library helper covers the
common cases without an install.

**Python** — `pip install watercrawl-py` (Python ≥3.8):
```python
from watercrawl import WaterCrawlAPIClient
client = WaterCrawlAPIClient(api_key, base_url="https://watercrawl.example.com/")
result = client.scrape_url("https://example.com", sync=True, download=True)  # result["markdown"]
cr = client.create_crawl_request(url="...", spider_options={}, page_options={}, plugin_options={})
for ev in client.monitor_crawl_request(cr["uuid"]):
    if ev["type"] == "result": ...   # ev["data"]["markdown"]
```

**Node** — `npm install @watercrawl/nodejs` (Node ≥14):
```js
import { WaterCrawlAPIClient } from "@watercrawl/nodejs";
const client = new WaterCrawlAPIClient(apiKey, "https://watercrawl.example.com");
const result = await client.scrapeUrl("https://example.com");
```

Also available: PHP client, an n8n node (`@watercrawl/n8n-nodes-watercrawl`), and an MCP
server (`watercrawl-mcp`).

## Known issues / unverified

- **`time_renge` spelling** — the schema (and `TimeRengeEnum`) spell it `time_renge`; some
  SDK examples use `time_range`. The helper sends `time_renge`. If a freshness filter has no
  effect, try `time_range`.
- **`Authorization: Bearer` in docs** — dashboard JWT auth, not API-key auth. Use `X-API-Key`.
- **Host alias** — docs sometimes use `api.watercrawl.dev`; SDKs default to `app.watercrawl.dev`.
  Irrelevant for self-host (you set your own host).
- **`/download/` format** — described as ZIP in SDK docs but not typed in the schema.
- **Rate limits** — plan-based; no documented numeric limit or `X-RateLimit-*` headers.
- **Crawl-completion webhooks** — none in the API schema (only a Stripe billing webhook).
  Use SSE or polling for completion.
- **`search` needs a SERP provider** — returns `[]` when the instance has no search provider
  configured (verified on this self-host: the result JSON was empty). `scrape`/`crawl` unaffected.
- **`/core/usage/` is JWT-only** — 401 with API keys by design; use
  `/api/v1/plan/subscriptions/current/` for quota/credits (verified 200 with API key).
