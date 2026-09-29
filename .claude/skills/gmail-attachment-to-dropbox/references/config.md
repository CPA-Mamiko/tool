# 設定: Email to Dropbox

| 項目 | 値 |
|---|---|
| Email to Dropbox アドレス | 未設定（公開リポジトリのため記載しない。claude.ai に登録するスキルにだけ記入する） |
| 動作確認 | 確認済（2026-09-29、転送後およそ1分で到着） |
| 添付の保存先フォルダ | `/Yamamoto Mamiko/Email Attachments`（確認済） |

## アドレスの確認・有効化方法

1. チーム管理者が 管理コンソール → 設定 → 製品と機能 → コンテンツ で **Email to Dropbox** をオンにする
2. ブラウザで Dropbox にログイン → 右上のアイコン → **設定** → 全般タブを下へスクロール → **メール to Dropbox** の「固有のメール アドレスを作成」
3. 表示される `xxxx@addtodropbox.com` 形式のアドレスをコピーし、上の表に記入する
   （無効になっている場合はオンにする）

- このアドレスに届いたメールの添付は `Email Attachments` フォルダに保存される。
- 初回の転送後、Dropbox `search`（`query: "Email Attachments"`, `include_folders: true`）で
  実際のフォルダパスを確認し、上の「保存先フォルダ」を更新すること。
- アドレスを知っている人は誰でも Dropbox にファイルを送り込めるため、外部に共有しない。
