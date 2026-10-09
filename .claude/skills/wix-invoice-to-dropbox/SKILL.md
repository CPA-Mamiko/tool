---
name: wix-invoice-to-dropbox
description: Wix でダウンロードした請求書 PDF（`Invoice-0000240.pdf` のような番号だけのファイル名）を、関連するクライアントの Dropbox フォルダ（チームフォルダの INDIVIDUAL / CORPORATION / USA / INHERITANCE / AUDIT / COUNTERPART 配下）の `Invoice` フォルダへ、`Invoice-<クライアント名>_<日付>.pdf` という名前で保存するスキル。「請求書をダウンロードした」「Invoice を保存して」「請求書を Invoice フォルダに」「Wix の請求書を仕分けして」「インボイスをリネームして」「invoice to Dropbox」などと言われたら必ず使う。Wix で請求書を作成・送付したあと、ダウンロードした請求書をまとめて整理するときにも使う。
---

# Wix 請求書 → クライアントの Invoice フォルダ

Wix で請求書を発行してダウンロードすると、ファイル名は `Invoice-0000240.pdf` のように請求書番号だけになる。
これを該当クライアントの `Invoice` フォルダへ移し、`Invoice-<クライアント名>_<日付>.pdf` に名前を変える。

例: `Invoice-0000240.pdf` → `INHERITANCE/Bruce Deaner/Invoce/Invoice-Bruce Deaner_9Oct2026.pdf`

チームフォルダのルート: `/Cpa.mamiko チーム フォルダ`（以下のパスはここからの相対パス）

## 前提（重要）

- **Wix の請求書 API は使えない。** Tokyoadvisory のサイトは旧 Invoices のままで、新しい Invoices API は
  `428 INVOICES_API_UNAVAILABLE` を返す（2026-10-09 確認）。顧客名と日付は **PDF の本文から読む**。
  Wix 側が新 Invoices に移行したら、請求書番号で Query Invoices を呼び `customerInfo` と `issueDate` を使う方法に切り替えてよい。
- Dropbox コネクタはファイルをアップロードできない。PC の「ダウンロード」フォルダにだけある PDF は、
  Dropbox に入っていない限りクラウドからは見えない（下の「ファイルの探し方」を参照）。

## 1. ダウンロードした請求書を探す

次の順に探し、見つかったものを全部対象にする。ユーザーがファイルや顧客を指定したらそれに絞る。

1. **Dropbox 内の番号名ファイル:** Dropbox `search`
   （`query: "Invoice-0000"`, `search_mode: "title_only"`, `order_by: "last_modified"`, `max_results: 100`）。
   名前が `Invoice-<7桁の数字>.pdf`（`Invoice-0000240 (1).pdf` のような付番も含む）のものが対象。
   - 既定では **直近14日以内に更新されたもの**だけを対象にする（`last_modified_after`）。
     それより古い番号名ファイル（過去にそのまま置いた分）は、ユーザーが「過去分も」と言ったときだけ扱う。
   - `Invoice-ITO18May2026着手金請求書-0000158.pdf` のように既に名前が付いているものは対象外。
2. **ローカルの「ダウンロード」フォルダ（PC のファイルを扱える環境のときだけ）:**
   `~/Downloads`（Windows は `%USERPROFILE%\Downloads`）で `Invoice-*.pdf` を探す。
   移動先は Dropbox デスクトップアプリが同期しているローカルのチームフォルダ（例 `~/Dropbox (…)/Cpa.mamiko チーム フォルダ/…`）。
   同期フォルダの場所が分からないときはユーザーに聞く。推測したパスへは移さない。
3. どちらでも見つからず、クラウド環境で動いている場合は、
   「PC のダウンロードフォルダにある PDF はこちらから見えないので、Dropbox のどこか（例 `/Yamamoto Mamiko` 直下）に
   入れてください」と伝える。Chrome の「ダウンロード前に各ファイルの保存場所を確認する」をオンにすれば、
   ダウンロード時に Dropbox フォルダを選べることも案内する。

## 2. PDF から顧客名・日付を読む

Dropbox `fetch`（`id` は search が返した `id:…`）で本文を取り出し、次を読む:

| 項目 | 本文での場所 | 例 |
|---|---|---|
| 請求書番号 | `INVOICE #0000240` | 0000240 |
| 発行日 | `Issue Date: Oct 9, 2026` | 2026-10-09 |
| 顧客名 | `Bill to:` の次の行 | Bruce Deaner |
| 顧客メール | `Additional Customer Info:` の下 | bruce.deaner@… |
| 件名 | 明細表の直前の1行 | Retainer – Japanese Inheritance Tax Advisory … |

- 本文が空で返る PDF がある（古い Wix の PDF など）。その場合は Gmail で請求書番号
  （例 `"0000204"` や `"Invoice #0000204"`）を `search_threads` し、Wix から届いた送付メール・控えから顧客名と日付を拾う。
  それでも分からなければ「要確認」にする。推測で名前を付けない。

