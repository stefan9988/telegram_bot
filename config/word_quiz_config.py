from .quote_of_the_day_config import FILEPATH
# FILEPATH = 'data/words_of_the_day.txt'
LLM_PROVIDER = "OPEN_ROUTER" # "AZURE", "OPEN_ROUTER"
AZURE_MODEL_ID = "gpt-4o"
OPEN_ROUTER_MODEL_ID = "moonshotai/kimi-k2:free" # "z-ai/glm-4.5-air:free", "deepseek/deepseek-chat-v3-0324:free"
TEMPERATURE = 0.4
TOP_P = 1.0
N_WORDS = 4
SYSTEM_MESSAGE = """
    You are a master creator of sentences. Your goal is to create example sentences for each word provided. Instead of
    using provided words write blank lines with underscores to indicate where the word should be used. DO NOT change
    word order. Each sentence should be clear and contextually relevant to the word it represents.
"""

