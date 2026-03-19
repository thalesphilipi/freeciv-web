import sqlite3
import json
from soberania_core.database import get_db_connection
from soberania_core.ia_bridge import ask_llm

class Agente:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.load_data()

    def load_data(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE id = ?", (self.agent_id,))
        self.data = cursor.fetchone()

        if self.data:
            cursor.execute("SELECT * FROM countries WHERE id = ?", (self.data['country_id'],))
            self.country = cursor.fetchone()
        conn.close()

    def gerar_prompt(self):
        base_prompt = """You are {name}, the {role} of {country}.
Your personality attributes are:
- Ambition: {ambition}/100 (high means you want power)
- Loyalty: {loyalty}/100 (high means you obey the leader, low means you might conspire)
- Fear: {fear}/100 (high means you are afraid of the leader's wrath)
- Ideology: {ideology}

The current state of your country is:
- GDP: {gdp}
- Treasury: {treasury}
- Stability: {stability}
- Inflation: {inflation}
- Unemployment: {unemployment}

Respond to the player's decrees or answer their questions as this character.
Keep your response strictly in character. If the player makes a decree (e.g., 'Legalize casinos'),
analyze how it affects your department and express your opinion, keeping your loyalty and fear in mind.
If you are disloyal and not afraid, you might subtly hint at dissent.
"""
        return base_prompt.format(
            name=self.data['name'],
            role=self.data['role'],
            country=self.country['name'],
            ambition=self.data['ambition'],
            loyalty=self.data['loyalty'],
            fear=self.data['fear'],
            ideology=self.data['ideology'],
            gdp=self.country['gdp'],
            treasury=self.country['treasury'],
            stability=self.country['stability'],
            inflation=self.country['inflation'],
            unemployment=self.country['unemployment']
        )

    def pensar(self, mensagem_usuario: str):
        prompt = self.gerar_prompt()
        resposta = ask_llm(prompt, mensagem_usuario)

        # "Mundo Vivo": Conspiração Silenciosa
        if self.data['loyalty'] < 30 and self.data['fear'] < 50:
            print(f"[Conspiração Silenciosa] O agente {self.data['name']} está enviando mensagens para agentes estrangeiros.")
            # Mock de log de conspiração
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO event_logs (tick, event_type, description, metadata)
                VALUES (
                    (SELECT COALESCE(MAX(tick), 0) + 1 FROM event_logs),
                    'agent_action',
                    ?,
                    ?
                )
            ''', (
                f"{self.data['name']} plotted against the government.",
                json.dumps({"agent_id": self.agent_id, "action": "conspiracy"})
            ))
            conn.commit()
            conn.close()

        return resposta
