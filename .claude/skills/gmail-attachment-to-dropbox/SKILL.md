---
name: gmail-attachment-to-dropbox
description: Gmail に届いたメールの添付資料や、Slack にアップロードされたファイルを、関連するクライアントの Dropbox フォルダ（チームフォルダの INDIVIDUAL / CORPORATION / USA / INHERITANCE / AUDIT 配下の Documents_ フォルダ）へ保存・移動するスキル。「添付を Dropbox に入れて」「メールの資料を保存して」「Slack のファイルを Dropbox に」「Slack Files を仕分けして」「添付資料を仕分けして」「Dropbox に移して」「送ってもらった書類を保存」「attachments to Dropbox」などと言われたら必ず使う。クライアントから資料が届いたとき、未保存の添付やSlackファイルをまとめて整理するとき、毎朝の受信整理にも使う。
---

# Gmail 添付資料・Slack ファイル → Dropbox 顧客フォルダ

クライアントがメールに添付してくれた資料や Slack にアップロードされたファイルを、Dropbox の該当クライアントフォルダへ保存する。

- **Gmail の添付** → 下の「仕組み」と「手順」（Email to Dropbox 経由）
- **Slack のファイル** → 末尾の「Slack のファイル」（転送は不要。Dropbox の `Slack Files` フォルダから移動するだけ）

保存先の決め方（手順2・3）と、計画の提示・確認（手順4）はどちらも共通。

## 仕組み（重要）

Dropbox コネクタはバイナリ（PDF・画像・Excel 等）をアップロードできず、Gmail コネクタも添付の中身を取り出せない。
そのため **Dropbox の「Email to Dropbox」機能** を経由する。

1. Gmail の `forward` で、メールを Email to Dropbox の専用アドレスへ転送する
2. Dropbox が添付を `Email Attachments` フォルダに自動保存する
3. Dropbox の `move` で、そのファイルを顧客フォルダへ移動する

専用アドレスと保存先フォルダは `references/config.md` に記載。
**未設定（`未設定` のまま）の場合は処理を始める前にユーザーにアドレスを尋ね**、設定方法（config.md 記載）を案内する。
推測したアドレスへは絶対に転送しない。
「動作確認」が `未検証` の場合は、最初の1通だけ転送して保存先フォルダに添付が届くかを確かめてから残りを処理する。
数分待っても届かなければ残りの転送は止め、アドレスが Email to Dropbox 用のものか（Dropbox の設定画面で表示される `@addtodropbox.com` のアドレスか）をユーザーに確認する。

## 手順

### 1. 対象メールを特定する

- ユーザーがメールを指定した場合はそれを使う（件名・差出人・日付で `search_threads`）。
- 指定がない場合は未処理の添付付きメールを探す:
  `has:attachment -from:me -label:Dropbox保存済 newer_than:14d`
- 各メールを `get_message`（`messageFormat: PLAIN_TEXT`）で開き、差出人・件名・本文・添付ファイル名/サイズを把握する。
- 次の添付は保存対象外として扱う（計画表には「対象外」と明記）:
  - 署名画像・インライン画像（`image001.png` 等、数十KB以下の画像）
  - `.ics`（招待状）、`winmail.dat`
  - こちら（東京アドバイザリー）が送った資料の返送・引用だけのもの

### 2. 関連するクライアントフォルダを決める

チームフォルダのルート: `/Cpa.mamiko チーム フォルダ`

| 区分 | フォルダ |
|---|---|
| 個人クライアント | `INDIVIDUAL/<氏名>` |
| 法人クライアント | `CORPORATION/<法人名>` |
| 米国申告 | `USA/<氏名>` |
| 相続 | `INHERITANCE/<氏名>` |
| 監査 | `AUDIT/<案件名>` |

判定の順序:

1. `references/client-map.md` に差出人のメールアドレス・ドメインがあればそれを使う。
2. なければ、差出人名・署名の会社名・件名・本文から候補名を拾い、上記の区分フォルダを
   `list_folder`（`recursive: false`）で一覧して照合する。表記ゆれ（姓名の順、ローマ字/カナ、
   「株式会社」「合同会社」の有無、大文字小文字）を考慮する。
3. それでも不明なら Dropbox `search`（`include_folders: true`）で名前を検索する。
4. 候補が複数・不明・新規クライアントの場合は **勝手に作らず**、計画表で「要確認」としてユーザーに選んでもらう。

### 3. 保存先を `Documents_<クライアント名>` に決める

