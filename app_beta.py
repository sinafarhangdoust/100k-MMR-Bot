# app.py
import os
import re
import asyncio
import chainlit as cl
from typing import List, Optional, Set, Tuple
from chainlit import Action  # UI actions (buttons)
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agents.agents import get_llm_agent
from tools import tools_mapping

# === Draft Coach / OpenDota bits ===
from tools.opendota_client import (
    init_heroes,
    resolve_hero_ids,
    counter_scores,
    HERO_IMG,
    HEROES,
    ROLE_PRESETS,
    ids_by_role_tags,
)
from tools.app_helpers import parse_role_param, lock_in



def chat_setup():
    llm_agent = get_llm_agent(model="gpt-4.1-mini", temperature=0.0)
    cl.user_session.set("llm_agent", llm_agent)
    cl.user_session.set("chat_history", [])
    # Draft board lives in session
    cl.user_session.set("draft", {"my": [], "enemy": []})


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("admin", "admin"):
        return cl.User(identifier="admin", metadata={"role": "admin", "provider": "credentials"})
    else:
        return None


def _board() -> dict:
    return cl.user_session.get("draft") or {"my": [], "enemy": []}


def _set_board(bd: dict):
    cl.user_session.set("draft", bd)


def hero_name(hid: int) -> str:
    return HEROES[hid]["localized_name"]


async def _render_board():
    """Render a compact pick board with images."""
    bd = _board()
    my_ids = bd["my"]
    enemy_ids = bd["enemy"]

    parts = ["**Draft Board**"]
    parts.append("**My Picks:** " + (", ".join(hero_name(h) for h in my_ids) if my_ids else "(none)"))
    parts.append("**Enemy Picks:** " + (", ".join(hero_name(h) for h in enemy_ids) if enemy_ids else "(none)"))

    elements = []
    for hid in my_ids + enemy_ids:
        nm = hero_name(hid)
        img = HERO_IMG.get(hid)
        if img:
            elements.append(cl.Image(url=img, name=nm, display="inline"))

    await cl.Message("\n".join(parts), elements=elements).send()


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _mentioned_hero_ids_from_text(text: str) -> List[int]:
    """Very light heuristic: scan for simple hero mentions in LLM text."""
    found = []
    normed = _norm(text)
    # Use HEROES localized names + 'raw' keys in NAME_TO_ID (already built in opendota_client)
    # We’ll just check localized_name occurrences for portraits.
    for hid, info in HEROES.items():
        ln = info.get("localized_name") or ""
        key = _norm(ln)
        if key and key in normed:
            found.append(hid)
    # Dedup & cap
    out = []
    for h in found:
        if h not in out:
            out.append(h)
        if len(out) >= 3:
            break
    return out


@cl.on_chat_start
async def on_chat_start():
    chat_setup()
    # Load OpenDota hero metadata & build role presets (cached in memory)
    await init_heroes()
    await cl.Message(
        "Hi! I’m ready. You can chat normally, or try:\n"
        "`counterpicks: pudge, storm spirit role=offlane`\n"
        "Use the **Lock** buttons to add picks to your board."
    ).send()


@cl.on_chat_resume
def on_chat_resume(thread):
    chat_setup()
    chat_history = []
    for step in thread.get("steps", []):
        if step["type"] == "user_message":
            chat_history.append(HumanMessage(step["output"]))
        elif step["type"] == "assistant_message":
            chat_history.append(AIMessage(step["output"]))
    cl.user_session.set("chat_history", chat_history)



