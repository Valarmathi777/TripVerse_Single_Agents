import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from .prompts import PLAN_PROMPT, RECOMMEND_PROMPT

load_dotenv()

# Groq client initialization pointing to the Groq base URL
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)


def generate_plan(destination, days, interests, must_include=""):

    prompt = f"""
    {PLAN_PROMPT}

    Destination:
    {destination}

    Days:
    {days}

    Interests:
    {interests}
    """
    if must_include:
        prompt += f"\nSpecific places/activities to include:\n{must_include}\n"

    # Generate content using Llama-3.3-70b-versatile on Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    text = response.choices[0].message.content
    return json.loads(text)


def generate_recommendations(destination, interests):

    prompt = f"""
    {RECOMMEND_PROMPT}

    Destination:
    {destination}

    Interests:
    {interests}
    """

    # Generate content using Llama-3.3-70b-versatile on Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    text = response.choices[0].message.content
    return json.loads(text)

