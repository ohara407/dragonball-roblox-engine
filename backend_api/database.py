"""
Banco de dados SQLite leve para armazenar os dados dos jogadores do Roblox.
Utiliza a biblioteca padrão sqlite3 com serialização JSON dos dados do jogador.
"""
import sqlite3
import json
import os
from typing import Optional
from models import PlayerStats

DB_PATH = os.path.join(os.path.dirname(__file__), "dragonball_game.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            data TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_player(user_id: int) -> Optional[PlayerStats]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM players WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        player_dict = json.loads(row["data"])
        return PlayerStats(**player_dict)
    return None

def save_player(player: PlayerStats) -> PlayerStats:
    conn = get_connection()
    cursor = conn.cursor()
    player_json = player.model_dump_json() if hasattr(player, "model_dump_json") else player.json()
    
    cursor.execute("""
        INSERT INTO players (user_id, username, data, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            data = excluded.data,
            updated_at = CURRENT_TIMESTAMP
    """, (player.user_id, player.username, player_json))
    
    conn.commit()
    conn.close()
    return player

def get_or_create_player(user_id: int, username: str) -> PlayerStats:
    player = get_player(user_id)
    if not player:
        player = PlayerStats(
            user_id=user_id,
            username=username,
            power_level=150,
            strength=25,
            defense=20,
            agility=20,
            ki=500.0,
            max_ki=500.0
        )
        save_player(player)
    return player
