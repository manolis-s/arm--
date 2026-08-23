import sqlite3
import pandas as pd
from player_clusters import get_fantasy_clusters

def setup_db(db_name = "fantasy.db"):
    conn = sqlite3.connect(db_name)
    return conn
def update_player_clusters_table():
    df = get_fantasy_clusters()
    if df is None or df.empty:
        print("No data to save")
        return 
    conn = setup_db()

    try:
        df.to_sql('players_roster', conn, if_exists='replace', index = False)
        print(f"{len(df)} players inserted to db")
        test_df = pd.read_sql("SELECT PLAYER_NAME, TEAM_ABBREVIATION, CLUSTER_ID FROM players_roster LIMIT 5", conn)
        print(test_df)

    except Exception as e:
        print(f'error: {e}')
    finally:
        conn.close()

if __name__ == "__main__":
    update_player_clusters_table()