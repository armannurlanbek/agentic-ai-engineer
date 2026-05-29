from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from backend.agents.angle import angle_node
from backend.agents.critic import critic_node
from backend.agents.discovery import discovery_node
from backend.agents.draft_writer import draft_writer_node
from backend.agents.fact_checker import fact_checker_node
from backend.agents.retrieval import retrieval_node
from backend.agents.text_checks import structural_violations
from backend.agents.voice_reviewer import voice_reviewer_node
from backend.models.state import PipelineState

DISCOVERY = "discovery"
RETRIEVAL = "retrieval"
ANGLE = "angle"
DRAFT_WRITER = "draft_writer"
CRITIC = "critic"
FACT_CHECKER = "fact_checker"
VOICE_REVIEWER = "voice_reviewer"

NODE_ORDER = [
    DISCOVERY, RETRIEVAL, ANGLE,
    DRAFT_WRITER, CRITIC,
    FACT_CHECKER, VOICE_REVIEWER, "done",
]


def should_continue_drafting(state: PipelineState) -> str:
    if state.get("draft_passed", False):
        return FACT_CHECKER

    iteration = state.get("draft_iteration", 0)
    max_iterations = state.get("max_draft_iterations", 3)
    if iteration >= max_iterations:
        return FACT_CHECKER

    # Objective structural problems (over char cap, under word floor, hashtags,
    # slop) must not be short-circuited by a quality plateau — keep revising while
    # we still have iterations to fix them. The iteration ceiling above still bounds us.
    if structural_violations(state.get("content_type", "tweet"), state.get("current_draft", "")):
        return DRAFT_WRITER

    history = state.get("critic_feedback_history", [])
    if len(history) >= 2:
        prev_score = history[-2].get("score", 0) if isinstance(history[-2], dict) else 0
        curr_score = history[-1].get("score", 0) if isinstance(history[-1], dict) else 0
        # Plateau: revision didn't move the needle (improved by <0.3 OR got worse).
        # Previous version only caught small *improvements* — missed the common
        # case where iter 2 scores lower than iter 1 and we should bail.
        if curr_score - prev_score < 0.3:
            return FACT_CHECKER

    return DRAFT_WRITER


def build_graph() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node(DISCOVERY, discovery_node)
    graph.add_node(RETRIEVAL, retrieval_node)
    graph.add_node(ANGLE, angle_node)
    graph.add_node(DRAFT_WRITER, draft_writer_node)
    graph.add_node(CRITIC, critic_node)
    graph.add_node(FACT_CHECKER, fact_checker_node)
    graph.add_node(VOICE_REVIEWER, voice_reviewer_node)

    graph.add_edge(START, DISCOVERY)
    graph.add_edge(DISCOVERY, RETRIEVAL)
    graph.add_edge(RETRIEVAL, ANGLE)
    graph.add_edge(ANGLE, DRAFT_WRITER)
    graph.add_edge(DRAFT_WRITER, CRITIC)

    graph.add_conditional_edges(
        CRITIC,
        should_continue_drafting,
        {
            DRAFT_WRITER: DRAFT_WRITER,
            FACT_CHECKER: FACT_CHECKER,
        },
    )

    graph.add_edge(FACT_CHECKER, VOICE_REVIEWER)
    graph.add_edge(VOICE_REVIEWER, END)

    return graph


def compile_graph():
    graph = build_graph()
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


content_pipeline = compile_graph()
