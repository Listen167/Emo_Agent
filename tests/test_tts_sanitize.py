import unittest

import tests._path  # noqa: F401
from ai.tts.text import sanitize_for_tts


class TTSSanitizeTest(unittest.TestCase):
    def test_removes_stage_directions_in_brackets(self):
        text = "（笑到拍大腿）这也太离谱了！"

        self.assertEqual(sanitize_for_tts(text), "这也太离谱了")

    def test_removes_asterisk_actions(self):
        text = "*叹气* 我们先一步一步来。"

        self.assertEqual(sanitize_for_tts(text), "我们先一步一步来")


if __name__ == "__main__":
    unittest.main()