async def handle_counterpicks(user_text: str):
    """
    counterpicks: <enemy1, enemy2, ...> [role=offlane | role=Initiator,Durable]
    """
    # Extract enemies portion (strip optional role= parameter)
    raw = user_text.split(":", 1)[1]
    enemies_part = re.sub(r"\brole\s*=\s*[a-zA-Z, \-]+", "", raw)
    enemies = [x.strip() for x in enemies_part.split(",") if x.strip()]
    enemy_ids = resolve_hero_ids(enemies)
    if not enemy_ids:
        await cl.Message(
            "I couldn't resolve any enemy heroes. Try: `counterpicks: pudge, storm spirit`."
        ).send()
        return

    # Parse role param -> include_only set of hero IDs
    include_only, role_label = parse_role_param(raw, ROLE_PRESETS, ids_by_role_tags)

    # Exclude heroes already present on the (very simple) board or enemies
    bd = _board()
    exclude = set(enemy_ids) | set(bd["my"]) | set(bd.get("bans", [] or []))

    # Compute counters
    results = await counter_scores(enemy_ids, list(exclude), include_only=include_only)
    # keep reasonable sample size & cap to 5
    top = [r for r in results if r[2] > 200][:5]

    if not top:
        await cl.Message("No strong candidates found with current filters. Try relaxing the role filter.").send()
        return

    # Build images + lines + actions
    elements = []
    lines = []
    actions: List[Action] = []
    for hid, score, samples in top:
        nm = hero_name(hid)
        img = HERO_IMG.get(hid)
        if img:
            elements.append(cl.Image(url=img, name=nm, display="side"))
        lines.append(f"**{nm}** — counter score: `{score:.2f}` (samples: {samples})")
        actions.append(Action(name="lock_in", value=str(hid), label=f"Lock {nm}"))

    expl = "Counters based on OpenDota matchup winrates, weighted by sample size"
    content = "\n".join([expl + role_label, "", *lines])
    await cl.Message(content, elements=elements, actions=actions).send()


@cl.action_callback("lock_in")
async def on_lock_in(action: Action):
    """Handle click → add to 'my' picks, re-render board."""
    try:
        hid = int(action.value)
    except Exception:
        await cl.Message("Could not parse selection.").send()
        return

    bd = _board()
    new_bd = lock_in(bd, hid)
    _set_board(new_bd)
    await cl.Message(f"Locked **{hero_name(hid)}** into **My Picks**.").send()
    await _render_board()



@cl.on_message
async def main(message: cl.Message):
    """
    Called for every user message.
    If it's a draft-coach command (`counterpicks:`), handle that path.
    Otherwise, stream the LLM agent and attach hero portraits when mentioned.
    """
    user_message = message.content.strip()

    # Draft Coach fast-path
    if user_message.lower().startswith("counterpicks:"):
        await handle_counterpicks(user_message)
        # Also keep conversation history updated for continuity
        cl.user_session.get("chat_history").append(HumanMessage(user_message))
        cl.user_session.get("chat_history").append(AIMessage("Shown counter picks above."))
        return

    # ---- Normal LLM streaming path (unchanged logic) ----
    cl.user_session.get("chat_history").append(HumanMessage(user_message))
    llm_agent = cl.user_session.get("llm_agent")
    assistant_message = ""
    tmp_message = cl.Message("")

    tool_responses: List[ToolMessage] = []

    async for event in llm_agent.astream_events(
        {
            "user_message": user_message,
            "chat_history": cl.user_session.get("chat_history"),
        },
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        if event["event"] == "on_chat_model_stream":
            await tmp_message.stream_token(token=event["data"]["chunk"].content)
            assistant_message += event["data"]["chunk"].content
        elif event["event"] == "on_chat_model_end" and event["data"]["output"].tool_calls:
            for tool_call in event["data"]["output"].tool_calls:
                tool_to_run = tools_mapping[tool_call["name"]]
                tool_args = tool_call["args"]
                tool_response = ToolMessage(content=tool_to_run(**tool_args), tool_call_id=tool_call["id"])
                tool_responses.append(tool_response)

    # If there are tool responses, run agent again to finalize
    if tool_responses:
        cl.user_session.get("chat_history").extend(tool_responses)
        async for event in llm_agent.astream_events(
            {
                "user_message": user_message,
                "chat_history": cl.user_session.get("chat_history"),
            },
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            if event["event"] == "on_chat_model_stream":
                await tmp_message.stream_token(token=event["data"]["chunk"].content)
                assistant_message += event["data"]["chunk"].content

    # Attach up to 3 hero portraits mentioned in the LLM text
    hero_elements = []
    for hid in _mentioned_hero_ids_from_text(assistant_message):
        img = HERO_IMG.get(hid)
        if img:
            hero_elements.append(cl.Image(url=img, name=hero_name(hid), display="side"))

    tmp_message.content = assistant_message
    await tmp_message.send(elements=hero_elements if hero_elements else None)

    cl.user_session.get("chat_history").append(AIMessage(assistant_message))


# Local runner
if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
