# Alembic 運用ガイド

本プロジェクトでは、データベーススキーマ管理に **Alembic + SQLAlchemy 2.x** を使用する。

---

## 🧠 基本方針

- DBスキーマ変更は **必ず Alembic を通す**
- モデル変更だけでは DB は変わらない
- `--autogenerate` は補助機能（必ずレビューする）

---

## 📦 技術スタック

- ORM: SQLAlchemy 2.x
- Migration: Alembic
- DB: MySQL（utf8mb4）

---

## 🚀 基本フロー

### 1. モデルを変更

```python
# 例: カラム追加
email: Mapped[str] = mapped_column(String(255), nullable=False)
```

### 2. Migrationファイル生成
```bash
uv run alembic revision --autogenerate -m "add email to users"
```

### 3. Migrationファイル生成
```bash
uv run alembic revision --autogenerate -m "add email to users"
```
チェックポイント
不要な変更が含まれていないか
データ破壊が起きないか
制約やインデックスが正しいか

### 4. Migration適用
```bash
uv run alembic upgrade head
```


## 🔄 よく使うコマンド
- 最新まで適用
```
uv run alembic upgrade head
```
- 1つ前に戻す
```
uv run alembic downgrade -1
```
- 履歴確認
```
uv run alembic history
```
- 現在のバージョン確認
```
uv run alembic current
```

## ⚠️ 注意事項（重要）
1. autogenerateは完全ではない
Alembicは差分の「候補」を出すだけ：
- 制約変更
- default値変更
- 型変更
などは誤検出・未検出あり
👉 必ず手動確認すること
1. データ破壊系操作に注意
NG例
```
op.drop_column("users", "name")
```
👉 データ消失
1. NOT NULL追加は慎重に
NG
```
op.add_column(... nullable=False)
```
👉 既存データで失敗
OKパターン
# Step1: nullableで追加
```
op.add_column(... nullable=True)
```

# Step2: データ埋める（手動 or migration）

# Step3: NOT NULL化
```
op.alter_column(... nullable=False)
```
4. 型変更は危険
String → Integer
👉 データ破損リスク
5. Migrationは履歴として扱う

#### Gitで管理
- 削除・上書きしない（原則）
- 順序を崩さない

#### 🧩 命名ルール
- Migrationファイルは以下の形式を推奨：
add_email_to_users
create_users_table
add_index_to_orders
#### 🧪 開発フロー
1. モデル変更
2. alembic revision --autogenerate
3. Migrationレビュー
4. alembic upgrade head
5. 動作確認
#### 🏗 本番運用ルール
直接DB変更禁止
必ずMigration経由
本番前に staging で検証
rollback（downgrade）手順を確認
#### 🛠 トラブルシュート
エラー: MetaData が見つからない
target_metadata が設定されていない
対処：
target_metadata = Base.metadata
エラー: モデルが反映されない
原因：
モデルが import されていない
対処：
from infrastructure.db.models.user_model import UserModel  # noqa: F401
エラー: DB接続できない
DATABASE_URL確認
cryptographyインストール（MySQLの場合）
uv add cryptography
#### 🧠 ベストプラクティスまとめ
Migrationは「履歴」
autogenerateは「補助」
DB変更は「慎重に」
本番は「必ず検証」

