from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), index=True)
    role = Column(String(10))  # user / assistant
    content_type = Column(String(10))  # text / audio
    content = Column(Text, nullable=False)
    emotion_label = Column(String(20), nullable=True)
    emotion_conf = Column(Float, nullable=True)
    tts_audio_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())