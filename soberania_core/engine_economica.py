import sqlite3
import json
from soberania_core.database import get_db_connection

class EngineEconomica:
    def processar_turno(self):
        """
        Calculates economic changes (GDP growth, inflation, unemployment) based on formulas,
        and updates the database.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all countries
        cursor.execute("SELECT * FROM countries")
        countries = cursor.fetchall()

        for country in countries:
            country_id = country['id']
            gdp = country['gdp']
            treasury = country['treasury']
            stability = country['stability']
            inflation = country['inflation']
            unemployment = country['unemployment']

            # Simple formula logic (mock for the simulation)
            # Fetch dynamic economic variables to influence growth
            cursor.execute("SELECT * FROM economic_variables WHERE country_id = ?", (country_id,))
            eco_vars = cursor.fetchall()

            gdp_boost = 0.0
            stability_mod = 0.0
            inflation_mod = 0.0
            unemployment_mod = 0.0

            for var in eco_vars:
                if var['effects']:
                    try:
                        effects = json.loads(var['effects'])
                        gdp_boost += effects.get('gdp_boost', 0.0)
                        stability_mod += effects.get('stability_boost', 0.0)
                        inflation_mod += effects.get('inflation_increase', 0.0)
                        unemployment_mod += effects.get('unemployment_decrease', 0.0) * -1
                    except json.JSONDecodeError:
                        pass

            # Fetch laws
            cursor.execute("SELECT * FROM leis WHERE country_id = ? AND status = 'active'", (country_id,))
            leis = cursor.fetchall()

            for lei in leis:
                if lei['impacts']:
                    try:
                        impacts = json.loads(lei['impacts'])
                        gdp_boost += impacts.get('gdp_boost', 0.0)
                        stability_mod += impacts.get('stability_boost', 0.0)
                        inflation_mod += impacts.get('inflation_increase', 0.0)
                        unemployment_mod += impacts.get('unemployment_decrease', 0.0) * -1
                    except json.JSONDecodeError:
                        pass

            # Base growth
            new_gdp = gdp * (1 + 0.02 + (gdp_boost / 100))

            # Treasury based on GDP and tax rate (mocking a base tax rate)
            tax_rate = 0.15 # 15%
            new_treasury = treasury + (new_gdp * tax_rate) - (new_gdp * 0.10) # 10% expenses

            new_stability = min(100.0, max(0.0, stability + stability_mod))
            new_inflation = max(0.0, inflation + 0.1 + inflation_mod)
            new_unemployment = max(0.0, unemployment + unemployment_mod)

            cursor.execute('''
                UPDATE countries
                SET gdp = ?, treasury = ?, stability = ?, inflation = ?, unemployment = ?
                WHERE id = ?
            ''', (new_gdp, new_treasury, new_stability, new_inflation, new_unemployment, country_id))

            # Log the turn update
            cursor.execute('''
                INSERT INTO event_logs (tick, event_type, description, metadata)
                VALUES (
                    (SELECT COALESCE(MAX(tick), 0) + 1 FROM event_logs),
                    'economic_update',
                    ?,
                    ?
                )
            ''', (
                f"Economy updated for {country['name']}",
                json.dumps({
                    "gdp_change": new_gdp - gdp,
                    "treasury_change": new_treasury - treasury
                })
            ))

        conn.commit()
        conn.close()

if __name__ == '__main__':
    engine = EngineEconomica()
    engine.processar_turno()
    print("Economic engine turn processed.")
