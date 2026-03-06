"""
The 4D AI Fluency Framework (Dakan, Feller & Anthropic, 2025)

4 Competencies, 12 Sub-competencies, 24 Behaviors
"""

from dataclasses import dataclass


@dataclass
class Behavior:
    id: int
    competency: str
    sub_competency: str
    name: str
    description: str
    observable: bool


BEHAVIORS: list[Behavior] = [
    # === DELEGATION ===
    # Problem Awareness
    Behavior(1, "Delegation", "Problem Awareness",
             "Clarifies goal before asking for help",
             "Defines what they want to accomplish before engaging AI. "
             "Articulates success criteria, project goals, and the nature of the work needed.",
             observable=True),
    Behavior(2, "Delegation", "Problem Awareness",
             "Understands problem scope and nature",
             "Recognizes what kind of thinking and work is needed: simple but time-consuming, "
             "uncertain and needing a thinking partner, requiring more data, or requiring critical judgment.",
             observable=False),
    # Platform Awareness
    Behavior(3, "Delegation", "Platform Awareness",
             "Assesses AI fit",
             "Evaluates whether a given AI system is appropriate for the task at hand, "
             "considering its strengths and limitations.",
             observable=False),
    Behavior(4, "Delegation", "Platform Awareness",
             "Selects platform",
             "Chooses among available AI systems based on task requirements, "
             "comparing capabilities like speed vs depth, accuracy vs creativity.",
             observable=False),
    # Task Delegation
    Behavior(5, "Delegation", "Task Delegation",
             "Consults AI on approach before execution",
             "Discusses strategy or approach with AI before diving into task execution. "
             "Uses AI as a thinking partner to plan work distribution.",
             observable=True),
    Behavior(6, "Delegation", "Task Delegation",
             "Distributes work strategically",
             "Thoughtfully divides work between human and AI, leveraging the unique "
             "strengths of each. Identifies what to automate, augment, or reserve for human-only.",
             observable=False),

    # === DESCRIPTION ===
    # Product Description
    Behavior(7, "Description", "Product Description",
             "Specifies format and structure needed",
             "Clearly defines desired output format, length, structure, and other "
             "characteristics rather than leaving AI to guess.",
             observable=True),
    Behavior(8, "Description", "Product Description",
             "Defines audience for the output",
             "Specifies who the output is for, what context it will be used in, "
             "and what level of detail or expertise is appropriate.",
             observable=True),
    # Process Description
    Behavior(9, "Description", "Process Description",
             "Provides examples of what good looks like",
             "Uses few-shot prompting or reference examples to demonstrate "
             "the desired style, format, or approach.",
             observable=True),
    Behavior(10, "Description", "Process Description",
              "Iterates and refines",
              "Engages in back-and-forth with AI, refining requests based on outputs. "
              "Adjusts prompts, adds context, or changes approach based on results.",
              observable=True),
    # Performance Description
    Behavior(11, "Description", "Performance Description",
              "Sets interaction mode",
              "Defines the type of collaboration needed: brainstorming vs converging, "
              "challenging assumptions vs following lead, detailed vs concise.",
              observable=True),
    Behavior(12, "Description", "Performance Description",
              "Communicates tone and style preferences",
              "Specifies role, persona, expertise level, or communication style "
              "for the AI to adopt during the interaction.",
              observable=True),

    # === DISCERNMENT ===
    # Product Discernment
    Behavior(13, "Discernment", "Product Discernment",
              "Checks facts and claims that matter",
              "Verifies factual accuracy of AI outputs, especially for claims "
              "that will be relied upon or shared with others.",
              observable=True),
    Behavior(14, "Discernment", "Product Discernment",
              "Identifies when AI might be missing context",
              "Recognizes when AI output lacks important context or makes assumptions "
              "that don't match the actual situation.",
              observable=True),
    # Process Discernment
    Behavior(15, "Discernment", "Process Discernment",
              "Questions when AI reasoning doesn't hold up",
              "Challenges AI's logical reasoning, identifies circular arguments, "
              "or pushes back when the AI's process seems flawed.",
              observable=True),
    Behavior(16, "Discernment", "Process Discernment",
              "Detects hallucination",
              "Recognizes when AI confidently produces plausible but incorrect information, "
              "and takes steps to verify or correct it.",
              observable=False),
    # Performance Discernment
    Behavior(17, "Discernment", "Performance Discernment",
              "Evaluates tone and communication fit",
              "Assesses whether the AI's communication style is effective for the task "
              "and adjusts if needed.",
              observable=False),
    Behavior(18, "Discernment", "Performance Discernment",
              "Recognizes bias in AI outputs",
              "Identifies systematic patterns in AI outputs that unfairly favor or "
              "disadvantage certain groups or perspectives.",
              observable=False),

    # === DILIGENCE ===
    # Creation Diligence
    Behavior(19, "Diligence", "Creation Diligence",
              "Chooses AI tools ethically",
              "Considers data privacy, security, ownership, and organizational policies "
              "before sharing information with AI systems.",
              observable=False),
    Behavior(20, "Diligence", "Creation Diligence",
              "Maintains ethical awareness during interaction",
              "Stays alert to ethical implications throughout the AI interaction, "
              "including potential harms and biases.",
              observable=False),
    # Transparency Diligence
    Behavior(21, "Diligence", "Transparency Diligence",
              "Discloses AI involvement to stakeholders",
              "Proactively communicates when and how AI was involved in creating work, "
              "to appropriate audiences.",
              observable=False),
    Behavior(22, "Diligence", "Transparency Diligence",
              "Represents AI contribution accurately",
              "Honestly characterizes the extent of AI's role — neither overstating "
              "nor understating its contribution.",
              observable=False),
    # Deployment Diligence
    Behavior(23, "Diligence", "Deployment Diligence",
              "Verifies and tests outputs before sharing",
              "Conducts thorough review of AI-assisted outputs before deploying or sharing, "
              "including fact-checking, bias review, and quality assurance.",
              observable=False),
    Behavior(24, "Diligence", "Deployment Diligence",
              "Takes ongoing accountability",
              "Accepts full responsibility for AI-assisted work products, "
              "willing to stand behind and be accountable for the final output.",
              observable=False),
]

COMPETENCIES = ["Delegation", "Description", "Discernment", "Diligence"]

SUB_COMPETENCIES = {
    "Delegation": ["Problem Awareness", "Platform Awareness", "Task Delegation"],
    "Description": ["Product Description", "Process Description", "Performance Description"],
    "Discernment": ["Product Discernment", "Process Discernment", "Performance Discernment"],
    "Diligence": ["Creation Diligence", "Transparency Diligence", "Deployment Diligence"],
}


def get_observable_behaviors() -> list[Behavior]:
    return [b for b in BEHAVIORS if b.observable]


def get_unobservable_behaviors() -> list[Behavior]:
    return [b for b in BEHAVIORS if not b.observable]


def get_behaviors_by_competency(competency: str) -> list[Behavior]:
    return [b for b in BEHAVIORS if b.competency == competency]
