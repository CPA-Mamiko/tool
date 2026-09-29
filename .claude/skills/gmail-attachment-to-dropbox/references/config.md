# 設定: Email to Dropbox

| 項目 | 値 |
|---|---|
| Email to Dropbox アドレス | 未設定 |
| 添付の保存先フォルダ | `/Yamamoto Mamiko/Email Attachments`（初回転送後に実際のパスを確認して更新する） |

## アドレスの確認・有効化方法

1. ブラウザで Dropbox にログイン → 右上のアイコン → **設定**
2. **メール to Dropbox**（Email to Dropbox）を開く
3. 表示される `xxxx@dropbox.com` 形式のアドレスをコピーし、上の表に記入する
   （無効になっている場合はオンにする）

- このアドレスに届いたメールの添付は `Email Attachments` フォルダに保存される。
- 初回の転送後、Dropbox `search`（`query: "Email Attachments"`, `include_folders: true`）で
  実際のフォルダパスを確認し、上の「保存先フォルダ」を更新すること。
- アドレスを知っている人は誰でも Dropbox にファイルを送り込めるため、外部に共有しない。
