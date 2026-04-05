# Alembic 運用ガイド

本プロジェクトでは、データベーススキーマ管理に **Alembic + SQLAlchemy 2.x** を使用する。

## 基本方針

- DB スキーマ変更は必ず Alembic を通す
- モデル変更だけでは DB は変わらない
- `--autogenerate` は補助機能なので必ずレビューする
- migration ファイル名は `YYYYMMDD_HHMMSS_slug.py` 形式で管理する
- 既存 revision を共有環境で書き換えない

## 技術スタック

- ORM: SQLAlchemy 2.x
- Migration: Alembic
- DB: MySQL（utf8mb4）

## 基本フロー

### 1. モデルを変更

```python
# 例: カラム追加
email: Mapped[str] = mapped_column(String(255), nullable=False)
```

### 2. Migration ファイル生成

```bash
uv run alembic revision --autogenerate -m "add chat table"
```

Alembic 設定により、生成ファイル名は自動で `YYYYMMDD_HHMMSS_slug.py` になる。

チェックポイント:

- 不要な変更が含まれていないか
- データ破壊が起きないか
- 制約やインデックスが正しいか

### 3. Migration 適用

```bash
uv run alembic upgrade head
```

## 命名ルール

- ファイル名: `YYYYMMDD_HHMMSS_slug.py`
- 例: `20260405_153045_add_projects_and_rooms_to_chat.py`
- 適用順はファイル名ではなく `revision` と `down_revision` で決まる
- `slug` は変更内容が分かる短い英語にする

## よく使うコマンド

- 最新まで適用

```bash
uv run alembic upgrade head
```

- 1つ前に戻す

```bash
uv run alembic downgrade -1
```

- 履歴確認

```bash
uv run alembic history
```

- 現在のバージョン確認

```bash
uv run alembic current
```

## 注意事項

### autogenerate は完全ではない

Alembic は差分の候補を出すだけなので、以下は誤検出や未検出がありえる。

- 制約変更
- default 値変更
- 型変更

必ず手動確認すること。

### データ破壊系操作に注意

NG 例:

```python
op.drop_column("users", "name")
```

データ消失につながる。

### NOT NULL 追加は慎重に

NG:

```python
op.add_column(... nullable=False)
```

既存データがあると失敗する。

OK パターン:

```python
op.add_column(... nullable=True)
```

その後にデータを埋めてから:

```python
op.alter_column(... nullable=False)
```

### 型変更は危険

`String -> Integer` のような変更はデータ破損リスクがある。

### Migration は履歴として扱う

- Git で管理する
- 原則として削除・上書きしない
- 順序を崩さない
- 共有済み migration は新しい revision を追加して変更する

## 開発フロー

1. モデル変更
2. `alembic revision --autogenerate`
3. Migration レビュー
4. `alembic upgrade head`
5. 動作確認

## 本番運用ルール

- 直接 DB 変更は禁止
- 必ず migration 経由で反映する
- 本番前に staging で検証する
- rollback 手順を事前に確認する

## トラブルシュート

### エラー: MetaData が見つからない

`target_metadata` が設定されていない可能性がある。

対処:

```python
target_metadata = Base.metadata
```

### エラー: モデルが反映されない

必要なモデルが Alembic 側で import されていない可能性がある。

対処:

```python
from core import models  # noqa: F401
```

### エラー: DB 接続できない

- `DATABASE_URL` を確認する
- MySQL の場合は必要ライブラリを確認する

```bash
uv add cryptography
```

## ベストプラクティスまとめ

- Migration は履歴
- autogenerate は補助
- DB 変更は慎重に
- 本番反映前に必ず検証する
