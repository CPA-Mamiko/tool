---
name: gmail-attachment-to-dropbox
description: Gmail に届いたメールの添付資料を、関連するクライアントの Dropbox フォルダ（チームフォルダの INDIVIDUAL / CORPORATION / USA / INHERITANCE / AUDIT 配下）へ保存・移動するスキル。「添付を Dropbox に入れて」「メールの資料を保存して」「添付資料を仕分けして」「Dropbox に移して」「送ってもらった書類を保存」「attachments to Dropbox」などと言われたら必ず使う。クライアントから資料が届いたメールを処理するとき、未保存の添付をまとめて整理するとき、毎朝の受信整理にも使う。
---

# Gmail 添付資料 → Dropbox 顧客フォルダ

クライアントがメールに添付してくれた資料を、Dropbox の該当クライアントフォルダへ保存する。

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
数分待っても届かなければ残りの転送は止め、アドレスが Email to Dropbox 用のものか（Dropbox の設定画面で表示されるアドレスか）をユーザーに確認する。

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

## 注意

- Email to Dropbox はメールサイズに上限がある。大容量の添付や、Google Drive・WeTransfer 等の
  リンク共有の場合は保存されないため、「手動対応が必要」として報告する。
- パスワード付き ZIP・PDF はそのまま保存する（解凍・解除はしない）。パスワードが別メールで届いていても
  Dropbox には書き込まない。
- 識別情報の取扱いはチームフォルダの CLAUDE.md の三層方針に従う。
