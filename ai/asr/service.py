from . import provider


class ASRService:
    def transcribe(self, audio_path: str):
        return provider.transcribe(audio_path)


_asr_service = ASRService()


def get_asr_service() -> ASRService:
    return _asr_service
