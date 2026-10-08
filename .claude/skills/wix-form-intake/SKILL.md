---
name: wix-form-intake
description: Wix のフォーム（「Personal information／基本情報（個人）」「Company information／基本情報（法人）」「アドバイザー登録フォーム」）に回答が届いたら、回答内容を PDF にして Dropbox の保存先に入れるスキル。個人・法人はクライアントフォルダの Basic フォルダ（無ければ新しく作る）、アドバイザーは GENERAL/Advisor/<氏名> に保存する。そのクライアントにアポイントメント（Wix Bookings／Google カレンダーの面談予約）が入っていれば、面談に先立ってヒアリングメモと基本知識の解説を含むワークブック（.xlsx）を作り、クライアントフォルダの Workbook フォルダに保存する。「Wix にフォームが来た」「基本情報が届いた」「Company information が来た」「got a new submission」「フォームの PDF を保存して」「Basic に入れて」「アドバイザー登録が来た」「面談前のワークブックを作って」「ヒアリングメモを用意して」などと言われたら必ず使う。毎朝の受信整理で Wix の通知メールを見つけたときにも使う。
---

# Wix フォーム → Dropbox（Basic / Advisor）＋面談前ワークブック

Wix のフォームに回答が届いたときの一連の処理。

1. 回答内容を取得して PDF を作る
2. 保存先フォルダに入れる（無いフォルダは作る）
   - 個人・法人 → `<区分>/<クライアント名>/Basic`
   - アドバイザー → `GENERAL/Advisor/<氏名>`
3. アポイントメントがあれば、面談前のワークブックを `<区分>/<クライアント名>/Workbook` に保存する（個人・法人のみ）

設定値（サイト ID、フォーム ID、フォルダ）は `references/config.md`、
ワークブックの構成と書き方は `references/workbook-spec.md` にある。

## 仕組み（重要）

- Wix の通知メール（差出人 `contact@tokyoadvisory.com`、件名 `… got a new submission`）には **PDF は付いていない**。
  回答の中身は通知メール本文か、Wix の Form Submissions API で取る。
- Wix には回答を PDF で取り出す公開 API が無い。そのため **回答データから `scripts/submission_to_pdf.py` で PDF を作る**。
- Dropbox コネクタはバイナリ（PDF・xlsx）をアップロードできない。そのため次のどちらかで保存する:
  - **A. ローカルの Dropbox 同期フォルダに書ける場合**（デスクトップ版でチームフォルダが同期されているなど）:
    その場所に直接保存する。
  - **B. それ以外（通常）**: Email to Dropbox を経由する。
    Gmail `send_message` で、ファイルを添付したメールを Email to Dropbox のアドレスへ送り、
    Dropbox の `Email Attachments` に保存されたファイルを `move` で保存先へ移す。
    アドレスと `Email Attachments` の場所は `gmail-attachment-to-dropbox` スキルの `references/config.md` と同じものを使う。
    アドレスが未設定ならユーザーに尋ねる。推測したアドレスへは絶対に送らない。

## 手順

### 1. 新しい回答を見つける

- ユーザーが人や通知メールを指定したらそれを使う。
- 指定が無い場合は Gmail で未処理の通知を探す:
  `from:contact@tokyoadvisory.com subject:"got a new submission" -label:Wix保存済 newer_than:14d`
  - 件名のフォーム名で種類を判定する（`Personal information`、`Company information`、`アドバイザー登録フォーム`）。
    「Contact」「相談」「メッセージ」など、その他のフォームはこのスキルの対象外（問合せは `inquiry-intake` スキル）。
  - **同じ回答の通知が2〜3通届く**ことがある（同時刻・同内容）。氏名とメールアドレスが同じなら1件として扱う。
- 回答の全項目は Wix API で取る（通知メール本文は項目が省略されていることがある）。
  `references/config.md` のサイト ID・フォーム ID で Query Submissions By Namespace を呼び、
  `createdDate` が通知メールの時刻に近く、メールアドレスが一致する回答を選ぶ。
  API が使えないときは通知メール本文の「Submission summary」と、ユーザーに Wix のダッシュボードの回答画面を確認してもらう。
