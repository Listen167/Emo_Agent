import unittest

import tests._path  # noqa: F401
from ai.llm.service import LLMService


class LLMServicePromptTest(unittest.TestCase):
    def test_build_system_prompt_has_emotion_strategy_without_forced_memes(self):
        service = LLMService()

        prompt = service.build_system_prompt("sad")

        self.assertIn("当前识别到的用户情绪：sad", prompt)
        self.assertIn("用户情绪偏低落", prompt)
        self.assertIn("不要强行玩梗", prompt)
        self.assertNotIn("拍大腿", prompt.replace("不要输出“（笑）”“（拍大腿）”这类舞台动作。", ""))
        self.assertNotIn("烂梗烂梗", prompt)

    def test_build_messages_injects_knowledge_context(self):
        service = LLMService()

        messages = service.build_messages(
            "奖学金怎么评？",
            {"label": "neutral"},
            history=[{"role": "user", "content": "我想了解综测"}],
            knowledge_context="[1] 奖学金规则\n需要参考综测成绩。",
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("校园知识库检索结果", messages[1]["content"])
        self.assertEqual(messages[-1], {"role": "user", "content": "奖学金怎么评？"})


if __name__ == "__main__":
    unittest.main()
