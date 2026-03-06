"""
Self-assessment questionnaire for unobservable behaviors.

Covers the 13 behaviors that can't be detected from conversation logs.
"""

from ai_fluency.framework import Behavior, get_unobservable_behaviors

RATING_SCALE = """
Rate yourself 1-5:
  1 = Never / Not at all
  2 = Rarely / Slightly
  3 = Sometimes / Moderately
  4 = Often / Mostly
  5 = Always / Fully
"""

QUESTIONS: dict[int, str] = {
    # Delegation - Problem Awareness
    2: (
        "Before using AI, how consistently do you analyze the nature of your work "
        "(e.g., is it time-consuming but simple, uncertain, requiring data, or "
        "requiring critical judgment)?"
    ),
    # Delegation - Platform Awareness
    3: (
        "How often do you evaluate whether a specific AI tool is the right fit "
        "for your task before starting?"
    ),
    4: (
        "How actively do you compare and choose between different AI platforms "
        "(e.g., Claude vs ChatGPT vs Gemini) based on task requirements?"
    ),
    # Delegation - Task Delegation
    6: (
        "How strategically do you divide work between yourself and AI, "
        "reserving critical judgment for yourself while leveraging AI for its strengths?"
    ),
    # Discernment - Process Discernment
    16: (
        "How reliably do you catch when AI generates plausible-sounding "
        "but incorrect information (hallucinations)?"
    ),
    # Discernment - Performance Discernment
    17: (
        "How often do you evaluate whether the AI's communication style "
        "is actually effective for your needs and adjust accordingly?"
    ),
    18: (
        "How alert are you to potential biases in AI outputs "
        "(e.g., cultural, gender, or perspective biases)?"
    ),
    # Diligence - Creation Diligence
    19: (
        "How carefully do you consider data privacy, security, and organizational "
        "policies before sharing information with AI systems?"
    ),
    20: (
        "How aware are you of ethical implications throughout your AI interactions "
        "(e.g., potential harms, misuse, fairness)?"
    ),
    # Diligence - Transparency Diligence
    21: (
        "How consistently do you disclose AI involvement in your work "
        "to colleagues, clients, or stakeholders who should know?"
    ),
    22: (
        "How accurately do you represent the extent of AI's contribution "
        "when discussing your AI-assisted work?"
    ),
    # Diligence - Deployment Diligence
    23: (
        "How thoroughly do you review and verify AI-assisted outputs "
        "(fact-check, bias review, quality assurance) before sharing or deploying?"
    ),
    24: (
        "How fully do you accept personal accountability for the final quality "
        "and consequences of your AI-assisted work?"
    ),
}


def run_questionnaire(interactive: bool = True) -> dict[int, int]:
    """Run the self-assessment questionnaire interactively or return structure."""
    if not interactive:
        return {bid: 0 for bid in QUESTIONS}

    print("\n=== AI Fluency Self-Assessment ===")
    print(RATING_SCALE)
    print("Answer each question with a number 1-5.\n")

    responses: dict[int, int] = {}
    unobservable = {b.id: b for b in get_unobservable_behaviors()}

    for bid, question in QUESTIONS.items():
        behavior = unobservable[bid]
        print(f"[{behavior.competency} > {behavior.sub_competency}]")
        print(f"  {question}")

        while True:
            try:
                answer = input("  Your rating (1-5): ").strip()
                rating = int(answer)
                if 1 <= rating <= 5:
                    responses[bid] = rating
                    print()
                    break
                print("  Please enter a number between 1 and 5.")
            except (ValueError, EOFError):
                print("  Please enter a number between 1 and 5.")

    return responses


def format_questionnaire_results(responses: dict[int, int]) -> dict:
    """Format questionnaire responses for the report."""
    unobservable = {b.id: b for b in get_unobservable_behaviors()}
    results = []
    for bid, rating in responses.items():
        b = unobservable[bid]
        results.append({
            "behavior_id": bid,
            "competency": b.competency,
            "sub_competency": b.sub_competency,
            "behavior": b.name,
            "question": QUESTIONS[bid],
            "rating": rating,
        })
    return {
        "source": "self_assessment",
        "found": True,
        "responses": results,
    }
