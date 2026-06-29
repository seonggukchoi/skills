#!/usr/bin/env python3
"""WaterCrawl API helper — scrape / crawl / search via a self-hosted (or cloud) WaterCrawl instance.

Why this exists: every WaterCrawl job is asynchronous (POST returns a uuid, then you
poll until it finishes and fetch the prefetched result). This wraps that loop so callers
get page content (markdown) in one command instead of re-implementing polling each time.

Config comes from the environment (override with flags):
  WATERCRAWL_BASE_URL   e.g. https://watercrawl.example.com   (no trailing /api/v1)
  WATERCRAWL_API_KEY    sent as the  X-API-Key  header

Standard library only — no `pip install` needed.

Examples:
  python watercrawl.py scrape https://example.com
  python watercrawl.py scrape https://example.com --html --screenshot --json
  python watercrawl.py crawl  https://example.com --max-depth 2 --page-limit 50
  python watercrawl.py search "watercrawl self host" --limit 5
  python watercrawl.py quota
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = "https://app.watercrawl.dev"
CORE = "/api/v1/core"


def _config(args):
    base = (args.base or os.environ.get("WATERCRAWL_BASE_URL") or DEFAULT_BASE).rstrip("/")
    key = args.api_key or os.environ.get("WATERCRAWL_API_KEY")
    if not key:
        sys.exit("error: WATERCRAWL_API_KEY is not set (export it or pass --api-key)")
    return base, key


def _request(method, path, key, base, body=None, query=None, timeout=60):
    """Return (status_code, parsed_json_or_text). Network failures exit the process."""
    url = base + path
    if query:
        # drop None values so callers can pass optional params freely
        query = {k: v for k, v in query.items() if v is not None}
        url += "?" + urllib.parse.urlencode(query)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-API-Key", key)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, (json.loads(raw) if raw.strip() else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except Exception:
            payload = raw
        return e.code, payload
    except urllib.error.URLError as e:
        sys.exit(f"error: cannot reach {base}: {e.reason}")


def _fail(status, payload):
    detail = json.dumps(payload, ensure_ascii=False) if isinstance(payload, (dict, list)) else str(payload)
    if status in (401, 403):
        detail += "\nhint: check WATERCRAWL_API_KEY — API keys use the X-API-Key header, not Bearer."
    sys.exit(f"error: HTTP {status}: {detail}")


def _poll(uuid, kind, key, base, interval, max_wait, quiet=False):
    """Poll the detail endpoint until the job leaves a non-terminal state.

    Returns the final job object. `kind` is 'crawl-requests' or 'search'.
    """
    deadline = time.time() + max_wait
    detail_path = f"{CORE}/{kind}/{uuid}/"
    last = None
    while True:
        code, payload = _request("GET", detail_path, key, base)
        if code != 200:
            _fail(code, payload)
        status = (payload or {}).get("status")
        if status != last and not quiet:
            print(f"  [{kind}] {uuid} status={status}", file=sys.stderr)
        last = status
        if status == "finished":
            return payload
        if status in ("failed", "canceled", "canceling"):
            sys.exit(f"error: job {uuid} ended with status={status}")
        if time.time() >= deadline:
            sys.exit(f"error: timed out after {max_wait}s waiting for {uuid} (last status={status})")
        time.sleep(interval)


def _build_page_options(args):
    """Translate CLI flags into the page_options object. Empty {} means server defaults."""
    po = {}
    if getattr(args, "no_main_content", False):
        po["only_main_content"] = False
    if getattr(args, "html", False):
        po["include_html"] = True
    if getattr(args, "links", False):
        po["include_links"] = True
    if getattr(args, "wait_time", None) is not None:
        po["wait_time"] = args.wait_time
    if getattr(args, "page_timeout", None) is not None:
        po["timeout"] = args.page_timeout
    if getattr(args, "exclude_tags", None):
        po["exclude_tags"] = args.exclude_tags
    if getattr(args, "include_tags", None):
        po["include_tags"] = args.include_tags
    actions = []
    if getattr(args, "screenshot", False):
        actions.append({"type": "screenshot"})
    if getattr(args, "pdf", False):
        actions.append({"type": "pdf"})
    if actions:
        po["actions"] = actions
    return po


def _crawl_results(uuid, key, base, max_pages=0):
    """Fetch page results with content inlined (prefetched=true), following pagination."""
    out = []
    path = f"{CORE}/crawl-requests/{uuid}/results/"
    page = 1
    while True:
        code, payload = _request("GET", path, key, base,
                                 query={"prefetched": "true", "page": page, "page_size": 50})
        if code != 200:
            _fail(code, payload)
        if isinstance(payload, dict):
            out.extend(payload.get("results", []))
            has_next = bool(payload.get("next"))
        else:  # some deployments may return a bare list
            out.extend(payload or [])
            has_next = False
        if max_pages and page >= max_pages:
            break
        if not has_next:
            break
        page += 1
    return out


def _result_markdown(item):
    """A crawl result's `result` field is the page JSON when prefetched, else a URL string."""
    content = item.get("result")
    if isinstance(content, dict):
        return content.get("markdown", "")
    return content or ""


