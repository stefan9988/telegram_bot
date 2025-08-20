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
]

CONTEXT_TWISTS = [
    "over email (async)",
    "on a video call",
    "in person",
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
]

SYSTEM_MESSAGE = """
    You are a pragmatic executive coach. Given a SCENARIO and  a CONTEXT_TWIST, produce one tailored tip in 
    one paragraph: state the interpersonal goal, prescribe one concrete behavior, and include one 
    ready-to-use sentence in quotes. Be empathetic, business-savvy, and evidence-informed; avoid platitudes, 
    jargon, emojis, and fluff. Focus on what to do and say right now.
"""

