# 設定: Wix フォーム・保存先

## Wix

| 項目 | 値 |
|---|---|
| サイト | `Tokyoadvisory`（siteId `3b2ff17a-5e7f-4c62-929c-ff6f607a4454`） |
| フォームの namespace | `wix.form_app.form` |
| 通知メール | 差出人 `contact@tokyoadvisory.com` → `yamamoto@tokyoadvisory.com`、件名 `<フォーム名> got a new submission` |

### フォーム

| フォーム名 | formId | 保存先 |
|---|---|---|
| Personal information ／基本情報（個人） | `72e4e7bf-f93f-4734-86b8-db77900bdec1` | `<区分>/<氏名>/Basic` |
| Company information ／基本情報（法人） | 実行時に名前で特定する（下記） | `CORPORATION/<法人名>/Basic` |
| Company information ／基本情報（法人） copy | `68db2882-7e84-4d1b-8d0c-5b5fb4d387f8` | 同上（複製フォーム。こちらで回答が来ることもある） |
| アドバイザー登録フォーム | `5d083666-fffa-4887-97af-495b03af3495` | `GENERAL/Advisor/<氏名>` |

フォーム ID が分からないとき・変わったときは、List Forms
（`GET https://www.wixapis.com/form-schema-service/v4/forms?namespace=wix.form_app.form`、
docs: https://dev.wix.com/docs/api-reference/crm/forms/form-schemas/list-forms）で取得し、`name` で照合する。
応答が大きい（フォーム定義を全部含む）ので、ID と名前だけを抜き出して読む。
判明したらこの表を更新する。

### 使う API（いずれも `CallWixSiteAPI`、siteId は上記）

| 目的 | エンドポイント | docs |
|---|---|---|
| 回答の一覧 | `POST https://www.wixapis.com/form-submission-service/v4/submissions/namespace/query` body: `{"query":{"filter":{"formId":"<formId>","namespace":"wix.form_app.form"},"sort":[{"fieldName":"createdDate","order":"DESC"}],"cursorPaging":{"limit":10}}}` | https://dev.wix.com/docs/api-reference/crm/forms/form-submissions/query-submissions-by-namespace |
| 回答1件 | `GET https://www.wixapis.com/form-submission-service/v4/submissions/{submissionId}` | https://dev.wix.com/docs/api-reference/crm/forms/form-submissions/get-submission |
| 予約の検索 | `POST https://www.wixapis.com/_api/bookings-reader/v2/extended-bookings/query` | https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-reader-v2/query-extended-bookings |

- 回答の `submissions` はフィールドの `target`（例 `first_name`、`email_4f2a`）をキーにした値の集まり。
  PDF の項目名にはフォーム定義の `label`（英日併記のラベル）を使う。ラベルは Get Form / List Forms の
  `formFields[].inputOptions.*Options.label` にある。
- 予約検索のフィルタに使えるフィールドは限られる（docs の Supported Filters を読む）。
  日付で絞ってから、メールアドレス・氏名の照合はコード側で行う。日付は UTC で指定する。
- 呼び出す前に、docs で request body の形を確かめること（推測で body を作らない）。

## Dropbox

| 項目 | 値 |
|---|---|
| チームフォルダのルート | `/Cpa.mamiko チーム フォルダ`（ns_path `ns:15080112371//`） |
| 個人クライアント | `INDIVIDUAL/<氏名>`、米国申告は `USA/<氏名>`、相続は `INHERITANCE/<氏名>` |
| 法人クライアント | `CORPORATION/<法人名>` |
| アドバイザー | `GENERAL/Advisor/<氏名>`（例 `GENERAL/Advisor/Thomas Burns`、`GENERAL/Advisor/iwai`） |
| 基本情報 PDF | クライアントフォルダ直下の `Basic`（既存例 `INDIVIDUAL/Esposito/Basic/Personal information_Espasio Maria.pdf`） |
| ワークブック | クライアントフォルダ直下の `Workbook`（既存例 `INDIVIDUAL/Tony/Workbook/Andriotis_Tax_Workbook.xlsx`） |
| Email to Dropbox | アドレス・保存先 `Email Attachments` は `gmail-attachment-to-dropbox/references/config.md` を参照 |

## Gmail

| 項目 | 値 |
|---|---|
| 処理済みラベル | `Wix保存済` |
