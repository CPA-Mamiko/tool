---
name: save-skill-to-dropbox
description: 作成・修正したスキルを .skill ファイルにまとめ、Dropbox のチームフォルダ `GENERAL/Claude/skills`（PC 上の C:\Users\cpama\Cpa.mamiko Dropbox\Cpa.mamiko チーム フォルダ\GENERAL\Claude\skills）に保存するスキル。スキルを新しく作ったとき・既存スキルを更新したときは、ユーザーに言われなくても最後にこのスキルで保存を提案する。「スキルを保存して」「skill を Dropbox に」「skills フォルダに入れて」「スキルをバックアップ」「.skill を保存」「save the skill」などと言われたら必ず使う。
---

# スキル → Dropbox `GENERAL/Claude/skills` に保存

スキルを作ったり直したりしたら、配布用の `.skill` ファイルにして、チームの共有フォルダに置いておく。
ほかの PC・メンバー・Claude 環境でも同じスキルを入れ直せるようにするためのバックアップ兼配布場所。

## 保存先

| 見え方 | パス |
|---|---|
| Windows（Dropbox デスクトップ） | `C:\Users\cpama\Cpa.mamiko Dropbox\Cpa.mamiko チーム フォルダ\GENERAL\Claude\skills` |
| Dropbox コネクタ（fq_path） | `/Cpa.mamiko チーム フォルダ/GENERAL/Claude/skills` |
| Dropbox コネクタ（ns_path） | `ns:15080112371//GENERAL/Claude/skills` |

- コネクタでは `/GENERAL/...` だけでは見つからない。必ず `/Cpa.mamiko チーム フォルダ/` から始めるか ns_path を使う。
- 既存ファイルは `<スキル名>.skill`（例: `meeting-follow-up.skill`、`client-personal-info.skill`）。同じ形式で揃える。

## 手順

### 1. 対象スキルを決める

- この会話で作成・修正したスキルがあればそれ。複数あれば全部を候補にする。
- ユーザーがスキル名を言った場合はそのフォルダ（`SKILL.md` がある場所）を探す。
  よくある場所: 作業中のフォルダ、`.claude/skills/<名前>/`、`~/.claude/skills/<名前>/`。
- スキル名は `SKILL.md` の frontmatter の `name`。ファイル名にはこれを使う。

### 2. `.skill` ファイルを作る

`.skill` は zip。中身は `<スキル名>/SKILL.md`、`<スキル名>/references/...` のようにスキルフォルダごと入れる。

skill-creator の `scripts/package_skill.py` が使えるならそれを使う（検証も兼ねる）:

```bash
python <skill-creator のパス>/scripts/package_skill.py <スキルフォルダ> <出力先フォルダ>
```

無ければ Python の zipfile で同じ形にする（`__pycache__`、`.DS_Store`、`*.pyc`、`evals/` は入れない）:

```bash
cd <スキルフォルダの親> && python -c "import zipfile,pathlib,sys; n=sys.argv[1]; z=zipfile.ZipFile(n+'.skill','w',zipfile.ZIP_DEFLATED); [z.write(p,p.as_posix()) for p in sorted(pathlib.Path(n).rglob('*')) if p.is_file() and not any(x in p.parts for x in ('__pycache__','.DS_Store')) and p.suffix!='.pyc' and p.parts[1:2]!=('evals',)]; z.close()" <スキル名>
```

作ったら `unzip -l <スキル名>.skill` で中身を確認する。

### 3. 保存方法を選ぶ

上から順に、使えるものを使う。

**A. Windows の Dropbox フォルダに直接書ける場合**（Claude デスクトップ／Cowork で PC のフォルダにアクセスできるとき）

- 保存先フォルダに `<スキル名>.skill` をコピーする。Dropbox アプリが自動で同期する。
- 同名ファイルがある場合は上書きしてよいか確認する（上書きしても Dropbox のバージョン履歴から戻せる）。

**B. Dropbox コネクタしか使えない場合**（クラウドのセッションなど）

Dropbox コネクタはバイナリ（zip）をアップロードできず、既存ファイルの上書きもできない。そのため:

1. `.skill` ファイルは `SendUserFile` でユーザーに渡し、「PC の上記フォルダに置いてください」と案内する。
2. あわせて、テキストのまま中身を残す: `skills/<スキル名>/` フォルダを `create_folder` で作り、
   `SKILL.md` と `references/`・`scripts/` 内のテキストファイルを同じ構成で `create_file` で保存する。
   - 画像・PDF・Excel などのバイナリは保存できないので、計画表に「手動で置く」と書く。
   - `skills/<スキル名>/` が既にある場合は上書きできないので、古いフォルダを
     `skills/_old/<スキル名>_<YYYYMMDD>` へ `move` してから新しく作る（`_old` が無ければ作る）。

### 4. 計画を見せて確認を取る（必須）

Dropbox への書き込み・移動の前に、次のような表を出して了承を得る:

| スキル | 保存方法 | 保存先 | 既存ファイル | 備考 |
|---|---|---|---|---|
| meeting-follow-up | A（直接コピー） | `GENERAL/Claude/skills/meeting-follow-up.skill` | あり → 上書き | |
| client-personal-info | B（コネクタ） | `GENERAL/Claude/skills/client-personal-info/` | なし | `assets/sign.png` は手動 |

既存ファイルの有無は `list_folder`（`path: ns:15080112371//GENERAL/Claude/skills`, `recursive: false`）で確認する。
了承が出るまで書き込まない。

### 5. 実行して報告する

- 保存後にもう一度 `list_folder` して、ファイル（またはフォルダ）ができていることを確かめる。
- 報告は短く: 保存したスキル名、保存先パス、手動で置く必要があるもの（B の場合の `.skill` ファイル・バイナリ）。

## 注意

- スキルの中にクライアントの個人情報（氏名・住所・SSN・マイナンバー等）が入っていないか、保存前に `SKILL.md` と references をざっと見る。
  入っていたら保存せずにユーザーに知らせる（チームフォルダは共有されるため）。
- 古い `.skill` を勝手に削除しない。整理はユーザーに言われたときだけ。
