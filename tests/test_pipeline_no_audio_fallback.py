import asyncio
import unittest

import tests._path  # noqa: F401
from app.services.conversation_orchestrator import ConversationOrchestrator


class PipelineNoAudioFallbackTest(unittest.TestCase):
    def test_generate_reply_uses_fallback_when_no_text_available(self):
        orchestrator = ConversationOrchestrator()

        reply = asyncio.run(
            orchestrator._generate_reply(
                "",
                {"label": "neutral", "confidence": 0.0},
                [],
                None,
            )
        )

        self.assertIn("没有听清", reply)
        self.assertIn("文字", reply)


if __name__ == "__main__":
    unittest.main()
