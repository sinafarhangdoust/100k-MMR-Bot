import chainlit as cl
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agents.agents import get_llm_agent
from tools import tools_mapping
from tools.opendota_client import init_heroes, resolve_hero_ids, counter_scores, HERO_IMG, HEROES

#TODO Change this to use the SCRAPER method
def hero_name(hid: int) -> str:
    return HEROES[hid]["localized_name"]

@cl.on_chat_start
async def on_start():
    await init_heroes()
    await cl.Message("Draft Coach ready. Type:\n`counterpicks: pudge, storm spirit`\nI’ll show top counters + pics.").send()

@cl.on_message
async def on_message(msg: cl.Message):
    text = msg.content.strip().lower()
    if text.startswith("counterpicks:"):
        # parse enemy list
        raw = text.split("counterpicks:", 1)[1]
        enemies = [x.strip() for x in raw.split(",") if x.strip()]
        enemy_ids = resolve_hero_ids(enemies)
        if not enemy_ids:
            return await cl.Message("I couldn't resolve any enemy heroes. Try: `counterpicks: pudge, storm spirit`.").send()

        # exclude already picked heroes (here we only exclude enemies; extend as needed)
        exclude = set(enemy_ids)

        # compute counters (top 5)
        results = await counter_scores(enemy_ids, list(exclude))
        top = [r for r in results if r[2] > 200][:5]  # require some samples

        # build images + explanation
        elements = []
        lines = []
        for hid, score, samples in top:
            nm = hero_name(hid)
            img = HERO_IMG.get(hid)
            if img:
                elements.append(cl.Image(url=img, name=nm, display="side"))
            lines.append(f"**{nm}** — counter score: `{score:.2f}` (samples: {samples})")

        expl = (
            "Here are strong counters based on aggregated matchup winrates "
            "weighted by sample size (OpenDota)."
        )
        await cl.Message("\n".join([expl, "", *lines]), elements=elements).send()
        return




def chat_setup():
    llm_agent = get_llm_agent(model='gpt-4.1-mini', temperature=0.0)
    cl.user_session.set('llm_agent', llm_agent)
    cl.user_session.set('chat_history', [])
    # cl.user_session.set('langsmith_client', LangsmithClient())

@cl.password_auth_callback
def auth_callback(username: str, password: str):

    if (username, password) == ("admin", "admin"):
        return cl.User(identifier="admin", metadata={"role": "admin", "provider": "credentials"})
    else:
        return None


@cl.on_chat_start
def on_chat_start():
    chat_setup()


@cl.on_chat_resume
def on_chat_resume(thread):
    chat_setup()
    chat_history = []
    for step in thread.get('steps', []):
        if step['type'] == 'user_message':
            chat_history.append(HumanMessage(step['output']))
        elif step['type'] == 'assistant_message':
            chat_history.append(AIMessage(step['output']))

    cl.user_session.set('chat_history', chat_history)


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back an intermediate response from the tool, followed by the final answer.

    Args:
        message: The user's message.

    Returns:
        None.
    """
    # langsmith_extra = {
    #    "project_name": os.getenv('LANGSMITH_PROJECT'),
    #    "metadata": {"thread_id": cl.context.session.thread_id}
    # }
    user_message = message.content
    cl.user_session.get('chat_history').append(HumanMessage(user_message))
    llm_agent = cl.user_session.get('llm_agent')
    assistant_message = ""
    tmp_message = cl.Message("")
    tool_responses = []
    async for event in llm_agent.astream_events(
        {
            'user_message': user_message,
            'chat_history': cl.user_session.get('chat_history')
        },
        config=RunnableConfig(
            callbacks=[cl.LangchainCallbackHandler()],
            # configurable={"langsmith_extra": langsmith_extra},
        )
    ):
        if event['event'] == 'on_chat_model_stream':
            await tmp_message.stream_token(token=event['data']['chunk'].content)
            assistant_message += event['data']['chunk'].content
        elif event['event'] == 'on_chat_model_end' and event['data']['output'].tool_calls:
            for tool_call in event['data']['output'].tool_calls:
                tool_to_run = tools_mapping[tool_call['name']]
                tool_args = tool_call['args']
                tool_response = ToolMessage(content=tool_to_run(**tool_args), tool_call_id=tool_call['id'])
                tool_responses.append(tool_response)

    # call again the llm agent if there are any tool_responses
    if tool_responses:

        cl.user_session.get('chat_history').extend(tool_responses)
        async for event in llm_agent.astream_events(
                {
                    'user_message': user_message,
                    'chat_history': cl.user_session.get('chat_history')
                },
                config=RunnableConfig(
                    callbacks=[cl.LangchainCallbackHandler()],
                    # configurable={"langsmith_extra": langsmith_extra},
                )
        ):
            if event['event'] == 'on_chat_model_stream':
                await tmp_message.stream_token(token=event['data']['chunk'].content)
                assistant_message += event['data']['chunk'].content



    tmp_message.content = assistant_message
    await tmp_message.send()


    cl.user_session.get('chat_history').append(AIMessage(assistant_message))


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)