## 3. 保存先のクライアントフォルダと Invoice フォルダを決める

1. **クライアントフォルダ:** `gmail-attachment-to-dropbox` スキルの `references/client-map.md` に顧客メールがあればそれを使う。
   なければ顧客名で区分フォルダ（`INDIVIDUAL` / `CORPORATION` / `USA` / `INHERITANCE` / `AUDIT` / `COUNTERPART`）を
   `list_folder`（`recursive: false`）で一覧して照合する。フォルダ名が名だけ・姓だけ・会社名・日本語表記のこともある
   （例 `Tony`、`Heath`、`武井周彦`、`mocomoco株式会社`、`Peter_山中湖`）。PDF の宛名が法人名なら `CORPORATION` を優先。
   それでも分からなければ Dropbox `search`（`include_folders: true`）で名前検索する。
   候補が複数・見つからないときは **勝手に決めず** 「要確認」にする。
2. **Invoice フォルダ:** クライアントフォルダを `list_folder`（`recursive: false`）で開き、名前が `invoice` で始まる
   フォルダを大文字小文字を区別せずに探す。`Invoce` のような綴りの誤りもそのまま使う（名前は直さない）。
   `mount`（共有フォルダ）として出ることもある。
   - 無ければ `Invoice` を作る案を計画表に書き、了承を得てから `create_folder` で作る。
   - 年度フォルダ（`202608/` など）の下ではなく、クライアントフォルダ直下の Invoice フォルダを使う。

## 4. ファイル名を決める

```
Invoice-<クライアント名>_<日><月の英語3文字><年>.pdf
```

- **クライアント名:** 原則、Dropbox のクライアントフォルダ名（例 `Bruce Deaner`、`Aliatta`、`mocomoco株式会社`）。
  ファイル名に使えない `/ \ : * ? " < > |` は取り除く。`Tokidoki, LLC` のようなカンマはそのまま残してよい。
  ユーザーが短い呼び名（例 `Bruce`、`TE`、`MO`）を指定したらそれを使い、`references/name-map.md` への追記を提案する。
- **日付:** PDF の Issue Date（発行日）。ダウンロードした日ではない。日はゼロ埋めしない。
  月は `Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec`。例 `9Oct2026`、`28Jul2026`。
- 同じ顧客・同じ発行日の請求書が2通以上あるときは、2通目以降の末尾に請求書番号を付ける
  （例 `Invoice-Aliatta_1Aug2026-0000231.pdf`）。既に同名ファイルがあるときも同じ扱いにする。上書きはしない。

## 5. 計画を提示して了承を得る（必須）

移動・リネームの前に必ず次の表を示し、了承を得る。了承なしに移動しない。

```
| # | 元のファイル | 請求書番号・発行日・宛名 | 保存先 | 新しいファイル名 | 備考 |
|---|---|---|---|---|---|
| 1 | /Yamamoto Mamiko/Invoice-0000240.pdf | #0000240・2026-10-09・Bruce Deaner | INHERITANCE/Bruce Deaner/Invoce | Invoice-Bruce Deaner_9Oct2026.pdf | |
| 2 | …/Documents_Heath/Invoice-0000241.pdf | #0000241・2026-10-09・Heath … | INDIVIDUAL/Heath/Invoice | Invoice-Heath_9Oct2026.pdf | |
| 3 | /Yamamoto Mamiko/Invoice-0000242.pdf | #0000242・2026-10-10・（読めず） | 要確認 | — | PDF本文が空、Gmail でも見つからず |
```

## 6. 移動とリネーム

- Dropbox `move` で、`destination_path` を新しいファイル名まで含めたパスにして1回で移動＋リネームする
  （`autorename: false`。同名があれば手順4のとおり番号を付けて名前を変えてから移す）。
  パスは search / list_folder が返した `ns:…` 形式のフォルダパスを使い、手で組み立てない。
- `status: in_progress` が返ったら `check_job_status` で完了を確認する。
- `Invoice-0000240 (1).pdf` のような付番ファイルが、付番なしの方とサイズまで同じなら重複なので移さず、
  削除してよいかユーザーに確認する（勝手に消さない）。
- ローカルのダウンロードフォルダから移す場合は、ファイルを同期フォルダへ移動（またはコピー後に元を削除してよいか確認）する。

## 7. 結果を報告する

- 移したファイルごとに最終パス（`path_display`）を一覧で示す。
- 要確認・重複・見つからなかったものを分けて示す。
- 新しく判明した「顧客メール → クライアントフォルダ」の対応は
  `gmail-attachment-to-dropbox/references/client-map.md` への追記を提案する。

## 注意

- 請求書には口座情報や顧客の住所・電話番号が含まれる。報告や計画表には宛名・番号・日付・金額までを書き、
  住所・電話番号・口座番号は書き写さない。
- Wix からダウンロードした領収書（Receipt）や見積書（Price Quote）は対象外。ユーザーが指示したときだけ、
  同じ手順で `Receipt-…` / `Quote-…` という名前にして扱う。
