from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import chainlit as cl

from hero_db import HeroDB


def get_hero(hero_name: str):
    hero_db = HeroDB()
    return hero_db.heroes.get(hero_name)


def get_llm_agent(model, temperature):
    llm = ChatOpenAI(model=model, temperature=temperature, streaming=True)
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a DOTA 2 expert. You must answer to the user's questions using the available tool `get_hero` to retrieve the information regarding the hero. Always generate the hero names in lower case"),
            ("human", "User message: {user_message} \n\n Chat History: {chat_history}")

        ]
    )
    llm_with_tools = llm.bind_tools([get_hero])
    return prompt_template | llm_with_tools


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