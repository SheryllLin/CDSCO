import re
from typing import Iterable, List


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sentence_split(text: str) -> List[str]:
    text = normalize_whitespace(text)
    if not text:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def keyword_sentences(text: str, keywords: Iterable[str]) -> List[str]:
    wanted = [k.lower() for k in keywords]
    hits = []
    for sentence in sentence_split(text):
        low = sentence.lower()
        if any(k in low for k in wanted):
            hits.append(sentence)
    return hits


def chunk_text(text: str, max_chars: int) -> List[str]:
    sentences = sentence_split(text)
    if not sentences:
        return []
    chunks: List[str] = []
    current = []
    size = 0
    for sentence in sentences:
        if current and size + len(sentence) + 1 > max_chars:
            chunks.append(" ".join(current))
            current = [sentence]
            size = len(sentence)
        else:
            current.append(sentence)
            size += len(sentence) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks
