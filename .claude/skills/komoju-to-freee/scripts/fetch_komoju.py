#!/usr/bin/env python3
"""KOMOJU の決済を取得し、freee の口座明細（wallet_txns）に登録する候補を JSON で出力する。

使い方:
  python3 fetch_komoju.py --from 2026-07-04 --to 2026-10-02 > komoju_rows.json
  python3 fetch_komoju.py --from 2026-07-04 --to 2026-10-02 --debug   # 1件目の生データを表示

環境変数 KOMOJU_SECRET_KEY（KOMOJU の秘密鍵 sk_live_...）を読む。鍵は表示・保存しない。
"""
import argparse
import base64
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

API = "https://komoju.com/api/v1/payments"
JST = dt.timezone(dt.timedelta(hours=9))


def get(params, key):
    url = API + "?" + urllib.parse.urlencode(params)
    auth = base64.b64encode((key + ":").encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": "Basic " + auth, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def jst_date(iso):
    if not iso:
        return None
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return t.astimezone(JST).date().isoformat()


def payer_name(p):
    d = p.get("payment_details") or {}
    for v in (d.get("name"), d.get("family_name") and f"{d.get('family_name')} {d.get('given_name') or ''}".strip(),
              (p.get("metadata") or {}).get("name"), d.get("email"), p.get("customer")):
        if v:
            return str(v)
    return p.get("id", "")


def method(p):
    d = p.get("payment_details") or {}
    return d.get("brand") or d.get("type") or ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", required=True, help="開始日 YYYY-MM-DD（JST）")
    ap.add_argument("--to", dest="end", required=True, help="終了日 YYYY-MM-DD（JST、この日を含む）")
    ap.add_argument("--debug", action="store_true")
    a = ap.parse_args()

    key = os.environ.get("KOMOJU_SECRET_KEY")
    if not key:
        sys.exit("KOMOJU_SECRET_KEY が設定されていません")

    start = dt.datetime.fromisoformat(a.start).replace(tzinfo=JST)
    end = dt.datetime.fromisoformat(a.end).replace(tzinfo=JST) + dt.timedelta(days=1)
    params = {"start_time": start.isoformat(), "end_time": end.isoformat(), "per_page": 100}

    payments, page = [], 1
    while True:
        res = get(dict(params, page=page), key)
        data = res.get("data") or []
        payments += data
        if a.debug and data:
            print(json.dumps(data[0], ensure_ascii=False, indent=2))
            return
        if not res.get("has_more") and len(data) < params["per_page"]:
            break
        page += 1

    rows = []
    for p in payments:
        if (p.get("currency") or "JPY") != "JPY":
            rows.append({"komoju_id": p.get("id"), "skip": f"通貨 {p.get('currency')}"})
            continue
        name = payer_name(p)
        m = method(p)
        desc = f"{name} ({m})" if m else name
        status = p.get("status")
        if status in ("captured", "refunded") and p.get("captured_at"):
            rows.append({"komoju_id": p["id"], "date": jst_date(p["captured_at"]), "entry_side": "income",
                         "amount": int(p.get("total") or p.get("amount")), "description": desc, "status": status})
        for rf in p.get("refunds") or []:
            rows.append({"komoju_id": p["id"], "refund_id": rf.get("id"), "date": jst_date(rf.get("created_at")),
                         "entry_side": "expense", "amount": int(rf.get("amount")), "description": f"返金 {desc}",
                         "status": "refund"})
        if status not in ("captured", "refunded"):
            rows.append({"komoju_id": p.get("id"), "skip": f"status={status}", "description": desc,
                         "amount": p.get("total") or p.get("amount")})
    rows.sort(key=lambda r: (r.get("date") or "", r.get("komoju_id") or ""))
    json.dump(rows, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
