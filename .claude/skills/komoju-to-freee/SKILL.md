---
name: komoju-to-freee
description: KOMOJU で決済された入金（クレジットカード・PayPay・銀行振込など）を KOMOJU の API から取得し、freee 会計（株式会社東京アドバイザリー）の「KOMOJU」口座の明細に取り込むスキル。「KOMOJU の明細を取り込んで」「komoju を freee に」「KOMOJU の入金を口座明細に」「決済データを freee に入れて」などと言われたら必ず使う。月次の記帳前にも使う。
---

# KOMOJU の決済 → freee「KOMOJU」口座の明細

## 設定

| 項目 | 値 |
|---|---|
| freee 事業所 | 株式会社東京アドバイザリー（company_id `180960`） |
| 取り込み先の口座 | `KOMOJU`（walletable_type `wallet`、walletable_id `6802773`） |
| KOMOJU の秘密鍵 | 環境変数 `KOMOJU_SECRET_KEY`（環境の設定で登録。チャットに貼ってもらわない） |
| ネットワーク | 環境の Network access で `komoju.com` を許可しておく |

freee の MCP は「現在の事業所」と違う company_id を受け付けないので、最初に `freee_set_current_company` で
`180960` に切り替える。作業が終わったら、元の事業所に戻す必要があるかユーザーに聞く。

## 明細の形（既存の取り込みに合わせる）

2026年4〜7月分は次の形で入っている。同じ形で入れる。

| 項目 | 値 |
|---|---|
| date | 決済日（`captured_at` を日本時間にした日付） |
| entry_side | 決済は `income`、返金は `expense` |
| amount | 決済額（税込・手数料差引前） |
| description | `<支払者名> (<支払方法>)`　例: `EMI SANO (visa)`、`Schummer Leah (paypay)`、`佐野 アミル (bank_transfer)` |

KOMOJU の手数料と、KOMOJU から銀行口座への振込（精算）は、このスキルでは取り込まない。
必要になったらユーザーと相談して追加する。

## 手順

### 1. どこまで取り込み済みか調べる

`freee_api_get` で `/api/1/wallet_txns`（`company_id: 180960, walletable_type: wallet, walletable_id: 6802773`）を取得し、
最新の明細の日付を確かめる。ユーザーが期間を指定しなければ「最新の日付」から今日までを対象にする
（最新の日付当日も含める。同じ日の決済が後から入っている場合があるため。重複は手順3で除く）。

### 2. KOMOJU から決済を取得する

```bash
python3 .claude/skills/komoju-to-freee/scripts/fetch_komoju.py --from <開始日> --to <終了日> > <scratchpad>/komoju_rows.json
```

- 初回、または出力の `description` が名前になっていないときは、`--debug` で1件目の生データを見て、
  スクリプトの `payer_name()` / `method()` が使う項目を直す（KOMOJU の項目名は API で確かめていない）。
- `skip` が付いた行（未完了・期限切れ・外貨など）は登録しないが、計画表に「対象外」として出す。
- `komoju.com` に接続できない（403）ときは、ネットワークの許可が無い。ユーザーに伝えて止まる。

### 3. 重複を除く

手順1で取得した既存の明細と、`date`・`amount`・`entry_side` が同じで、支払者名が同じ（大文字小文字・姓名の順を無視）
ものは「登録済み」として除く。

### 4. 計画を提示して確認を取る（必須）

```
| # | 日付 | 入/出 | 金額 | 摘要 | KOMOJU ID | 備考 |
|---|---|---|---|---|---|---|
| 1 | 2026-07-10 | 入金 | 33,000 | Jason Hahn (visa) | xxxxx | |
| 2 | 2026-07-12 | 入金 | 33,000 | Leah Schummer (paypay) | xxxxx | 登録済み（除外） |
```

合計件数と入金合計・返金合計も示す。了承を得てから登録する。

### 5. freee に登録する

了承された行ごとに `freee_api_post` で `/api/1/wallet_txns` に登録する。

```json
{
  "company_id": 180960,
  "walletable_type": "wallet",
  "walletable_id": 6802773,
  "entry_side": "income",
  "amount": 33000,
  "date": "2026-07-10",
  "description": "Jason Hahn (visa)"
}
```

エラーが出たらそこで止めてユーザーに伝える（続きを勝手に登録しない）。

### 6. 結果を報告する

登録した件数・金額合計、除外した行（登録済み・対象外）を報告する。登録した明細は freee の「自動で経理」に
未処理として並ぶので、取引の登録（売上の消込など）はユーザーが行うか、別途指示を受けてから行う。

## 既知の注意点

- 2026年4〜5月分には、同じ決済が2回入っているもの（`Tai Ito` と `Tai Ito (master)` など、支払方法の有無だけ違う組）がある。
  両方を取引登録すると売上が二重になる。見つけたらユーザーに伝える（勝手に削除しない）。
