"""Minimal Google Health API v4 client for the ironman verifiers.

Google turned off the Fitbit Web API on 2026-10-30 (every call returns 410),
so hitpoints-verify and quest-verify read the Google Health API instead. The
access token comes from the harness's ``fitbit-mcp/bin/google-health-token``,
which owns the one token file and the one refresh path. This module never
refreshes anything itself.

Exit codes follow the old scripts: 2 when the token or the API is not usable,
so a watcher treats it as "try later", never as data.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

API = "https://health.googleapis.com/v4/users/me/dataTypes"
TOKEN_CMD = os.environ.get(
    "GOOGLE_HEALTH_TOKEN_CMD",
    os.path.expanduser("~/Documents/Exobrain harness/fitbit-mcp/bin/google-health-token"),
)
UA = "exobrain-harness/1.0 (+https://github.com/BaesTheorem/exobrain-harness)"


def token() -> str:
    try:
        out = subprocess.run([TOKEN_CMD], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"google-health-token failed: {e}", file=sys.stderr)
        sys.exit(2)
    if out.returncode != 0 or not out.stdout.strip():
        print(out.stderr.strip() or "google-health-token returned no token", file=sys.stderr)
        sys.exit(2)
    return out.stdout.strip()


def _call(tok: str, url: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": f"Bearer {tok}", "Accept": "application/json", "User-Agent": UA}
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        print(f"Google Health {e.code}: {e.read().decode(errors='replace')[:300]}", file=sys.stderr)
        sys.exit(2)
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"Google Health unreachable: {e}", file=sys.stderr)
        sys.exit(2)


def list_points(tok: str, data_type: str, flt: str, page_size: int | None = None) -> list[dict]:
    """Every data point that matches an AIP-160 filter, all pages."""
    out: list[dict] = []
    page = ""
    while True:
        q = {"filter": flt}
        if page_size:
            q["pageSize"] = str(page_size)
        if page:
            q["pageToken"] = page
        resp = _call(tok, f"{API}/{data_type}/dataPoints?{urllib.parse.urlencode(q)}")
        out.extend(resp.get("dataPoints", []))
        page = resp.get("nextPageToken", "")
        if not page:
            return out


def _civil(d: date) -> dict:
    return {"date": {"year": d.year, "month": d.month, "day": d.day}}


def daily_rollup(tok: str, data_type: str, start: date, end: date) -> list[dict]:
    """Daily roll-ups for civil dates start..end inclusive (one call holds up to 90 days)."""
    out: list[dict] = []
    chunk = start
    while chunk <= end:
        last = min(chunk + timedelta(days=89), end)
        page = ""
        while True:
            body = {"range": {"start": _civil(chunk), "end": _civil(last + timedelta(days=1))}, "windowSizeDays": 1, "pageSize": 90}
            if page:
                body["pageToken"] = page
            resp = _call(tok, f"{API}/{data_type}/dataPoints:dailyRollUp", body)
            out.extend(resp.get("rollupDataPoints", []))
            page = resp.get("nextPageToken", "")
            if not page:
                break
        chunk = last + timedelta(days=1)
    return out


def civil_date(d: dict) -> str:
    return f"{d['year']:04d}-{d['month']:02d}-{d['day']:02d}"


def seconds(s: str | None) -> float:
    """Google durations are strings such as '1285s'."""
    return float(str(s or "0s").rstrip("s") or 0)


def local_iso(utc: str, offset: str | None) -> str:
    """UTC timestamp plus a '-18000s' offset -> local wall-clock date string."""
    t = datetime.fromisoformat(utc.replace("Z", "+00:00")) + timedelta(seconds=seconds(offset))
    return t.strftime("%Y-%m-%d")
