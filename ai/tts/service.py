from . import provider


class TTSService:
    def synthesize(self, text: str, session_id: str, emotion: str) -> str:
        return provider.synthesize(text, session_id, emotion)

    def sanitize_for_tts(self, text: str) -> str:
        return provider.sanitize_for_tts(text)


_tts_service = TTSService()


def get_tts_service() -> TTSService:
    return _tts_service
