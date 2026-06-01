from pydantic import BaseModel

LUCID_SYSTEM = (
    "You are Lucid, the intelligence behind a pair of camera glasses. "
    "The wearer presses a button and you receive whatever was in front of them: "
    "a math problem, an exam question, a multiple-choice sheet, a line of code, "
    "a form, a sign in another language, a broken device. "
    "Your job, in order: decide what actually needs solving in the frame, "
    "solve it correctly, then write hud_text, the single answer to display on a "
    "tiny screen inside the lens. "
    "The wearer cannot scroll and is reading discreetly, so hud_text must be the "
    "bottom-line result, answer first, 120 characters maximum. "
    "For multiple choice, hud_text is just the letter and the option. "
    "Put the full reasoning in solution, never in hud_text. "
    "If the frame is too blurry or empty to solve, say so in hud_text and set low confidence."
)


class LucidSolution(BaseModel):
    problem_type: str
    summary: str
    solution: str
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
            "Put only the translation in hud_text and set problem_type to 'translation'."
        )
    if notes:
        joined = "\n".join(f"- {note}" for note in notes)
        parts.append(
            "The wearer provided their own reference material. Treat it as the source of "
            f"truth and prefer it when it is relevant:\n{joined}"
        )
    if ocr_text:
        parts.append(
            "Handwriting OCR extracted from the frame (use it to disambiguate messy "
            f"strokes; trust the image if they disagree):\n{ocr_text}"
        )
    if mode:
        parts.append(f"The wearer set the session focus to: {mode}. Read the scene through that lens first.")
    if peer_answers:
        listed = "\n".join(
            f"- {p['provider']} answered '{p['hud_text']}' because: {p['solution']}" for p in peer_answers
        )
        parts.append(
            "Other AI models examined the exact same frame and proposed:\n"
            f"{listed}\n"
            "Reconsider carefully. If one of them exposes a mistake in your reading, correct it. "
            "If you are still confident you are right, keep your answer. Output your best final answer."
        )
    parts.append("Identify what should be solved, solve it, and fill the schema.")
    return "\n\n".join(parts)
