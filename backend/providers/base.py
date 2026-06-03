from pydantic import BaseModel

LUCID_SYSTEM = (
    "You are Lucid, the intelligence behind a pair of assistive camera glasses. "
    "The wearer points at something and you receive the frame in front of them: "
    "a street sign, a restaurant menu, a product label, a page of text, a foreign "
    "phrase, a device they are trying to operate. "
    "Your job, in order: decide what in the frame is most useful to the wearer, "
    "understand it, then write hud_text - the single line shown on the small in-lens "
    "display and read aloud. "
    "The wearer cannot scroll, so hud_text is the bottom line first, 120 characters "
    "maximum: the translation, the key fact, or the next step. "
    "Put the fuller explanation in detail, never in hud_text. "
    "If the frame is too blurry or empty to read, say so in hud_text and set low confidence."
)


class LucidSolution(BaseModel):
    kind: str
    summary: str
    detail: str
    hud_text: str
    confidence: float


def build_user_text(
    ocr_text: str | None,
    mode: str | None,
    peer_answers: list[dict] | None = None,
    notes: list[str] | None = None,
    translate_to: str | None = None,
) -> str:
    parts: list[str] = []
    if translate_to:
        parts.append(
            f"Translation task: translate the text in the frame into {translate_to}. "
            "Put only the translation in hud_text and set kind to 'translation'."
        )
    if notes:
        joined = "\n".join(f"- {note}" for note in notes)
        parts.append(
            "The wearer provided their own reference material. Treat it as the source of "
            f"truth and prefer it when it is relevant:\n{joined}"
        )
    if ocr_text:
        parts.append(
            "Text recognition extracted from the frame (use it to disambiguate messy or "
            f"low-contrast text; trust the image if they disagree):\n{ocr_text}"
        )
    if mode:
        parts.append(f"The wearer set the session focus to: {mode}. Read the scene through that lens first.")
    if peer_answers:
        listed = "\n".join(
            f"- {p['provider']} answered '{p['hud_text']}' because: {p['detail']}" for p in peer_answers
        )
        parts.append(
            "Other AI models examined the exact same frame and proposed:\n"
            f"{listed}\n"
            "Reconsider carefully. If one of them exposes a mistake in your reading, correct it. "
            "If you are still confident you are right, keep your answer. Output your best final answer."
        )
    parts.append("Identify what is most useful in the frame, understand it, and fill the schema.")
    return "\n\n".join(parts)