クライアントから届いた資料は、**クライアントフォルダ内の `Documents_<クライアント名>` フォルダ**に入れる
（例: `INDIVIDUAL/Jason Hahn/Documents_Jason Hahn`、`CORPORATION/Aliatta/Documents_Jura Noire`）。

- クライアントフォルダを `list_folder`（`recursive: false`）で開き、名前が `Documents_` で始まるフォルダを探す
  （フォルダではなく共有フォルダ `mount` として表示されることもある）。
  名前の後半はフォルダ名と少し違う場合もある（例 `Documents_Jura Noire`、`Documets_Jeanette` のような綴りの誤り）ので、
  `Documents_` / `Documets_` で始まるものを1つ見つけたらそれを使う。
- `Documents_` フォルダの直下にファイルを入れる。中にサブフォルダがあっても、ユーザーの指示がなければ直下に入れる。
- `Documents_` フォルダが無い場合: `Documents_<クライアントフォルダ名>` を新しく作る案を計画表に書き、
  了承を得てから `create_folder` で作る。
- `Documents_` で始まるフォルダが2つ以上あり、どれか決められない場合は「要確認」にする。
- ファイル名は原則そのまま。重複時は `autorename: true` で Dropbox に連番を付けさせる（上書きしない）。

### 4. 計画を提示して確認を取る（必須）

移動前に必ず次の形で提示し、ユーザーの了承を得る。了承なしに転送・移動しない。

```
| # | メール（日付・差出人・件名） | 添付ファイル | 保存先 | 備考 |
|---|---|---|---|---|
| 1 | 9/28 Jason Hahn「W-2 送付」 | W-2_2025.pdf | INDIVIDUAL/Jason Hahn/Documents_Jason Hahn | |
| 2 | 9/28 Jason Hahn「W-2 送付」 | image001.png | — | 署名画像のため対象外 |
| 3 | 9/27 info@xxx.co.jp「決算資料」 | 試算表.xlsx | 要確認（候補: CORPORATION/A社, CORPORATION/B社） | |
```

マイナンバーカード・通知カードの画像など特に機微な資料が含まれる場合は、備考でその旨を明示する。

### 5. 転送して Email Attachments に保存させる

- 了承されたメールごとに Gmail `forward` で `references/config.md` のアドレスへ転送する（`forwardText` は空でよい）。
- 1通のメールに複数の添付があっても転送は1回。
- 数十秒〜数分後に、config.md の保存先フォルダを `list_folder`（`recursive: false`）で確認し、
  添付ファイル名と一致するファイルを探す（Dropbox が `ファイル名 (1).pdf` のように付番することがある）。
  まだ無ければ少し待って再確認する。数回確認しても現れなければ、そのメールは「未着」として報告し先に進む。
- **同じ添付が2組保存されることがある**（2組目は `ファイル名 (1).pdf` のように付番され、サイズも同じ）。
  付番のない方を移動し、`(1)` 付きの重複はサイズが同じことを確かめたうえで、削除してよいかユーザーに確認する。

### 6. 顧客フォルダへ移動する

- Dropbox `move` でまとめて移動（`autorename: true`）。`destination_path` はファイル名まで含める。
- `status: in_progress` が返ったら `check_job_status` で完了を確認する。
- 対象外にした添付（署名画像等）が Email Attachments に保存されていたら、そのままにせず
  ユーザーに削除してよいか確認する（勝手に消さない）。

### 7. Gmail に処理済みラベルを付ける

- ラベル `Dropbox保存済` が無ければ `create_label` で作成し、移動が完了したメールに `label_message` で付ける。
- 次回以降の検索（手順1の `-label:Dropbox保存済`）で重複処理を防ぐため。
- 転送により「送信済み」に Email to Dropbox 宛の転送メールが残るが、問題ない。

### 8. 結果を報告する

- 移動したファイルごとに最終パス（`path_display`）を一覧で示す。
- 未着・要確認・対象外のものを分けて示す。
- 新しく判明した「差出人 → フォルダ」の対応があれば、`references/client-map.md` への追記を提案する。

## Slack のファイル

Slack で共有されたファイルは、Slack と Dropbox の連携により **`/Yamamoto Mamiko/Slack Files`** に自動で保存されている。
Slack からファイルの中身を取り出して送り直す必要はない（`slack_read_file` の base64 をメールに載せる方法は、
ファイルが大きいと扱えないので使わない）。このフォルダから顧客フォルダへ `move` するだけでよい。

