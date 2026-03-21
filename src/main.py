from fastapi import FastAPI

from src.core.db import Base, engine
from src.core import models  # noqa: F401
from src.modules.chat.interface.router import router as chat_router

app = FastAPI(title="LLM Compare App")

Base.metadata.create_all(bind=engine)

app.include_router(chat_router)
