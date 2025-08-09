import chainlit as cl

from agents.agents import get_llm_agent


@cl.on_chat_start
def on_start():
    llm_agent = get_llm_agent(model='gpt-4.1-mini', temperature=0.0)
    cl.user_session.set('llm_agent', llm_agent)
    cl.user_session.set('chat_history', [])


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

    user_message = message.content
    llm_agent = cl.user_session.get('llm_agent')
    assistant_message = ""
    tmp_message = cl.Message("")
    async for event in llm_agent.astream_events(
        {
            'user_message': user_message,
            'chat_history': cl.user_session.get('chat_history')
        }
    ):
        if event['event'] == 'on_chat_model_stream':
            await tmp_message.stream_token(token=event['data']['chunk'].content)
            assistant_message += event['data']['chunk'].content

    tmp_message.content = assistant_message
    await tmp_message.send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)