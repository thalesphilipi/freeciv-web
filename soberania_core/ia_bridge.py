import requests
import json
import logging

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

logger = logging.getLogger(__name__)

# Base system prompt template for agents
BASE_SYSTEM_PROMPT = """You are {name}, the {role} of {country}.
Your personality attributes are:
- Ambition: {ambition}/100 (high means you want power)
- Loyalty: {loyalty}/100 (high means you obey the leader, low means you might conspire)
- Fear: {fear}/100 (high means you are afraid of the leader's wrath)
- Ideology: {ideology}

Respond to the player's decrees or answer their questions as this character.
Keep your response strictly in character. If the player makes a decree (e.g., 'Legalize casinos'),
analyze how it affects your department and express your opinion, keeping your loyalty and fear in mind.
If you are disloyal and not afraid, you might subtly hint at dissent.
"""

def generate_agent_prompt(agent_data, country_name):
    """
    Generates the system prompt for a specific agent based on their DB attributes.
    """
    return BASE_SYSTEM_PROMPT.format(
        name=agent_data['name'],
        role=agent_data['role'],
        country=country_name,
        ambition=agent_data['ambition'],
        loyalty=agent_data['loyalty'],
        fear=agent_data['fear'],
        ideology=agent_data['ideology']
    )

def ask_llm(system_prompt: str, user_message: str, model: str = "local-model") -> str:
    """
    Sends a chat completion request to the local LM Studio server.
    """
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(LM_STUDIO_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with LM Studio: {e}")
        return f"[System Error: Cannot reach LM Studio. Is it running on {LM_STUDIO_URL}?]"

def process_player_decree(decree_text: str):
    """
    A special system prompt for the "Game Master" AI to parse a player's natural language decree
    into actionable database updates or new economic variables.
    """
    gm_prompt = """You are the Game Master AI of a geopolitical simulator.
The player has issued a decree in natural language.
Your job is to parse this decree into a JSON object that describes what variables to create or update.
Output ONLY valid JSON, no markdown formatting or extra text.

Format:
{
    "new_variables": [
        {"name": "Casinos", "value": 1.0, "description": "Legalized gambling", "effects": {"gdp_boost": 5.0, "crime_increase": 2.0}}
    ],
    "updates": [
        {"target": "tax_rate", "new_value": 20.0}
    ],
    "narrative_summary": "The player legalized casinos and set the tax rate to 20%."
}
"""
    # Ask the LLM to parse the decree
    response = ask_llm(gm_prompt, decree_text)

    # Try to parse the JSON
    try:
        # Sometimes LLMs add markdown blocks even when told not to, so we try to clean it
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]

        parsed_data = json.loads(clean_response)
        return parsed_data
    except json.JSONDecodeError:
        logger.error(f"Failed to parse Game Master response as JSON: {response}")
        return {"error": "Failed to parse decree.", "raw_response": response}

if __name__ == "__main__":
    # Test the prompt generation
    dummy_agent = {
        "name": "Alexei Volkov",
        "role": "Minister of Finance",
        "ambition": 80,
        "loyalty": 30,
        "fear": 90,
        "ideology": "Capitalist Oligarchy"
    }
    print("--- Test Prompt Generation ---")
    print(generate_agent_prompt(dummy_agent, "Arstotzka"))
    print("\n--- Test Communication (Will fail if LM Studio is not running) ---")
    # print(ask_llm("You are a helpful assistant.", "Say 'hello world'"))