- 回答にファイル（パスポート、在留カード等）が添付されている場合は、PDF に「添付ファイルあり（ファイル名）」と書き、
  ファイル自体は Wix のダッシュボードから取るようユーザーに伝える（このスキルでは取りに行かない）。

### 2. 保存先を決める

チームフォルダのルート: `/Cpa.mamiko チーム フォルダ`

| フォーム | 保存先 | ファイル名 |
|---|---|---|
| Personal information／基本情報（個人） | `<INDIVIDUAL か USA か INHERITANCE>/<氏名>/Basic` | `Personal information_<氏名>.pdf` |
| Company information／基本情報（法人） | `CORPORATION/<法人名>/Basic` | `Company Information_<法人名>.pdf` |
| アドバイザー登録フォーム | `GENERAL/Advisor/<氏名>` | `Advisor information_<氏名>.pdf` |

クライアントフォルダの探し方:

1. 区分フォルダ（`INDIVIDUAL`、`USA`、`INHERITANCE`、`CORPORATION`、アドバイザーなら `GENERAL/Advisor`）を
   `list_folder`（`recursive: false`）で一覧し、氏名・法人名と照合する。
   表記ゆれ（姓だけ・名だけのフォルダ名 例 `Esposito`、`Tony`、`Nora`、ローマ字／カナ、大文字小文字、
   「株式会社」の有無）を考慮する。
2. 見つからなければ Dropbox `search`（`include_folders: true`）で氏名・メールアドレスのドメイン・会社名を検索する。
   Gmail で同じメールアドレスとのやり取りを探し、既存クライアントか、どの業務（米国申告・相続等）かを確かめる。
3. 個人の区分（INDIVIDUAL / USA / INHERITANCE）は、既存フォルダがあればそれに従う。新規の場合は、
   問合せ内容が米国税務中心なら `USA`、相続なら `INHERITANCE`、それ以外は `INDIVIDUAL` を提案する。
4. 候補が複数あって決められない場合は「要確認」にして、ユーザーに選んでもらう。

**フォルダが無い場合**は作る（`create_folder` は親から順に1階層ずつ）:

- クライアントフォルダはあるが `Basic` が無い → `<クライアントフォルダ>/Basic` を作る。
  `basic`（小文字）など綴り違いのフォルダが既にあればそれを使い、新しく作らない。
- クライアントフォルダ自体が無い（新規クライアント）→ フォルダ名を `<氏名>`（法人は `<法人名>`）として、
  クライアントフォルダ → `Basic` の順に作る。
- アドバイザーは `GENERAL/Advisor/<氏名>` が無ければ作る（中に `Basic` は作らない）。

### 3. アポイントメントを確認する（個人・法人のみ）

次のどれかで、回答者（法人なら担当者）の面談予定を探す。**今日以降**の予定だけを対象にする。

- Wix Bookings: Query Extended Bookings（`config.md` 参照）。`startDate` が今日以降のものを取り、
  回答のメールアドレス・氏名と `contactDetails` を照合する（照合はコード側で行う）。
- Google カレンダー: `search_events` を氏名・メールアドレスで検索する。
- Gmail: 自分が送った予約確認（件名 `Your consultation on …`、`Your online session …`、`ご相談の日程` 等）を
  回答者のアドレスで検索する。

見つかったら、日時（日本時間）・形式（Zoom／来社／電話）・サービス名を控える。
見つからなければワークブックは作らず、報告に「アポイントメントなし」と書く。

### 4. 計画を提示して確認を取る（必須）

作成・保存の前に次の形で示し、了承を得る。了承なしにフォルダ作成・送信・移動をしない。

```
| # | フォーム（受信日時） | 回答者 | 保存するファイル | 保存先 | フォルダ作成 | アポ |
|---|---|---|---|---|---|---|
| 1 | 個人 10/7 17:04 | John Smith | Personal information_John Smith.pdf | INDIVIDUAL/John Smith/Basic | Basic を新規作成 | 10/9 17:00 Zoom → ワークブック作成 |
| 2 | 法人 10/7 18:10 | Example KK | Company Information_Example KK.pdf | CORPORATION/Example KK/Basic | クライアントフォルダと Basic を新規作成 | なし |
| 3 | アドバイザー 10/8 9:00 | Taro Yamada | Advisor information_Taro Yamada.pdf | GENERAL/Advisor/Yamada | なし | — |
```

