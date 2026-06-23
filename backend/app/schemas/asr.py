from pydantic import BaseModel


class ASRTranscribeResponse(BaseModel):
    text: str
