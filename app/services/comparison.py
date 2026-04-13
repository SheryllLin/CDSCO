import difflib
from typing import List

from app.models.schemas import CompareResponse, ModifiedSegment
from app.utils.text import sentence_split


class DocumentComparisonService:
    def compare(self, old_text: str, new_text: str) -> CompareResponse:
        old_sentences = sentence_split(old_text)
        new_sentences = sentence_split(new_text)
        matcher = difflib.SequenceMatcher(a=old_sentences, b=new_sentences)

        added: List[str] = []
        removed: List[str] = []
        modified: List[ModifiedSegment] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "insert":
                added.extend(new_sentences[j1:j2])
            elif tag == "delete":
                removed.extend(old_sentences[i1:i2])
            elif tag == "replace":
                old_block = " ".join(old_sentences[i1:i2]).strip()
                new_block = " ".join(new_sentences[j1:j2]).strip()
                if old_block or new_block:
                    modified.append(ModifiedSegment(before=old_block, after=new_block))

        unified_diff = "\n".join(
            difflib.unified_diff(
                old_text.splitlines(),
                new_text.splitlines(),
                fromfile="old_version",
                tofile="new_version",
                lineterm="",
            )
        )
        return CompareResponse(
            added=added,
            removed=removed,
            modified=modified,
            unified_diff=unified_diff,
            change_summary={
                "added_count": len(added),
                "removed_count": len(removed),
                "modified_count": len(modified),
            },
        )
