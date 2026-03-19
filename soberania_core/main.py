import os
import sys

# Add the project root to the python path so imports work correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from soberania_core.database import init_db, get_db_connection
from soberania_core.engine_economica import EngineEconomica
from soberania_core.agentes_brain import Agente

def setup_initial_state():
    print("Setting up initial state...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Country
    cursor.execute('''
        INSERT INTO countries (name, ruler_title, gdp, treasury, population, stability, inflation, unemployment)
        VALUES ('Republica de Nova Terra', 'Presidente', 1000000.0, 50000.0, 5000000, 60.0, 5.0, 8.0)
    ''')
    country_id = cursor.lastrowid

    # Create Agent
    cursor.execute('''
        INSERT INTO agents (country_id, name, role, ambition, loyalty, fear, ideology)
        VALUES (?, 'Marcus Viana', 'Ministro da Economia', 75.0, 60.0, 40.0, 'Capitalismo Liberal')
    ''', (country_id,))
    agent_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return country_id, agent_id

def main():
    print("Inicializando SOBERANIA EMERGENTE v1.0...")

    # 1. Initialize DB
    init_db()

    # Check if we already have data to avoid duplicate inserts on multiple runs
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM countries LIMIT 1")
    row = cursor.fetchone()
    if row is None:
        country_id, agent_id = setup_initial_state()
    else:
        country_id = row['id']
        cursor.execute("SELECT id FROM agents WHERE country_id = ? LIMIT 1", (country_id,))
        agent_id = cursor.fetchone()['id']
    conn.close()

    print(f"País ID: {country_id}, Agente ID: {agent_id}")

    # 2. Process first turn
    engine = EngineEconomica()
    engine.processar_turno()

    # 3. Instantiate Agent and request initial report
    ministro = Agente(agent_id)
    print("\n[Relatório Inicial do Ministro da Economia]")
    resposta = ministro.pensar("Faça um relatório inicial da economia do país.")
    print(f"Marcus Viana diz:\n{resposta}\n")

if __name__ == '__main__':
    main()