def _emit_attachments(item):
    for att in item.get("attachments", []) or []:
        print(f"[attachment: {att.get('attachment_type')}] {att.get('attachment')}", file=sys.stderr)


def cmd_scrape(args):
    base, key = _config(args)
    body = {
        "url": args.url,
        "options": {
            "spider_options": {"page_limit": 1, "max_depth": 1},
            "page_options": _build_page_options(args),
            "plugin_options": {},
        },
    }
    code, payload = _request("POST", f"{CORE}/crawl-requests/", key, base, body=body)
    if code not in (200, 201):
        _fail(code, payload)
    uuid = payload.get("uuid")
    _poll(uuid, "crawl-requests", key, base, args.poll_interval, args.max_wait, args.quiet)
    results = _crawl_results(uuid, key, base, max_pages=1)
    if not results:
        sys.exit("error: job finished but returned no results")
    item = results[0]
    if args.json:
        print(json.dumps(item, ensure_ascii=False, indent=2))
    else:
        print(_result_markdown(item))
        _emit_attachments(item)


def cmd_crawl(args):
    base, key = _config(args)
    spider = {"max_depth": args.max_depth, "page_limit": args.page_limit}
    if args.concurrent is not None:
        spider["concurrent_requests"] = args.concurrent
    if args.allowed_domains:
        spider["allowed_domains"] = args.allowed_domains
    if args.include_paths:
        spider["include_paths"] = args.include_paths
    if args.exclude_paths:
        spider["exclude_paths"] = args.exclude_paths
    body = {
        "url": args.url,
        "options": {
            "spider_options": spider,
            "page_options": _build_page_options(args),
            "plugin_options": {},
        },
    }
    code, payload = _request("POST", f"{CORE}/crawl-requests/", key, base, body=body)
    if code not in (200, 201):
        _fail(code, payload)
    uuid = payload.get("uuid")
    if not args.quiet:
        print(f"  crawl request created: {uuid}", file=sys.stderr)
    _poll(uuid, "crawl-requests", key, base, args.poll_interval, args.max_wait, args.quiet)
    results = _crawl_results(uuid, key, base)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for item in results:
            print(f"# {item.get('url', '')}\n\n{_result_markdown(item)}\n\n---\n")
        if not args.quiet:
            print(f"  {len(results)} page(s) crawled", file=sys.stderr)


def cmd_search(args):
    base, key = _config(args)
    search_options = {}
    if args.depth:
        search_options["depth"] = args.depth
    if args.country:
        search_options["country"] = args.country
    if args.language:
        search_options["language"] = args.language
    if args.time_range:
        # NOTE: the API field is spelled "time_renge" (sic) in the OpenAPI schema.
        search_options["time_renge"] = args.time_range
    body = {"query": args.query, "result_limit": args.limit, "search_options": search_options}
    code, payload = _request("POST", f"{CORE}/search/", key, base, body=body)
    if code not in (200, 201):
        _fail(code, payload)
    uuid = payload.get("uuid")
    _poll(uuid, "search", key, base, args.poll_interval, args.max_wait, args.quiet)
    code, detail = _request("GET", f"{CORE}/search/{uuid}/", key, base, query={"prefetched": "true"})
    if code != 200:
        _fail(code, detail)
    result = detail.get("result") if isinstance(detail, dict) else None
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif isinstance(result, list):
        if not result and not args.quiet:
            print("  (0 results — check that a SERP provider is configured on the WaterCrawl instance)", file=sys.stderr)
        for r in result:
            print(f"{r.get('order', '?')}. {r.get('title', '')}\n   {r.get('url', '')}\n   {r.get('description', '')}\n")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_status(args):
    base, key = _config(args)
    code, payload = _request("GET", f"{CORE}/{args.kind}/{args.uuid}/", key, base)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(0 if code == 200 else 1)


