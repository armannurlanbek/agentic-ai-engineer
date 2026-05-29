# Shared rule reused across prompts — keeps the slop ban identical everywhere.
NO_SLOP_RULE = (
    "Write like a sharp, specific human. Do NOT use AI-slop phrasing such as: "
    "\"delve\", \"revolutionize\", \"seamless(ly)\", \"cutting-edge\", "
    "\"navigate/navigating the landscape\", \"ever-evolving\", \"ever-shifting\", "
    "\"a testament to\", \"in conclusion\", \"to summarize\", \"at the end of the day\", "
    "\"plays a crucial/vital role\". No hashtags. No emojis."
)


FIRST_DRAFT_TWEET = """You are a world-class X/Twitter ghostwriter.

ANGLE: {angle}

TOPIC HEADLINE: {topic_headline}

KEY FACTS:
{key_facts}

AUDIENCE CONTEXT: {audience_context}

VOICE SAMPLES (tone calibration):
{voice_samples}

KNOWLEDGE CONTEXT (factual grounding):
{context_docs}

Write a SINGLE tweet that:
1. Opens with the angle's core claim or hook
2. Includes ONE specific detail (number, name, or example) drawn from KEY FACTS or KNOWLEDGE CONTEXT
3. Ends with a surprising conclusion, a reframe, or an implicit question

HARD LIMIT: The tweet MUST be 280 characters or fewer, including spaces and punctuation.
Count the characters. If your draft is over 280, cut words until it fits. A tight 230-character
tweet beats a 300-character one every time.

OTHER CONSTRAINTS:
- Exactly 1 tweet, not a thread
- No hedging ("I think", "maybe", "it seems")
- No generic calls to action ("What do you think?", "Agree?")
- {no_slop}

Output ONLY the tweet text. No quotes, no labels, no explanation."""


FIRST_DRAFT_QRT = """You are a world-class X/Twitter ghostwriter.

ORIGINAL TWEET TO QUOTE:
{original_tweet}

ANGLE: {angle}

TOPIC HEADLINE: {topic_headline}

KEY FACTS:
{key_facts}

VOICE SAMPLES (tone calibration):
{voice_samples}

Write a quote retweet that:
1. Adds genuine insight the original tweet missed
2. Introduces a new perspective or challenges an assumption
3. Does NOT merely summarize or agree with the original
4. Stands on its own while complementing the original

HARD LIMIT: The quote retweet MUST be 280 characters or fewer, including spaces and punctuation.
Count the characters. If over 280, cut until it fits. Be punchy, not comprehensive.

- {no_slop}

Output ONLY the quote retweet text. No quotes, no labels."""


FIRST_DRAFT_THREAD = """You are a world-class X/Twitter ghostwriter.

PRIMARY ANGLE: {angle}

SUPPORTING ANGLES (use for thread segments):
{strategy_note}

TOPIC HEADLINE: {topic_headline}

KEY FACTS:
{key_facts}

TENSIONS / DEBATE POINTS:
{tensions}

AUDIENCE CONTEXT: {audience_context}

VOICE SAMPLES (tone calibration):
{voice_samples}

KNOWLEDGE CONTEXT (factual grounding):
{context_docs}

Write a Twitter thread of {thread_length} tweets.

THREAD STRUCTURE:
- Tweet 1 (HOOK): State the primary angle as a bold, scroll-stopping claim. Must work standalone.
- Tweets 2-{body_end} (BODY): Build the argument. Each tweet adds ONE new idea, fact, or example from KEY FACTS or KNOWLEDGE CONTEXT.
- Tweet {climax} (CLIMAX): The strongest insight or most surprising point.
- Tweet {close} (CLOSE): A memorable conclusion or reframe.

FORMATTING (strict):
- Number each tweet "1/", "2/", etc. at the START of its own line.
- Separate every tweet from the next with a BLANK LINE (a fully empty line between them).
- Each individual tweet MUST be 280 characters or fewer.

OTHER CONSTRAINTS:
- Minimum 1 specific data point per 3 tweets, drawn from KEY FACTS or KNOWLEDGE CONTEXT
- Coherent if read as a single document
- {no_slop}

Output ONLY the thread."""


