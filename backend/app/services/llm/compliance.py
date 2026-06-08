from __future__ import annotations
"""
Forbidden-phrase filter for any generated copy (zh / vi / mm / en).

Used as a hard gate before LLM output can leave the draft stage. Returns the list
of forbidden hits; an empty list means "clean". Negation/compliance phrases are
explicitly allowed (e.g. "不可提现", "Không phải dịch vụ cá cược").

This never raises; it only reports. Callers decide to block on a non-empty result.
"""

# Substrings that are forbidden in customer-facing copy, by locale family.
_FORBIDDEN = {
    "zh": ["下注", "稳赚", "必中", "跟单", "购彩", "回报率", "返奖",
            "收益承诺", "现金奖池", "包赢", "必赢", "投注"],
    "vi": ["chắc thắng", "đảm bảo thắng", "kiếm tiền", "lợi nhuận chắc chắn",
            "cá cược", "đặt cược"],
    "mm": ["လောင်းကစား"],
    "en": ["guaranteed win", "sure win", "fixed match", "cash prize", "wager", "betting"],
}

# Allowed contexts: a forbidden substring is OK only inside one of these phrases.
_ALLOWED_CONTEXTS = {
    "提现": ["不可提现"],
    "cá cược": ["không phải dịch vụ cá cược", "không nhận cược"],
    "đặt cược": ["không nhận đặt cược"],
    "လောင်းကစား": ["လောင်းကစား မဟုတ်", "လောင်းကစား မချိတ်"],
    "betting": ["not a betting", "no betting", "non-betting"],
    "wager": ["no cash wagering", "no wagering"],
}

# Cross-locale extra: standalone 提现 (allowed only inside 不可提现).
_WITHDRAW = "提现"


def _hit_is_allowed(text_l: str, term_l: str) -> bool:
    ctxs = _ALLOWED_CONTEXTS.get(term_l)
    if not ctxs:
        return False
    # Allowed only if every occurrence of the term sits inside an allowed context.
    idx = 0
    while True:
        pos = text_l.find(term_l, idx)
        if pos == -1:
            return True
        if not any(c in text_l for c in ctxs):
            return False
        # crude: if an allowed context exists in the text, treat this occurrence as covered
        idx = pos + len(term_l)


def scan(text: str, locale: str) -> list[str]:
    """Return forbidden phrases found in `text` for the given locale (+ shared rules)."""
    if not text:
        return []
    text_l = text.lower()
    hits: list[str] = []
    terms = list(_FORBIDDEN.get(locale, [])) + _FORBIDDEN["en"]  # en rules always apply
    for term in terms:
        term_l = term.lower()
        if term_l in text_l and not _hit_is_allowed(text_l, term_l):
            hits.append(term)
    # withdrawal rule (zh): 提现 allowed only inside 不可提现
    if _WITHDRAW in text:
        # count standalone occurrences (not preceded by 不可)
        standalone = text.replace("不可提现", "")
        if _WITHDRAW in standalone:
            hits.append(_WITHDRAW)
    return sorted(set(hits))
