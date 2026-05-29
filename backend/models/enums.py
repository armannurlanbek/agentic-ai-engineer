from enum import Enum


class ContentType(str, Enum):
    TWEET = "tweet"
    QUOTE_RETWEET = "quote_retweet"
    THREAD = "thread"
    ESSAY = "essay"
    ARTICLE = "article"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


TAVILY_QUERY_COUNT = {
    ContentType.TWEET: 2,
    ContentType.QUOTE_RETWEET: 2,
    ContentType.THREAD: 3,
    ContentType.ESSAY: 4,
    ContentType.ARTICLE: 5,
}


# (key_facts, tensions, angle_seeds) per content type
TOPIC_BRIEF_COUNTS = {
    ContentType.TWEET: (3, 1, 2),
    ContentType.QUOTE_RETWEET: (3, 1, 2),
    ContentType.THREAD: (5, 2, 3),
    ContentType.ESSAY: (6, 3, 4),
    ContentType.ARTICLE: (7, 3, 4),
}


# How many candidate angles to generate per content type
ANGLE_COUNTS = {
    ContentType.TWEET: 3,
    ContentType.QUOTE_RETWEET: 3,
    ContentType.THREAD: 5,
    ContentType.ESSAY: 6,
    ContentType.ARTICLE: 6,
}


# ── Length contracts (single source of truth for draft/critic/voice/harness) ──

# Hard per-output character cap for single-tweet formats.
CHAR_LIMITS = {
    ContentType.TWEET: 280,
    ContentType.QUOTE_RETWEET: 280,
}

# Per-segment cap for threads (each numbered tweet).
THREAD_SEGMENT_CHAR_LIMIT = 280
THREAD_MIN_SEGMENTS = 4

# Word bands for long-form: (floor, target, ceiling).
# Floors are enforced by the critic (under-length -> auto-revise) and are set to
# values gpt-4o can realistically reach in 2-3 iterations with sectioned prompts.
WORD_BANDS = {
    ContentType.ESSAY: (700, 1100, 1900),
    ContentType.ARTICLE: (1200, 1900, 3400),
}


# AI-slop phrases banned across generation, critique, and final voice pass.
# The harness lints against this same list so "what we forbid" == "what we check".
SLOP_PHRASES = [
    "delve", "tapestry", "in today's fast-paced", "in the realm of",
    "it's important to note", "it is important to note", "game-changer",
    "game changer", "navigate the landscape", "navigating the landscape",
    "ever-evolving", "ever evolving", "ever-shifting", "ever-changing",
    "unlock the potential", "unlocking the potential", "unleash the power",
    "harness the power", "at the end of the day", "when it comes to",
    "the world of", "revolutionize", "revolutionizing", "revolutionary",
    "seamless", "seamlessly", "cutting-edge", "look no further",
    "rest assured", "needless to say", "a testament to", "plays a crucial role",
    "plays a vital role", "plays a pivotal role", "in conclusion,",
    "to summarize", "first and foremost", "paradigm shift", "dawn of",
    "in the ever", "stands as a", "treacherous landscape",
]