マイナンバー・SSN・パスポート番号など特に機微な項目を含む場合は、その旨を備考に書く。

### 5. PDF を作る

1. 回答を JSON にまとめる（`scripts/submission_to_pdf.py` の冒頭に形式あり）。
   項目名はフォームのラベルのまま（英日併記）、値は回答のまま。並びはフォームの順番。
2. 作業用ディレクトリで実行する:
   `python3 scripts/submission_to_pdf.py submission.json "Personal information_<氏名>.pdf"`
3. できた PDF を開いて（または `pdftotext` で）、全項目が載っていること・文字化けが無いことを確かめる。

### 6. 面談前ワークブックを作る（アポイントメントがある場合のみ）

`references/workbook-spec.md` に従って内容を組み立て、`scripts/build_workbook.py` で .xlsx にする。

- 材料: フォームの回答、問合せメール・これまでのやり取り（Gmail）、予約内容、
  クライアントフォルダ内の既存資料（`Documents_` の書類名、過去のメモ）。
- 報酬・必要資料・期限は `tokyo-advisory-services` スキル、会社・代表者の情報は `tokyo-advisory-profile` スキル、
  米国の信託・遺産なら `us-estate-trust-tax` スキルを読んで書く。記憶で数字を書かない。
- ファイル名: `<姓 or 法人名>_Prep_Workbook_<面談日 YYYYMMDD>.xlsx`
- 保存先: `<クライアントフォルダ>/Workbook`（無ければ作る）。

### 7. Dropbox に保存する

**A. ローカル同期フォルダがある場合**: 保存先に直接書き込む。

**B. Email to Dropbox 経由（通常）**:

1. Gmail `send_message` で Email to Dropbox のアドレス宛に送る。
   件名 `[Wix] <ファイル名>`、本文は空でよい。`attachments` に PDF（とワークブック）を base64 で添付する
   （PDF は `application/pdf`、xlsx は `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`）。
2. 1分ほどして `Email Attachments` を `list_folder`（`recursive: false`）で確認し、同じ名前のファイルを探す
   （`ファイル名 (1).pdf` のように付番されることがある）。
3. `move`（`autorename: true`）で保存先へ移す。`destination_path` はファイル名まで含める。
   `status: in_progress` なら `check_job_status` で完了を確かめる。
4. 同じファイルが2つ保存されていたら、付番の無い方を移し、もう一方はサイズが同じことを確かめてから
   削除してよいかユーザーに確認する。
5. 送信済みフォルダに Email to Dropbox 宛のメールが残るが問題ない。

### 8. 後処理と報告

- 処理した Wix の通知メール（重複分も含む）に Gmail ラベル `Wix保存済` を付ける（無ければ `create_label`）。
- 報告する内容:
  - 保存したファイルの最終パス（`path_display`）
  - 新しく作ったフォルダ
  - アポイントメントの有無と、作ったワークブックのパス・中身の概要（ヒアリング項目の数、扱った論点）
  - 要確認のもの、取りに行けなかった添付ファイル
- 個人の基本情報なら、続けて `client-personal-info` スキル（契約書・同意書の更新、2848・114a）を使うか尋ねる。
- 来社の面談なら `qr-code-request` スキル（入館QRコード）も案内する。

## 注意

- 回答内容（氏名・住所・生年月日・番号類）はメール本文やチャットに必要以上に書き出さない。
  計画表と報告には氏名と保存先だけを書く。
- Email to Dropbox のアドレスは公開リポジトリに書かない。
- 識別情報の取扱いはチームフォルダの CLAUDE.md の三層方針に従う。
- 既に Basic に同じ内容の PDF がある場合（前回処理済み）は作り直さず「保存済み」として報告する。
  内容が更新されている（再回答）場合は、日付を付けた別名（`…_<YYYYMMDD>.pdf`）で保存し、古い方は消さない。
