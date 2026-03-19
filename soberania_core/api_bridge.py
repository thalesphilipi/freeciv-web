from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import json
from soberania_core.database import get_db_connection
from soberania_core.ia_bridge import process_player_decree
from soberania_core.agentes_brain import Agente

app = FastAPI(title="Soberania Emergente API")

class DecreeRequest(BaseModel):
    decree_text: str
    country_id: int
    target_agent_id: int

@app.post("/decree")
def issue_decree(req: DecreeRequest):
    # Process decree using LM Studio as Game Master
    parsed_decree = process_player_decree(req.decree_text)

    if "error" in parsed_decree:
        raise HTTPException(status_code=500, detail="Failed to parse decree")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Store new economic variables
    if "new_variables" in parsed_decree:
        for var in parsed_decree["new_variables"]:
            cursor.execute('''
                INSERT INTO economic_variables (country_id, name, value, description, effects)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(country_id, name) DO UPDATE SET
                value=excluded.value, description=excluded.description, effects=excluded.effects
            ''', (req.country_id, var.get('name', ''), var.get('value', 0.0), var.get('description', ''), json.dumps(var.get('effects', {}))))

    # Store updates to existing variables
    if "updates" in parsed_decree:
        for update in parsed_decree["updates"]:
            target = update.get("target")
            val = update.get("new_value")
            if target and val is not None:
                # Basic protection for valid targets, e.g. tax_rate is a mock concept
                pass

    conn.commit()
    conn.close()

    # Query the targeted agent for reaction
    agente = Agente(req.target_agent_id)
    reaction = agente.pensar(req.decree_text)

    return {
        "status": "success",
        "parsed_decree": parsed_decree,
        "agent_reaction": reaction
    }
