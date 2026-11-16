"""One-off probe of the Eastmoney quote endpoints (run from CI, not local)."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://quote.eastmoney.com/",
}
QUOTE_URL = "https://push2.eastmoney.com/api/qt/stock/get"
BATCH_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"
SINGLE_FIELDS = "f43,f44,f45,f46,f47,f48,f57,f58,f59,f60,f116,f164,f167,f168,f170,f173"
LIST_FIELDS = "f2,f3,f4,f5,f6,f8,f9,f12,f13,f14,f15,f16,f17,f18,f20,f23,f37,f115"


def main() -> None:
    session = requests.Session()
    session.headers.update(HEADERS)

    print("== single vs batch for the same symbols ==")
    samples = ["1.688981", "176.8035", "178.2330", "105.INTC"]
    single = {}
    for secid in samples:
        try:
            r = session.get(QUOTE_URL, params={"secid": secid, "fltt": 2, "invt": 2, "fields": SINGLE_FIELDS}, timeout=15)
            single[secid] = (r.json() or {}).get("data") or {}
        except Exception as exc:
            single[secid] = {"error": type(exc).__name__}
        time.sleep(0.3)
    print("single:", json.dumps(single, ensure_ascii=False))

    for size in (4, 60):
        symbols = json.loads(Path("data/symbols.json").read_text(encoding="utf-8")).get("symbols", {})
        secids = [record["secid"] for record in symbols.values() if isinstance(record, dict) and record.get("secid")][:size]
        if size == 4:
            secids = samples
        started = time.time()
        try:
            r = session.get(BATCH_URL, params={"fltt": 2, "invt": 2, "secids": ",".join(secids), "fields": LIST_FIELDS}, timeout=25)
            data = (r.json() or {}).get("data") or {}
            diff = data.get("diff") or []
            print(f"== batch size {size}: sent {len(secids)} returned {data.get('total')} in {time.time() - started:.1f}s")
            if size == 4:
                print(json.dumps(diff, ensure_ascii=False))
        except Exception as exc:
            print(f"batch size {size} ERR", type(exc).__name__, str(exc)[:120])
        time.sleep(1)


if __name__ == "__main__":
    main()