def cmd_quota(args):
    # The /core/usage/ endpoint is JWT/dashboard-only (401 with an API key); the
    # plan subscription endpoint exposes credits/limits to API keys. A 200 here
    # also doubles as an auth/connectivity health check.
    base, key = _config(args)
    code, payload = _request("GET", "/api/v1/plan/subscriptions/current/", key, base)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(0 if code == 200 else 1)


def build_parser():
    p = argparse.ArgumentParser(description="WaterCrawl API helper (scrape/crawl/search).")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--base", help="base URL (default: $WATERCRAWL_BASE_URL)")
    common.add_argument("--api-key", help="API key (default: $WATERCRAWL_API_KEY)")
    common.add_argument("--poll-interval", type=float, default=2.0, help="seconds between status polls (default 2)")
    common.add_argument("--max-wait", type=float, default=300.0, help="max seconds to wait for a job (default 300)")
    common.add_argument("--json", action="store_true", help="emit raw JSON instead of markdown/text")
    common.add_argument("--quiet", action="store_true", help="suppress progress on stderr")

    page = argparse.ArgumentParser(add_help=False)
    page.add_argument("--no-main-content", action="store_true", help="keep full page, not just main content")
    page.add_argument("--html", action="store_true", help="include raw HTML in the result")
    page.add_argument("--links", action="store_true", help="include extracted links")
    page.add_argument("--screenshot", action="store_true", help="capture a screenshot (returned as an attachment)")
    page.add_argument("--pdf", action="store_true", help="capture a PDF (returned as an attachment)")
    page.add_argument("--wait-time", type=int, dest="wait_time", metavar="MS", help="ms to wait before extracting (JS render)")
    page.add_argument("--page-timeout", type=int, dest="page_timeout", metavar="MS", help="per-page timeout in ms")
    page.add_argument("--include-tags", nargs="+", dest="include_tags", metavar="TAG", help="HTML tags to keep")
    page.add_argument("--exclude-tags", nargs="+", dest="exclude_tags", metavar="TAG", help="HTML tags to drop")

    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("scrape", parents=[common, page], help="scrape a single page → markdown")
    sp.add_argument("url")
    sp.set_defaults(func=cmd_scrape)

    cp = sub.add_parser("crawl", parents=[common, page], help="crawl a site (multiple pages)")
    cp.add_argument("url")
    cp.add_argument("--max-depth", type=int, default=2, help="crawl depth (default 2)")
    cp.add_argument("--page-limit", type=int, default=20, help="max pages (default 20)")
    cp.add_argument("--concurrent", type=int, help="concurrent requests (1-16)")
    cp.add_argument("--allowed-domains", nargs="+", metavar="DOMAIN", help="domains allowed during crawl")
    cp.add_argument("--include-paths", nargs="+", metavar="PATTERN", help="only crawl matching paths")
    cp.add_argument("--exclude-paths", nargs="+", metavar="PATTERN", help="skip matching paths")
    cp.set_defaults(func=cmd_crawl)

    rp = sub.add_parser("search", parents=[common], help="web (SERP) search → results")
    rp.add_argument("query")
    rp.add_argument("--limit", type=int, default=5, help="result count 1-20 (default 5)")
    rp.add_argument("--depth", choices=["basic", "advanced", "ultimate"], help="search depth")
    rp.add_argument("--country", help="country code")
    rp.add_argument("--language", help="language code")
    rp.add_argument("--time-range", choices=["any", "day", "week", "month", "year"], help="freshness window")
    rp.set_defaults(func=cmd_search)

    stp = sub.add_parser("status", parents=[common], help="show a job's current state")
    stp.add_argument("uuid")
    stp.add_argument("--kind", choices=["crawl-requests", "search"], default="crawl-requests")
    stp.set_defaults(func=cmd_status)

    up = sub.add_parser("quota", parents=[common], help="show plan credits / limits (also a quick auth health check)")
    up.set_defaults(func=cmd_quota)

    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
