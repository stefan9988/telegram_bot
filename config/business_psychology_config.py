LLM_PROVIDER = "OPEN_ROUTER" # "AZURE", "OPEN_ROUTER"
AZURE_MODEL_ID = "gpt-4o"
OPEN_ROUTER_MODEL_ID = "moonshotai/kimi-k2:free" # "z-ai/glm-4.5-air:free", "deepseek/deepseek-chat-v3-0324:free"
TEMPERATURE = 0.4
TOP_P = 1.0
SCENARIOS = [
    "job interview",
    "team meeting",
    "performance review",
    "networking event",
    "salary negotiation",
    "client presentation",
    "conflict resolution with a colleague",
    "giving constructive feedback",
    "receiving criticism",
    "managing up",
    "onboarding a new team member",
    "1:1 career development conversation",
    "mentoring or coaching session",
    "project kickoff",
    "sprint retrospective",
    "town hall or all-hands meeting",
    "board meeting or investor update",
    "handling layoffs or tough news",
    "managing a difficult client relationship",
    "mediating conflict between teammates",
]


CONTEXT_TWISTS = [
    "with a skeptical executive",
    "with a non-technical stakeholder",
    "with a junior colleague",
    "cross-functional team",
    "cross-cultural setting",
    "after a recent mistake",
    "under a tight deadline",
    "when stakes are high",
    "when goals are unclear",
    "with conflicting priorities",
    "when trust is low",
    "when emotions run high",
    "when you have less power",
    "when you have more power",
    "when you need a decision today",
    "when you must push back",
    "when you have to say no",
    "when alignment is missing",
    "with limited information",
    "when prior feedback was ignored",
    "in a fully remote context",
    "when language barriers exist",
    "with a data-first approach",
    "with a story-first approach",
    "with a time-boxed agenda",
    "as a follow-up",
    "during preparation beforehand",
    "when the other person is defensive",
    "when someone is disengaged",
    "when the other side dominates the conversation",
    "when you need to rebuild credibility",
    "when hidden agendas are in play",
    "in a startup environment",
    "in a corporate bureaucracy",
    "in a highly regulated industry",
    "with no prep time",
    "after a meeting was rescheduled last-minute",
]


SYSTEM_MESSAGE = """
    You are a pragmatic executive coach. Given a SCENARIO and a CONTEXT_TWIST, produce one tailored tip in 
    one paragraph: state the interpersonal goal, prescribe one concrete behavior, and include one ready-to-use 
    sentence in quotes. Be empathetic, business-savvy, and evidence-informed; avoid platitudes, jargon, emojis, 
    and fluff. Focus on what to do and say right now.

    Decision protocol (follow strictly):
    1) Evaluate whether the SCENARIO + CONTEXT_TWIST is unrealistic or contradictory.
    Use these checks:
    - Audience mismatch (e.g., "board meeting" + "with a junior colleague")
    - Temporal mismatch (one-off event + "as a follow-up")
    - Process mismatch (conflict mediation + "data-first approach" as primary mode)
    2) If—and only if—you can state a concrete contradiction in ≤12 words, substitution is allowed.
    Otherwise, KEEP the original CONTEXT_TWIST.
    3) Never invent an alternative. Only use ALTERNATIVE_CONTEXT_TWIST if provided AND step (2) is satisfied.
    4) First line must be exactly one of:
    - "Substitution: NO"
    - "Substitution: YES — reason: <12-word reason>; Using: <ALTERNATIVE_CONTEXT_TWIST>"

    Then write the tip.
"""


