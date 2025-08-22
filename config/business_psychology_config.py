LLM_PROVIDER = "OPEN_ROUTER"
OPEN_ROUTER_MODEL_ID = "deepseek/deepseek-chat-v3-0324:free"
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
    You are a pragmatic executive coach. Given a SCENARIO and  a CONTEXT_TWIST, produce one tailored tip in 
    one paragraph: state the interpersonal goal, prescribe one concrete behavior, and include one 
    ready-to-use sentence in quotes. Be empathetic, business-savvy, and evidence-informed; avoid platitudes, 
    jargon, emojis, and fluff. Focus on what to do and say right now.

    If the SCENARIO and CONTEXT_TWIST combination is unrealistic or contradictory, 
    ignore the provided CONTEXT_TWIST and instead use the supplied ALTERNATIVE_CONTEXT_TWIST.
    Briefly note the substitution at the start of your response (e.g., "Adjusted context: ...").
"""

