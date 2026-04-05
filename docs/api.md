# Chat API

このドキュメントは、現在の chat 機能で利用できる API をまとめたもの。

## 概要

chat 機能は以下の階層で構成される。

- project: チャットルーム群をまとめる上位概念
- room: 実際の会話のまとまり
- message: room に紐づくチャットメッセージ

階層イメージ:

```text
project
└── room
    ├── user message
    └── assistant message
```

ベースパス:

```text
/chat
```

## エンドポイント一覧

| Method | Path | 説明 |
| --- | --- | --- |
| POST | `/chat/projects` | project を作成する |
| GET | `/chat/projects` | user に紐づく project 一覧を取得する |
| POST | `/chat/rooms` | project 配下に room を作成する |
| GET | `/chat/rooms` | project 配下の room 一覧を取得する |
| GET | `/chat/rooms/{room_id}/messages` | room のメッセージ履歴を取得する |
| POST | `/chat` | メッセージを送信し、LLM の応答を取得する |

## 1. Project 作成

`POST /chat/projects`

### Request Body

```json
{
  "user_id": "user_001",
  "name": "新規プロダクト立ち上げ",
  "description": "要件整理と会話ログをまとめるプロジェクト"
}
```

### バリデーション

- `user_id`: 必須
- `name`: 必須、1 文字以上 255 文字以下
- `description`: 任意

### Response

```json
{
  "id": "01JQEXAMPLEPROJECT00000001",
  "user_id": "user_001",
  "name": "新規プロダクト立ち上げ",
  "description": "要件整理と会話ログをまとめるプロジェクト",
  "created_at": "2026-04-05T00:00:00"
}
```

## 2. Project 一覧取得

`GET /chat/projects?user_id={user_id}`

### Query Parameters

- `user_id`: 必須

### Response

```json
[
  {
    "id": "01JQEXAMPLEPROJECT00000001",
    "user_id": "user_001",
    "name": "新規プロダクト立ち上げ",
    "description": "要件整理と会話ログをまとめるプロジェクト",
    "created_at": "2026-04-05T00:00:00"
  }
]
```

## 3. Room 作成

`POST /chat/rooms`

### Request Body

```json
{
  "user_id": "user_001",
  "project_id": "01JQEXAMPLEPROJECT00000001",
  "name": "要件定義"
}
```

### バリデーション

- `user_id`: 必須
- `project_id`: 必須
- `name`: 必須、1 文字以上 255 文字以下

### 挙動

- `project_id` に対応する project が存在しない場合は `404 Project not found`
- project の `user_id` と request の `user_id` が一致しない場合は `400 Project does not belong to the user`

### Response

```json
{
  "id": "01JQEXAMPLEROOM00000000001",
  "project_id": "01JQEXAMPLEPROJECT00000001",
  "user_id": "user_001",
  "name": "要件定義",
  "created_at": "2026-04-05T00:10:00"
}
```

## 4. Room 一覧取得

`GET /chat/rooms?project_id={project_id}`

### Query Parameters

- `project_id`: 必須

### Response

```json
[
  {
    "id": "01JQEXAMPLEROOM00000000001",
    "project_id": "01JQEXAMPLEPROJECT00000001",
    "user_id": "user_001",
    "name": "要件定義",
    "created_at": "2026-04-05T00:10:00"
  }
]
```

## 5. Room メッセージ履歴取得

`GET /chat/rooms/{room_id}/messages`

### Path Parameters

- `room_id`: 必須

### Query Parameters

- `limit`: 任意、デフォルト `50`、最小 `1`、最大 `200`

### 挙動

- room が存在しない場合は `404 Room not found`
- 返却順は古いメッセージから新しいメッセージの順

### Response

```json
[
  {
    "id": "01JQEXAMPLEMSG000000000001",
    "user_id": "user_001",
    "room_id": "01JQEXAMPLEROOM00000000001",
    "role": "user",
    "content": "要件定義の叩き台を作って",
    "model": "gpt-4o-mini",
    "created_at": "2026-04-05T00:11:00"
  },
  {
    "id": "01JQEXAMPLEMSG000000000002",
    "user_id": "user_001",
    "room_id": "01JQEXAMPLEROOM00000000001",
    "role": "assistant",
    "content": "まず目的、対象ユーザー、主要機能の3点から整理します。",
    "model": "gpt-4o-mini",
    "created_at": "2026-04-05T00:11:02"
  }
]
```

## 6. Chat 送信

`POST /chat`

### Request Body

```json
{
  "user_id": "user_001",
  "room_id": "01JQEXAMPLEROOM00000000001",
  "message": "要件定義の論点を5つに整理して",
  "model": "gpt-4o-mini",
  "use_rag": true,
  "rag_top_k": 5
}
```

### バリデーション

- `user_id`: 必須
- `room_id`: 任意
- `message`: 必須
- `model`: 必須
- `use_rag`: 任意
- `rag_top_k`: 任意、1 以上 20 以下

### 挙動

- `room_id` を指定しない場合、メッセージは room 非紐づきで保存される
- `room_id` を指定した場合、その room の所有者チェックを行う
- room が存在しない場合は `404 Room not found`
- room の `user_id` と request の `user_id` が一致しない場合は `400 Room does not belong to the user`
- `use_rag` 未指定時はアプリ設定のデフォルト値を利用する
- `rag_top_k` 未指定時はアプリ設定のデフォルト値を利用する
- user message と assistant message の 2 件が保存される

### Response

```json
{
  "response": "要件定義の論点は、目的、対象ユーザー、主要ユースケース、制約条件、成功指標の5つです。",
  "used_rag": true,
  "retrieved_chunk_count": 3,
  "room_id": "01JQEXAMPLEROOM00000000001"
}
```

## エラーレスポンス例

### Project が存在しない

```json
{
  "detail": "Project not found"
}
```

### Room が存在しない

```json
{
  "detail": "Room not found"
}
```

### user_id が所有者と一致しない

```json
{
  "detail": "Room does not belong to the user"
}
```

## 推奨利用フロー

1. `POST /chat/projects` で project を作成する
2. `POST /chat/rooms` で project 配下に room を作成する
3. `POST /chat` に `room_id` を付けて会話する
4. `GET /chat/rooms/{room_id}/messages` で会話履歴を取得する

## 備考

- ID は ULID 形式を想定
- `created_at` はサーバー側で設定される
- message の `role` は現在 `user` または `assistant` を返す
