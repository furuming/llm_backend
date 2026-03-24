from src.modules.chat.domain.entities import ChatMessage
from src.modules.chat.infrastructure.repository import ChatRepository
from src.shared.llm.factory import get_llm_client
from src.shared.kernel.id.generator import IDGenerator


class SendMessageUseCase:
    def __init__(self, repository: ChatRepository, id_generator: IDGenerator):
        """メッセージ保存先と ID 生成器を受け取って初期化する。"""
        self.repository = repository
        self.id_generator = id_generator
        

    def execute(self, user_id: str, message: str, model: str) -> str:
        """ユーザーメッセージを保存し、LLM 応答を生成して返す。"""
        user_message = ChatMessage(
            id=self.id_generator.generate(),
            user_id=user_id,
            role="user",
            model=model,
            content=message,
        )
        self.repository.save(user_message)
        llm = get_llm_client("local")

        reply = llm.generate(
            user_message=message,
            system_prompt="You are a helpful assistant. Answer in Japanese.",
        )

        assistant_message = ChatMessage(
            id=self.id_generator.generate(),
            user_id=user_id,
            role="assistant",
            model=model,
            content=reply,
        )
        self.repository.save(assistant_message)

        return reply