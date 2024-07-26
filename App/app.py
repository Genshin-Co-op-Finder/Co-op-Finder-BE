import json
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def connect():
    try:
        database = mysql.connector.connect(
            host="localhost",
            user=os.getenv('DATABASEUSER'),
            password=os.getenv('DATABASEPAS'),
            database="genshinfinder"
        )
        cursor = database.cursor(dictionary=True)
        return database, cursor
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None, None

def create_lobby(title, players_max, tags, uid, display_name):
    database, cursor = connect()
    if not cursor:
        return "Failed to connect to the database."
        
    try:
        json_tags = json.dumps(tags)
        json_uids = json.dumps([{"uid": uid, "display_name": display_name}])
        cursor.execute(
            "INSERT INTO lobbys (title, playersJoin, playersMax, tags, uid, playersInLobby, displayName) VALUES(%s, 1, %s, %s, %s, %s, %s)",
            (title, players_max, json_tags, uid, json_uids, display_name)
        )
        database.commit()

        cursor.execute("SELECT * FROM lobbys WHERE uid = %s", (uid,))
        lobby_details = cursor.fetchall()
        return lobby_details[0]
    except mysql.connector.Error as err:
        return f"Error executing query: {err}"
    finally:
        cursor.close()
        database.close()

def join_lobby(lobby_id, uid, display_name):
    database, cursor = connect()
    if not cursor:
        return "Failed to connect to the database." 
    
    try:
        cursor.execute("SELECT * FROM lobbys WHERE id = %s", (lobby_id,))
        lobby_details = cursor.fetchone()
        if lobby_details:
            player_list = json.loads(lobby_details["playersInLobby"])
            player_list.append({"uid": uid, "display_name": display_name})
            json_uids = json.dumps(player_list)
            cursor.execute(
                "UPDATE lobbys SET playersInLobby = %s, playersJoin = playersJoin + 1 WHERE id = %s",
                (json_uids, lobby_id)
            )
            database.commit()
        else:
            return "Lobby not found."
    except mysql.connector.Error as err:
        return f"Error executing query: {err}"
    finally:
        cursor.close()
        database.close()

def leave_lobby(lobby_id, uid, display_name):
    database, cursor = connect()
    if not cursor:
        return "Failed to connect to the database."
    
    try:
        cursor.execute("SELECT * FROM lobbys WHERE id = %s", (lobby_id,))
        lobby_details = cursor.fetchone()
        if lobby_details:
            player_list = json.loads(lobby_details["playersInLobby"])
            player_list = [player for player in player_list if player["uid"] != uid or player["display_name"] != display_name]
            json_uids = json.dumps(player_list)
            cursor.execute(
                "UPDATE lobbys SET playersInLobby = %s, playersJoin = playersJoin - 1 WHERE id = %s",
                (json_uids, lobby_id)
            )
            database.commit()
        else:
            return "Lobby not found."
    except mysql.connector.Error as err:
        return f"Error executing query: {err}"
    finally:
        cursor.close()
        database.close()

def get_all_lobbies():
    database, cursor = connect()
    if not cursor:
        return "Failed to connect to the database."
    
    try:
        cursor.execute("SELECT * FROM lobbys")
        lobbies = cursor.fetchall()
        return lobbies
    except mysql.connector.Error as err:
        return f"Error executing query: {err}"
    finally:
        cursor.close()
        database.close()

def close_lobby(lobby_id):
    database, cursor = connect()
    if not cursor:
        return "Failed to connect to the database."
    
    try:              
        cursor.execute("DELETE FROM lobbys WHERE id = %s", (lobby_id,))
        database.commit()
    except mysql.connector.Error as err:
        return f"Error executing query: {err}"
    finally:
        cursor.close()
        database.close()

def get_lobby_details(lobby_id):
    database, cursor = connect()
    if not cursor:
        return "Failed to connect to the database."
    
    try:
        cursor.execute("SELECT * FROM lobbys WHERE id = %s", (lobby_id,))
        lobby_details = cursor.fetchone()
        return lobby_details
    except mysql.connector.Error as err:
        return f"Error executing query: {err}"
    finally:
        cursor.close()
        database.close()


print(os.getenv('DATABASEPAS'))