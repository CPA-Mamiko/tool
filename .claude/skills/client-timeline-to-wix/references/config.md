# 設定

## Wix サイト

| 項目 | 値 |
|---|---|
| サイト名 | Tokyoadvisory |
| siteId | `3b2ff17a-5e7f-4c62-929c-ff6f607a4454` |

（もう1つの `My Site 3` は使わない）

## 登録先スケジュール

| 項目 | 値 |
|---|---|
| スケジュール名 | 山本真美子（Wix Bookings のスタッフ・スケジュール） |
| scheduleId | `b24827a5-a131-4651-8341-b343c11c2616` |
| タイムゾーン | `Asia/Tokyo` |

予約サービス用のスケジュール（「来社によるご相談」「Tax」など）には入れない。
サービスのスケジュールに予定を作ると、そのサービスの予約枠として扱われるおそれがあるため。

他のスタッフ（吉見和子・熊谷和哉・Kanako Nakaminami・Naona Nagae）の担当案件で、
そのスタッフのカレンダーに入れたいとユーザーが言った場合だけ、`schedules/query` で
そのスタッフのスケジュール ID を調べて使う。

## API

| 用途 | エンドポイント | ドキュメント |
|---|---|---|
| 予定の作成 | `POST https://www.wixapis.com/calendar/v3/events` | https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/create-event |
| 予定の検索（重複確認） | `POST https://www.wixapis.com/calendar/v3/events/query` | https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/query-events |
| スケジュール一覧 | `POST https://www.wixapis.com/calendar/v3/schedules/query` | https://dev.wix.com/docs/api-reference/business-management/calendar/schedules-v3/query-schedules |

予定の変更・取消（Update Event / Cancel Event）は、使う前に
`SearchWixRESTDocumentation` でドキュメントを確認してからリクエストを組み立てる。

## 動作確認

- 予定の検索（読み取り）: 確認済み（2026-10-02）
- 予定の作成と、Wix ダッシュボードの予約カレンダーでの表示: 確認済み（2026-10-02、終日・TRANSPARENT の予定が山本真美子の終日欄に表示される）