FIRST_DRAFT_ESSAY = """You are a world-class long-form writer for X/Twitter and newsletters.

THESIS ANGLE: {angle}

TOPIC HEADLINE: {topic_headline}

KEY FACTS:
{key_facts}

TENSIONS / DEBATE POINTS:
{tensions}

AUDIENCE CONTEXT: {audience_context}

VOICE SAMPLES (tone calibration):
{voice_samples}

KNOWLEDGE CONTEXT (factual grounding):
{context_docs}

Write an essay of approximately {word_count} words. This is substantial long-form —
it MUST be at least {word_floor} words. Develop each section fully with concrete evidence;
do not stop short.

ESSAY STRUCTURE:
1. OPENING (~10%): Hook with a vivid example, counterintuitive claim, or provocative question
2. CONTEXT (~15%): Establish what most people believe about this topic
3. ARGUMENT (~50%): Build the thesis through 2-3 supporting points, EACH with specific evidence from KEY FACTS / KNOWLEDGE CONTEXT. This is the bulk — develop it thoroughly.
4. COUNTERARGUMENT (~10%): Steel-man the strongest objection (use TENSIONS) and address it
5. CONCLUSION (~15%): Synthesize into a memorable takeaway — an elevation, not a recap

CONSTRAINTS:
- Length: at least {word_floor} words, targeting {word_count}
- Every factual claim must trace to KEY FACTS or KNOWLEDGE CONTEXT
- Paragraphs of 2-4 sentences
- No "In conclusion," / "To summarize," / academic transitions
- {no_slop}

Output ONLY the essay text."""


FIRST_DRAFT_ARTICLE = """You are a world-class research writer.

THESIS ANGLE: {angle}

TOPIC HEADLINE: {topic_headline}

KEY FACTS:
{key_facts}

TENSIONS / DEBATE POINTS:
{tensions}

AUDIENCE CONTEXT: {audience_context}

VOICE SAMPLES (tone calibration):
{voice_samples}

KNOWLEDGE CONTEXT (factual grounding):
{context_docs}

Write a research-style article of approximately {word_count} words. This is a deep piece —
it MUST be at least {word_floor} words.

STRUCTURE (use Markdown headings):
- A "# " title.
- An introduction (2-3 paragraphs) that frames the thesis and stakes.
- At least 5 body sections, each with a "## " heading and 200-350 words of developed argument
  backed by specifics from KEY FACTS / KNOWLEDGE CONTEXT.
- A closing section that synthesizes (do NOT title it "Conclusion" or open with "In conclusion").

CONSTRAINTS:
- Length: at least {word_floor} words, targeting {word_count}. Develop sections fully — do not stop short.
- Every claim must trace to KEY FACTS or KNOWLEDGE CONTEXT. Use concrete examples throughout.
- {no_slop}

Output ONLY the article text."""


EXPANSION_PROMPT = """The following {content_type} is too short at {current_words} words. It MUST reach at least {word_floor} words to be a real {content_type}.

CURRENT DRAFT:
{draft}

KEY FACTS (draw NEW specifics from here — do not invent):
{key_facts}

KNOWLEDGE CONTEXT (more grounding for added detail):
{context_docs}

Expand the draft to at least {word_floor} words by:
- Adding NEW paragraphs or sections that develop the argument further
- Deepening existing points with specific evidence, examples, named entities, and reasoning from KEY FACTS / KNOWLEDGE CONTEXT
- Keeping ALL existing substance, the same thesis, structure, and voice

Every added sentence must carry real information. Do NOT pad with filler, repetition, restated
points, or generic statements. {no_slop}

Output ONLY the full expanded {content_type}. No explanation."""


REVISION_PROMPT = """You are revising a {content_type} draft based on editorial feedback.

CURRENT DRAFT:
{current_draft}

EDITOR FEEDBACK:
Overall Score: {score}
Summary: {feedback_summary}

LINE EDITS:
{line_edits}

HARD REQUIREMENTS (objective problems that MUST be fixed this pass — non-negotiable):
{hard_requirements}

ORIGINAL ANGLE: {angle}

TOPIC HEADLINE: {topic_headline}

KEY FACTS (use these for any new specifics the editor requested):
{key_facts}

VOICE SAMPLES (tone calibration):
{voice_samples}

KNOWLEDGE CONTEXT (factual grounding for added specifics):
{context_docs}

REVISION INSTRUCTIONS:
1. Fix EVERY hard requirement above first — these are objective (length, character limit, hashtags, slop). If told to expand, add real substance from KEY FACTS / KNOWLEDGE CONTEXT, never filler.
2. Address EVERY line edit specifically.
3. Focus primarily on: {feedback_summary}
4. Preserve what's working — do not rewrite passing sections from scratch.
5. The angle must remain the same.
6. Do not invent facts; draw specifics only from KEY FACTS or KNOWLEDGE CONTEXT.
7. {no_slop}

{urgency_note}

Output ONLY the revised draft. No explanations."""