1. **対象を一覧する:** `Slack Files` を `list_folder`（`recursive: false`）で開く。
   移動済みのファイルはここから無くなるので、残っているものが未処理。ユーザーが期間やファイルを指定したらそれに絞る。
2. **どのクライアントのファイルか調べる:**
   - ファイル名にクライアント名が入っていればそれを手がかりにする（例 `Wangun_…` → `CORPORATION/Wangun`）。
   - 分からなければ Slack の `slack_search_public_and_private` でファイルを探し（`content_types: files`、
     ファイル名の特徴的な単語を `keywords` に。長い日本語名は一部の単語に分けて検索する）、
     投稿されたチャンネル名・DM の相手・投稿者から判断する。
   - クライアントフォルダの探し方と `Documents_` フォルダの決め方は手順2・3と同じ。
3. **対象外として扱うもの（計画表に「対象外」と書き、移動しない）:**
   - `image.png` / `image (12).png` のような画面のスクリーンショット（Slack に貼り付けた画像）。
     ユーザーが指定した場合だけ移動する。
   - こちら（東京アドバイザリー）が作ってSlackで共有した下書き・メモ類（例 `…_DRAFT.docx`、`…_税務検討メモ.docx`）。
     クライアントから届いた資料ではないので、`Documents_` には入れず「要確認」にする。
4. **`(1)` `(2)` 付きのファイル:** Slack では同じ名前の別の版が何度も共有されるので、Gmail の場合と違い
   **サイズが違えば別の版として両方移動する**。サイズまで同じものだけ重複候補として挙げ、削除はユーザーに確認する。
5. **計画を提示して了承を得る（手順4と同じ表。「メール」列の代わりに「Slack（日付・投稿者・チャンネル）」）。**
6. 了承後、手順6と同じく `move`（`autorename: true`）で移動し、手順8と同じ形で報告する。
   Gmail のようなラベル付けは不要（`Slack Files` に残っていないこと自体が処理済みの印になる）。

### アドバイザーの月報（決まった保存先）

アドバイザーが Slack で送ってくる月報（タイムチャージ表）は、クライアント資料ではないので `Documents_` には入れず、
下表のフォルダに入れる。依頼のたびに保存先を確認し直す必要はない（了承済みのルール）。

| 送り主（Slack 表示名） | ファイル名の例 | 保存先 |
|---|---|---|
| 井上雄貴（井上会計事務所、外部 Slack Connect） | `Mothly TimeCharge_2609井上.xlsx`（`YYMM` が対象月） | `GENERAL/Advisor/Inoue/invoice` |
| 吉見（社内） | `Yoshimi_Time_Charge_Aug_2026.pdf` | `GENERAL/Advisor/Yoshimi` |

- 送られてくる場所: 井上さんとの DM、または 吉見さん・井上さん・山本のグループ DM（2026年10月からはこちら）。
  同じ月の月報が両方に送られることがあるので、保存は1つだけにする（サイズが違えば新しい方）。
- 保存前に保存先フォルダを `list_folder` し、同じ月のファイルがすでにあれば重複保存しない。
- **井上さんは外部ユーザーのため、そのファイルは `Slack Files` に自動保存されず、`slack_read_file` でも
  `file_not_found` になる（2026-10-01 確認）。** そのため Claude からは取り込めない。次のどちらかで対応する:
  1. ユーザー（または吉見さん）が Slack からダウンロードして保存先フォルダへ入れる。
  2. 井上さんに Dropbox ファイルリクエストからアップロードしてもらう。
     作成済み（2026-10-01、期限なし）: タイトル「月報（Monthly TimeCharge）提出 - 井上」、
     保存先 `GENERAL/Advisor/Inoue/invoice`。リンクは `list_file_requests` で確認する。
- 吉見さんの月報も、同じ日に作ったファイルリクエスト「月報（Time Charge）提出 - 吉見」
  （保存先 `GENERAL/Advisor/Yoshimi`）から提出してもらう。
- 対応後、保存先フォルダに当月分があるかを確認して報告する。

## 注意

- Email to Dropbox はメールサイズに上限がある。大容量の添付や、Google Drive・WeTransfer 等の
  リンク共有の場合は保存されないため、「手動対応が必要」として報告する。
- パスワード付き ZIP・PDF はそのまま保存する（解凍・解除はしない）。パスワードが別メールで届いていても
  Dropbox には書き込まない。
- 識別情報の取扱いはチームフォルダの CLAUDE.md の三層方針に従う。
