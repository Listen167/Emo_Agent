import re


def sanitize_for_tts(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"[\(\（\[\【<《][^\)\）\]\】>》]{0,40}[\)\）\]\】>》]", "", cleaned)
    cleaned = re.sub(r"\*[^*]{0,40}\*", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" ，。！？,.!?;；:：")
