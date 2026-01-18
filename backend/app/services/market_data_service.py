"""
Market data service for live NSE snapshots (configurable source)
"""
from __future__ import annotations

from typing import Dict, List, Optional
import csv
import io
import json
import re
import time

import httpx
try:
    from bs4 import BeautifulSoup
except Exception:  # pragma: no cover - optional dependency guard
    BeautifulSoup = None

from app.core.config import settings


class MarketDataService:
    """Fetch and format live market data from a configurable source."""

    def __init__(self):
        self._cache: List[Dict] = []
        self._cache_ts: float = 0.0

    async def get_market_snapshot(self, query: str) -> Optional[str]:
        """Return a compact market snapshot string tailored to the query."""
        rows = await self._get_market_data()
        if not rows:
            return None

        matched = self._match_rows(query, rows)
        timestamp = time.strftime("%Y-%m-%d %H:%M %Z")
        source_url = settings.nse_market_data_url or "configured source"
        has_ticker = any(r.get("ticker") for r in rows)
        has_price = any(r.get("price") for r in rows)
        index_like = sum(
            1 for r in rows if "index" in (r.get("name") or "").lower()
        )
        index_ratio = index_like / max(len(rows), 1)
        is_index_feed = not has_ticker and not has_price and index_ratio >= 0.5
        stats_like = sum(
            1
            for r in rows
            if any(
                keyword in (r.get("name") or "").lower()
                for keyword in ("total", "turnover", "volume", "traded")
            )
        )
        stats_ratio = stats_like / max(len(rows), 1)
        is_stats_feed = not has_ticker and not has_price and stats_ratio >= 0.5
        feed_note = ""
        if is_index_feed:
            feed_note = (
                "Note: this feed lists market indices/sector indices, "
                "not individual share prices."
            )
        if is_stats_feed and not feed_note:
            feed_note = (
                "Note: this feed provides market summary statistics, "
                "not individual share prices."
            )

        if matched:
            lines = [self._format_row(row) for row in matched]
            lines = [line for line in lines if line]
            if lines:
                return (
                    f"Live NSE market snapshot ({timestamp}, source: {source_url}). "
                    "Figures change throughout the day. "
                    + " ".join(lines)
                )

        mover_key = "change_pct"
        if not any(self._to_number(r.get("change_pct")) is not None for r in rows):
            mover_key = "change"
        if is_index_feed or is_stats_feed:
            gainers = []
            losers = []
        else:
            gainers = self._top_movers(rows, key=mover_key, reverse=True)
            losers = self._top_movers(rows, key=mover_key, reverse=False)

        gainers_text = "; ".join([self._format_row(r) for r in gainers if self._format_row(r)])
        losers_text = "; ".join([self._format_row(r) for r in losers if self._format_row(r)])

        return (
            f"Live NSE market snapshot ({timestamp}, source: {source_url}). "
            "Figures change throughout the day. "
            + (f"{feed_note} " if feed_note else "")
            + (f"Top gainers: {gainers_text}. " if gainers_text else "")
            + (f"Top losers: {losers_text}." if losers_text else "")
        ).strip()

    async def _get_market_data(self) -> List[Dict]:
        url = settings.nse_market_data_url
        if not url:
            return []

        ttl = settings.nse_market_cache_ttl_seconds
        if self._cache and (time.time() - self._cache_ts) < ttl:
            return self._cache

        categories = []
        if settings.nse_market_category:
            categories = [
                c.strip() for c in settings.nse_market_category.split(",") if c.strip()
            ]

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                data = []
                if "nse.co.ke/dataservices/market-statistics" in url and categories:
                    for category in categories:
                        response = await client.get(url, params={"category": category})
                        response.raise_for_status()
                        content_type = response.headers.get("content-type", "")
                        data.extend(self._parse_response(response.text, content_type))
                else:
                    response = await client.get(url)
                    response.raise_for_status()
                    content_type = response.headers.get("content-type", "")
                    data = self._parse_response(response.text, content_type)
        except Exception:
            return self._cache if self._cache else []

        self._cache = data
        self._cache_ts = time.time()
        return data

    def _parse_response(self, text: str, content_type: str) -> List[Dict]:
        text = text.strip()
        if "json" in content_type or text.startswith("{") or text.startswith("["):
            return self._parse_json(text)
        if "html" in content_type or "<table" in text.lower():
            return self._parse_html(text)
        return self._parse_csv(text)

    def _parse_json(self, text: str) -> List[Dict]:
        try:
            parsed = json.loads(text)
        except Exception:
            return []

        if isinstance(parsed, dict):
            for key in ("data", "results", "items"):
                if isinstance(parsed.get(key), list):
                    return [self._normalize_row(r) for r in parsed[key] if isinstance(r, dict)]
            return []
        if isinstance(parsed, list):
            return [self._normalize_row(r) for r in parsed if isinstance(r, dict)]
        return []

    def _parse_csv(self, text: str) -> List[Dict]:
        reader = csv.DictReader(io.StringIO(text))
        return [self._normalize_row(row) for row in reader if row]

    def _parse_html(self, text: str) -> List[Dict]:
        if BeautifulSoup is None:
            return []
        soup = BeautifulSoup(text, "html.parser")
        table = soup.find("table")
        if not table:
            return []

        headers = []
        thead = table.find("thead")
        if thead:
            headers = [th.get_text(strip=True).lower() for th in thead.find_all("th")]
        if not headers:
            first_row = table.find("tr")
            if first_row:
                headers = [th.get_text(strip=True).lower() for th in first_row.find_all(["th", "td"])]

        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if not cells:
                continue
            row = {}
            for idx, value in enumerate(cells):
                key = headers[idx] if idx < len(headers) and headers[idx] else f"col_{idx}"
                row[key] = value
            rows.append(self._normalize_row(row))
        return rows

    def _normalize_row(self, row: Dict) -> Dict:
        def pick(*keys: str) -> Optional[str]:
            for key in keys:
                val = row.get(key)
                if val is not None and str(val).strip() != "":
                    return str(val).strip()
            return None

        return {
            "ticker": pick("ticker", "symbol", "code", "security", "share"),
            "name": pick("name", "company", "issuer", "security name"),
            "price": pick("last", "last_price", "price", "close", "close_price"),
            "change": pick("change", "chg", "net change", "net_change"),
            "change_pct": pick("change_pct", "pct_change", "percent_change", "% change", "percent", "change %"),
            "volume": pick("volume", "vol", "turnover", "traded volume"),
        }

    def _match_rows(self, query: str, rows: List[Dict]) -> List[Dict]:
        tokens = re.findall(r"[A-Za-z]{2,6}", query.upper())
        tickers = {(r.get("ticker") or "").upper() for r in rows if r.get("ticker")}
        matched = [r for r in rows if (r.get("ticker") or "").upper() in tokens]
        if matched:
            return matched

        # fallback: match company names in query
        query_lower = query.lower()
        for r in rows:
            name = (r.get("name") or "").lower()
            if name and name in query_lower:
                matched.append(r)
        return matched

    def _top_movers(self, rows: List[Dict], key: str, reverse: bool) -> List[Dict]:
        def score(row: Dict) -> float:
            raw = row.get(key)
            if raw is None:
                return float("-inf") if reverse else float("inf")
            number = self._to_number(raw)
            if number is None:
                return float("-inf") if reverse else float("inf")
            return number

        sorted_rows = sorted(rows, key=score, reverse=reverse)
        return sorted_rows[:5]

    def _to_number(self, value: Optional[str]) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(str(value).replace("%", "").replace(",", "").strip())
        except Exception:
            return None

    def _format_row(self, row: Dict) -> Optional[str]:
        ticker = row.get("ticker")
        name = row.get("name")
        price = row.get("price")
        change = row.get("change")
        change_pct = row.get("change_pct")
        volume = row.get("volume")

        if not ticker and not name:
            return None

        parts = []
        label = ticker or name
        if ticker and name:
            label = f"{ticker} ({name})"
        parts.append(label)
        if price:
            parts.append(f"KSh {price}")
        if change or change_pct:
            change_text = change or ""
            pct_text = f"{change_pct}%" if change_pct and "%" not in str(change_pct) else str(change_pct or "")
            if change_text and pct_text:
                parts.append(f"change {change_text} ({pct_text})")
            elif change_text:
                parts.append(f"change {change_text}")
            elif pct_text:
                parts.append(f"change {pct_text}")
        if volume:
            parts.append(f"vol {volume}")

        return ", ".join(parts)


market_data_service = MarketDataService()
