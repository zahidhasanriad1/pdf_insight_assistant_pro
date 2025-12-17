import re

def clean_repetition(text: str, max_bullets: int = 6) -> str:
    if not text:
        return text

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    seen = set()
    cleaned = []
    bullet_count = 0

    for ln in lines:
        norm = re.sub(r"\s+", " ", ln).strip().lower()

        if norm in seen:
            continue
        seen.add(norm)

        is_bullet = ln.startswith(("•", "*", "-", "1.", "2.", "3.", "4.", "5.", "6."))
        if is_bullet:
            bullet_count += 1
            if bullet_count > max_bullets:
                continue

        cleaned.append(ln)

    out = "\n".join(cleaned).strip()

    out = re.sub(r"(\n\s*){3,}", "\n\n", out)
    return out
