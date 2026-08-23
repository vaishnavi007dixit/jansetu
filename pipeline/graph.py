"""
The Layer 2 ingestion pipeline, as a LangGraph StateGraph:

    stt_node -> classify_node -> geocode_node -> tts_node -> END

Each node reads/writes a shared PipelineState dict. This is a linear graph on
purpose — a hackathon demo doesn't need branching, but using LangGraph's
StateGraph (rather than five plain function calls) is what lets you honestly
say "multi-agent pipeline" in the README/pitch, and it's a two-minute lift to
add a branch later (e.g. route audio vs text differently, or add a
verification/retry node) if you have time.

If LangGraph install is being difficult tonight, run_pipeline() at the bottom
also works as a plain sequential function chain — see the try/except import.
"""
from typing import Optional, TypedDict

from pipeline.classify import classify
from pipeline.geocode import resolve_location
from pipeline.stt import passthrough_text, transcribe_and_translate
from pipeline.tts import generate_confirmation

try:
    from langgraph.graph import END, StateGraph
    _HAS_LANGGRAPH = True
except ImportError:
    _HAS_LANGGRAPH = False


class PipelineState(TypedDict, total=False):
    request_id: str
    input_type: str
    audio_base64: Optional[str]
    text: Optional[str]
    language_hint: Optional[str]
    reported_lat: Optional[float]
    reported_lng: Optional[float]
    reported_place_name: Optional[str]

    english_text: str
    language_detected: str
    category: str
    lat: Optional[float]
    lng: Optional[float]
    district: str
    confirmation_audio_url: Optional[str]


def stt_node(state: PipelineState) -> PipelineState:
    if state["input_type"] == "audio":
        result = transcribe_and_translate(state["audio_base64"])
    else:
        result = passthrough_text(state["text"], state.get("language_hint"))
    return {**state, **result}


def classify_node(state: PipelineState) -> PipelineState:
    return {**state, "category": classify(state["english_text"])}


def geocode_node(state: PipelineState) -> PipelineState:
    result = resolve_location(
        state.get("reported_lat"),
        state.get("reported_lng"),
        state.get("reported_place_name"),
    )
    return {**state, **result}


def tts_node(state: PipelineState) -> PipelineState:
    url = generate_confirmation(state["english_text"], state["request_id"])
    return {**state, "confirmation_audio_url": url}


def _build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("stt", stt_node)
    graph.add_node("classify", classify_node)
    graph.add_node("geocode", geocode_node)
    graph.add_node("tts", tts_node)

    graph.set_entry_point("stt")
    graph.add_edge("stt", "classify")
    graph.add_edge("classify", "geocode")
    graph.add_edge("geocode", "tts")
    graph.add_edge("tts", END)

    return graph.compile()


_compiled_graph = _build_graph() if _HAS_LANGGRAPH else None


def run_pipeline(state: PipelineState) -> PipelineState:
    if _HAS_LANGGRAPH:
        return _compiled_graph.invoke(state)

    # Fallback: plain sequential chain, same nodes, same order.
    state = stt_node(state)
    state = classify_node(state)
    state = geocode_node(state)
    state = tts_node(state)
    return state
