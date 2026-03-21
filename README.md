

###
##### domain
- 業務的な概念
- ChatMessage など
##### usecase
- 処理の流れを組み立てる
- 保存する
- LLM呼ぶ
- 必要なら結果も保存する
##### infrastructure
- SQLAlchemyモデル
- Repository実装
- 外部LLM接続
##### interface
- FastAPIのrouter
- HTTP入出力


###  処理のフロー

[HTTP Request]
   ↓
router (interface)
   ↓
usecase（アプリケーション層）
   ↓
domain（ロジック）
   ↓
infrastructure（LLM / DB）
   ↓
Response