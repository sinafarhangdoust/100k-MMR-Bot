import os
from typing import Any, Optional, List, Dict, Annotated, Literal
import requests

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable, RunnableSequence
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import MarkdownifyTransformer
import tiktoken

from constants import SCRAPER_SYSTEM_PROMPT


class SummaryInfo(BaseModel):
    adjectives: List[str] = Field(description="The adjectives that describe the hero, appearing on the top of the page.")
    num_legs: str | int = Field(description="The number of legs that the hero has.")
    roles: List[str] = Field(description="The roles of the hero.")
    summary: str = Field(description="The full summary of the hero that appears on the top of the page.")


class AttributeStats(BaseModel):
    attribute: str = Field(description="The name of the attribute. (Strength, Agility, Intelligence)")
    attribute_gain: str = Field(description="The gain per level for this attribute.")
    base_attribute: str = Field(description="The starting value of this attribute.")
    type: Literal['primary', 'secondary'] = Field(description="The classification of the attribute (primary/secondary). If it doesn't have primary attribute in the id of the element then it's secondary.")


class BasicStats(BaseModel):
    acquisition_range: str = Field(default=None, description="The range at which the unit acquires targets.")
    attack_animation: str = Field(default=None, description="The time taken for attack animation.")
    attack_range: str = Field(default=None, description="The maximum range at which the unit can attack.")
    attack_speed: str = Field(default=None, description="The unit's base attack speed. Not to be confused with BAT value.")
    attributes: List[AttributeStats] = Field(default=None, description="Dictionary of unit attributes (strength, agility, intelligence).")
    base_armor: str = Field(default=None, description="The unit's starting armor value.")
    base_average_damage: str = Field(default=None, description="The average damage dealt. Looks like (<number> Avg)")
    base_damage: str = Field(default=None, description="The minimum and maximum damage range.")
    base_health: int = Field(default=None, description="The unit's starting health.")
    base_health_regeneration: float = Field(default=None, description="The health regeneration rate per second.")
    base_magic_resistence: str = Field(default=None, description="The unit's base magic resistance percentage.")
    base_mana: int = Field(default=None, description="The unit's starting mana.")
    base_mana_regeneration: float = Field(default=None, description="The mana regeneration rate per second.")
    bound_radius: int = Field(default=None, description="The unit's bounding radius (hitbox size).")
    collision_size: int = Field(default=None, description="The unit's collision size (pathing size).")
    day_movement_speed: int = Field(default=None, description="The unit's movement speed during the day.")
    day_vision_range: int = Field(default=None, description="The vision range during the daytime.")
    # night_movement_speed: int = Field(default=None, description="The unit's movement speed during the night.")
    night_vision_range: int = Field(default=None, description="The vision range during nighttime.")
    projectile_speed: str = Field(default=None, description="The speed of projectiles.")
    turn_rate: Optional[str] = Field(default=None, description="The unit's turn rate (empty if not applicable).")


class Hero(BaseModel):
    summary_info: SummaryInfo
    basic_stats: BasicStats


class ExtractSchema(BaseModel):
    hero: Hero


def custom_agent(
    model: str,
    temperature: float,
    extract_schema
) -> RunnableSequence:
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    scraper_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", SCRAPER_SYSTEM_PROMPT),
            ("human", "Webpage element html: {html_element}")
        ]
    )
    structured_llm = llm.with_structured_output(extract_schema)
    llm_agent = scraper_prompt_template | structured_llm
    return llm_agent


def get_html(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> str:
    """
    Retrieve the HTML content of a given URL.

    Args:
        url: The URL to fetch HTML from
        headers: Optional dictionary of HTTP headers to send with the request
        timeout: Request timeout in seconds

    Returns:
        The HTML content as a string

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    if headers:
        default_headers.update(headers)

    try:
        response = requests.get(url, headers=default_headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        raise

def main():

    # retrieve the html content
    # html_content = get_html("https://liquipedia.net/dota2/Axe")
    loader = AsyncHtmlLoader(["https://liquipedia.net/dota2/Axe"])
    docs = loader.load()

    md = MarkdownifyTransformer(
        strip=[
            '<img>', '</img>', '<img', 'img', 'images'
            '<a>', '</a>', '<a', 'a',

        ]
    )
    converted_docs = md.transform_documents(docs)

    llm_scraper = custom_agent(
        model="gpt-4.1-nano",
        temperature=0,
        #endpoint="https://openrouter.ai/api/v1/",
        extract_schema=ExtractSchema
    )
    response = llm_scraper.invoke(
        {
            #"extract_schema": ExtractSchema.model_json_schema(),
            "md_content": converted_docs[0].page_content,
        }
    )
    print()


if __name__ == '__main__':
    main()

