# RAG Module

## 全体像

`src/modules/rag` は Retrieval-Augmented Generation を担うモジュールです。
既存の `chat` / `user` モジュールと同じく、依存の向きを内側へ向けた構成を採用し、外部サービスや Web API の都合を内側のユースケースへ漏らさないことを目的とします。

想定する処理フローは次の 2 系統です。

1. Indexing 系
   - アップロードされたファイルや入力テキストを受け取る
   - パースして生テキストへ正規化する
   - チャンクへ分割する
   - 埋め込みを生成する
   - ベクトルストアと永続層へ保存する
2. Retrieval 系
   - 問い合わせを受け取る
   - 問い合わせ文の埋め込みを生成する
   - ベクトルストアから関連チャンクを取得する
   - LLM に渡しやすい文脈へ整形する
   - 必要に応じて chat モジュールから利用する

## レイヤごとの責務

### models

RAG モジュール内で扱うデータ構造を表現します。
`Chunk`、`RawText`、`RetrievedChunk`、`UploadFile` など、ユースケースの入出力やリポジトリ間で受け渡す値を定義します。

責務:
- データの構造を表す
- ビジネスロジックに近い最小限の不変条件を持つ
- 外部 I/O やフレームワークへ依存しない

### repositories

ユースケースが必要とする永続化・検索の抽象境界を定義します。
実装詳細は持たず、インターフェースとして振る舞います。

責務:
- `RawTextRepository` で生テキスト保存を抽象化する
- `ChunkRepository` でチャンク保存を抽象化する
- `VectorStoreRepository` でベクトル検索を抽象化する

### services

ドメイン寄りの処理ルールを表現します。
単独では外部フレームワークに依存せず、ユースケースから組み合わせて使う前提です。

責務:
- `Parser` でファイルからテキストを抽出する
- `Chunker` でテキストをチャンクへ分割する
- `Embedder` で埋め込み生成を抽象化する
- `Retriever` で関連チャンク取得の振る舞いを定義する
- `PromptContextBuilder` で取得結果を LLM 向け文脈へ整形する

### usecases

アプリケーション固有の処理手順を定義します。
依存先は `models`、`repositories`、`services` に限定し、FastAPI や Qdrant などの具体実装には依存しません。

責務:
- `parse_attached_file.py` でアップロードファイルをテキスト化する
- `idex_document.py` でテキストの保存、分割、埋め込み、索引化を統括する
- `retrieve_chunks.py` で検索クエリから関連チャンクを取得する

補足:
- ファイル名 `idex_document.py` は既存名を維持していますが、実装時に違和感があれば `index_document.py` へのリネームを検討できます

### infrastructure

外部ライブラリ・外部サービスに依存する具体実装を配置します。
この層で `repositories` や `services` の抽象を実装し、上位層へ注入します。

責務:
- `liteparse_parser.py` でファイル解析ライブラリ連携を行う
- `embedding_gateway.py` で埋め込み API / モデル呼び出しを行う
- `qdrant_vector_store.py` でベクトルストア連携を行う
- `rag_query_service.py` で複数インフラをまとめる補助実装を置く

### api

HTTP 入出力の責務を持ちます。
FastAPI の router、request / response schema、依存解決をここに閉じ込め、ユースケースの呼び出しだけを行います。

責務:
- `rag_schema.py` で API 入出力スキーマを定義する
- `rag_controller.py` でエンドポイントを定義する
- HTTP 固有のバリデーションとレスポンス整形を行う

## 依存ルール

依存の向きは次の通りです。

`api -> usecases -> repositories/services/models`
`infrastructure -> repositories/services/models`

守りたいルール:
- `models` はどの外側層にも依存しない
- `usecases` は FastAPI、ORM、Qdrant、httpx などへ直接依存しない
- `api` は永続化や埋め込み生成の詳細を知らない
- `infrastructure` は具体実装を持つが、業務手順の決定はしない

## 実装方針

実装開始時は、既存ファイルを増やしすぎず、このディレクトリ配下の空ファイルを埋める形で進めます。
まずは最小構成として以下を目指します。

- ファイル入力を `RawText` に変換できる
- `RawText` を `Chunk` に分割できる
- クエリから `RetrievedChunk` を取得できる
- 将来 `chat` モジュールから文脈取得に再利用できる

## 初手の実装順

1. `models` と `repositories/services` の抽象を定義する
2. `usecases` に indexing / retrieval の流れを実装する
3. `infrastructure` に暫定実装を入れる
4. `api` を FastAPI に接続する
5. `main.py` から router を組み込む
