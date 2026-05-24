from . import fusion, provider


class EmotionService:
    def predict_text(self, text: str):
        return provider.predict_text(text)

    def fuse(self, audio_probs, text_probs, audio_weight: float) -> dict:
        return fusion.calculate(audio_probs, text_probs, audio_weight)


_emotion_service = EmotionService()


def get_emotion_service() -> EmotionService:
    return _emotion_service
