"""One-off probe of the Eastmoney quote endpoints (run from CI, not local)."""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor

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
LIST_FIELDS = "f2,f3,f4,f5,f6,f9,f12,f13,f14,f15,f16,f17,f18,f20,f23,f37,f115"

SECIDS = ["1.688981", "105.INTC", "176.8035", "178.2330", "105.NVDA", "105.ASML"]


def main() -> None:
    session = requests.Session()
    session.headers.update(HEADERS)

    print("== single ==")
    for secid in SECIDS[:3]:
        try:
            r = session.get(QUOTE_URL, params={"secid": secid, "fltt": 2, "invt": 2, "fields": SINGLE_FIELDS}, timeout=15)
            print(secid, r.status_code, json.dumps((r.json() or {}).get("data"), ensure_ascii=False)[:300])
        except Exception as exc:
            print(secid, "ERR", type(exc).__name__)
        time.sleep(0.3)

    for fields, label in ((LIST_FIELDS, "list-fields"), (SINGLE_FIELDS, "single-fields")):
        print(f"== batch {label} ==")
        try:
            r = session.get(BATCH_URL, params={"fltt": 2, "invt": 2, "secids": ",".join(SECIDS), "fields": fields}, timeout=20)
            data = (r.json() or {}).get("data") or {}
            print(r.status_code, "total", data.get("total"))
            print(json.dumps(data.get("diff"), ensure_ascii=False)[:1200])
        except Exception as exc:
            print("ERR", type(exc).__name__, str(exc)[:120])
        time.sleep(1)

    print("== burst 40 single requests, 6 workers ==")
    secids = [s for s in SECIDS] * 7

    def fetch(secid):
        try:
            r = session.get(QUOTE_URL, params={"secid": secid, "fltt": 2, "invt": 2, "fields": SINGLE_FIELDS}, timeout=15)
            return bool((r.json() or {}).get("data"))
        except Exception:
            return False

    started = time.time()
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(fetch, secids))
    print(f"ok={sum(results)}/{len(results)} in {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()
