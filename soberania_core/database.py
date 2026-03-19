import sqlite3
import json
from typing import Dict, Any, List

DB_PATH = 'soberania_core/simulation.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Countries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ruler_title TEXT,
            gdp REAL DEFAULT 0,
            treasury REAL DEFAULT 0,
            population INTEGER DEFAULT 0,
            stability REAL DEFAULT 50.0,
            inflation REAL DEFAULT 0.0,
            unemployment REAL DEFAULT 0.0
        )
    ''')

    # Agents table (Ministers, Mayors, Foreign Leaders)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            name TEXT NOT NULL,
            role TEXT NOT NULL, -- e.g., 'Minister of Defense', 'Mayor of Capital', 'Foreign Leader'
            ambition REAL DEFAULT 50.0,
            loyalty REAL DEFAULT 50.0,
            fear REAL DEFAULT 50.0,
            ideology TEXT,
            memory TEXT DEFAULT '[]', -- JSON array of important memories
            FOREIGN KEY (country_id) REFERENCES countries (id)
        )
    ''')

    # Economic Variables table (for dynamic creation like 'Casinos', 'State Crypto')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS economic_variables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            name TEXT NOT NULL,
            value REAL DEFAULT 0.0,
            description TEXT,
            effects TEXT, -- JSON string representing effects on GDP, stability, etc.
            FOREIGN KEY (country_id) REFERENCES countries (id),
            UNIQUE(country_id, name)
        )
    ''')

    # Laws table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            name TEXT NOT NULL,
            status TEXT NOT NULL, -- e.g., 'active', 'proposed', 'repealed'
            impacts TEXT, -- JSON string representing effects on variables
            FOREIGN KEY (country_id) REFERENCES countries (id)
        )
    ''')

    # International Relations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relacoes_internacionais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_a_id INTEGER,
            country_b_id INTEGER,
            status TEXT NOT NULL, -- e.g., 'peace', 'war', 'alliance'
            relations_score REAL DEFAULT 50.0,
            agreements TEXT, -- JSON string of active agreements
            FOREIGN KEY (country_a_id) REFERENCES countries (id),
            FOREIGN KEY (country_b_id) REFERENCES countries (id)
        )
    ''')

    # Event Logs table (for conversations, decisions, tick history)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tick INTEGER NOT NULL,
            event_type TEXT NOT NULL, -- e.g., 'player_command', 'agent_action', 'economic_update'
            description TEXT NOT NULL,
            metadata TEXT -- JSON string for additional data
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
