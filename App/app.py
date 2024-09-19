import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()
uri =f"mongodb+srv://eduvall9405:{os.getenv('DATABASEPASS')}@cluster0.ktfps.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def connect():
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client['lobby_database'] 
    except Exception as e:
        print(e)
        return None


def create_lobby(title, players_max, tags, uid, display_name):
    db = connect()
    if db is None:
        return "Failed to connect to the database."
    
    try:
        if (db.lobbies.find_one({"_id": uid}) is None):
            lobby_data = {
            "_id":uid,
            "title": title,
            "playersJoin": 1,
            "playersMax": players_max,
            "tags": tags,
            "uid": uid,
            "playersInLobby": [{"uid": uid, "display_name": display_name}],
            "displayName": display_name
        }
            db.lobbies.insert_one(lobby_data)
            return db.lobbies.find_one({"_id": uid})  
        else:
         return "Lobby already created using that UID"
   
    except Exception as e:
        return f"Error creating lobby: {e}"

def join_lobby(lobby_id, uid, display_name):
    db = connect()
    if db is None:
        return "Failed to connect to the database."
    
    try:
        lobby = db.lobbies.find_one({"_id": lobby_id})
        if lobby:
            players_in_lobby = lobby["playersInLobby"]
            players_in_lobby.append({"uid": uid, "display_name": display_name})
            db.lobbies.update_one(
                {"_id": lobby_id},
                {"$set": {"playersInLobby": players_in_lobby}, "$inc": {"playersJoin": 1}}
            )
            return db.lobbies.find_one({"_id": lobby_id})
        else:
            return "Lobby not found."
    except Exception as e:
        return f"Error joining lobby: {e}"

def leave_lobby(lobby_id, uid, display_name):
    db = connect()
    if db is None:
        return "Failed to connect to the database."
    
    try:
        lobby = db.lobbies.find_one({"_id": lobby_id})
        if lobby:
            players_in_lobby = lobby["playersInLobby"]
            players_in_lobby = [player for player in players_in_lobby if player["uid"] != uid or player["display_name"] != display_name]
            db.lobbies.update_one(
                {"_id": lobby_id},
                {"$set": {"playersInLobby": players_in_lobby}, "$inc": {"playersJoin": -1}}
            )
            return db.lobbies.find_one({"_id": lobby_id})
        else:
            return "Lobby not found."
    except Exception as e:
        return f"Error leaving lobby: {e}"

def get_all_lobbies():
    db = connect()
    if db is None:
        return "Failed to connect to the database."
    
    try:
        lobbies = list(db.lobbies.find())
        return lobbies
    except Exception as e:
        return f"Error fetching lobbies: {e}"

def close_lobby(lobby_id):
    db = connect()
    if db is None:
        return "Failed to connect to the database."
    
    try:
        result = db.lobbies.delete_one({"_id": lobby_id})
        if result.deleted_count == 1:
            return "Lobby closed successfully."
        else:
            return "Lobby not found."
    except Exception as e:
        return f"Error closing lobby: {e}"

# Get details of a specific lobby
def get_lobby_details(lobby_id):
    db = connect()
    if db is None:
        return "Failed to connect to the database."
    
    try:
        lobby = db.lobbies.find_one({"_id": lobby_id})
        if lobby:
            return lobby
        else:
            return "Lobby not found."
    except Exception as e:
        return f"Error fetching lobby details: {e}"

