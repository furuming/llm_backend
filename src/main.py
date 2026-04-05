from fastapi import FastAPI

from src.modules.chat.interface.router import router as chat_router
from src.modules.rag.api.rag_controller import router as rag_router

app = FastAPI(title='LLM Compare App')

app.include_router(chat_router)
app.include_router(rag_router)
