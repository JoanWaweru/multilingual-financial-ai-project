"""
Language style detection and instructions for code-switching behavior.
"""
from __future__ import annotations

import re
from typing import Literal

LanguageStyle = Literal["english", "kiswahili", "code-switch"]


def detect_language_style(text: str) -> LanguageStyle:
    """Heuristic detector for English/Kiswahili/code-switch."""
    tokens = re.findall(r"[a-z']+", text.lower())
    if not tokens:
        return "english"

    neutral_terms = {
        "sacco", "saccos", "mmf", "mmfs", "t-bill", "t-bills", "treasury",
        "bond", "bonds", "nse", "kes", "ksh", "market", "fund", "funds"
    }

    sw_words = {
        "na", "ya", "kwa", "kwenye", "ni", "sio", "si", "wewe", "mimi", "yako",
        "yangu", "wako", "wangu", "hii", "hizo", "hayo", "huyu", "wapi", "nini",
        "nime", "una", "nina", "kuwa", "kuna", "pesa", "uwekezaji", "sacco",
        "sasa", "kabisa", "tafadhali", "karibu", "tumia", "fanya", "sababu",
        "muda", "mrefu", "hatari", "faida", "akaunti", "benki"
    }
    en_words = {
        "the", "and", "for", "with", "that", "this", "you", "your", "i", "we",
        "should", "can", "could", "would", "please", "invest", "investment",
        "return", "risk", "money", "savings", "account", "bank"
    }

    sw_hits = sum(1 for t in tokens if t in sw_words and t not in neutral_terms)
    en_hits = sum(1 for t in tokens if t in en_words and t not in neutral_terms)

    if sw_hits > 0 and en_hits > 0:
        # Treat any clear mix as code-switch (even short prompts)
        return "code-switch"

    if sw_hits > en_hits:
        return "kiswahili"
    if en_hits > sw_hits:
        return "english"

    vowel_ending = sum(1 for t in tokens if t[-1] in "aeiou")
    return "kiswahili" if vowel_ending >= max(3, len(tokens) // 2) else "english"


def language_style_instruction(style: LanguageStyle) -> str:
    if style == "kiswahili":
        return "Reply in Kiswahili only."
    if style == "code-switch":
        return "Reply in a code-switched mix of English and Kiswahili, matching the user's mix and tone."
    return "Reply in English only."


def is_code_switch_compliant(text: str) -> bool:
    """Check for at least one English sentence and one Kiswahili sentence."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    en_count = 0
    sw_count = 0
    for sentence in sentences:
        tokens = re.findall(r"[a-z']+", sentence.lower())
        if len(tokens) < 3:
            continue
        style = detect_language_style(sentence)
        if style == "english":
            en_count += 1
        elif style == "kiswahili":
            sw_count += 1
    return en_count >= 1 and sw_count >= 1
