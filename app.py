import chainlit as cl
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agents.agents import get_llm_agent
from tools import tools_mapping

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