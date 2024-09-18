import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()
uri =f"mongodb+srv://eduvall9405:<{os.getenv('DATABASEPASS')}>@cluster0.ktfps.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def connect():
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client['lobby_database']  # Access the specific database for lobbies
    except Exception as e:
        print(e)
        return None

# Create a new lobby
def create_lobby(title, players_max, tags, uid, display_name):
    db = connect()
    if not db:
        return "Failed to connect to the database."
    
    try:
        lobby_data = {
            "title": title,
            "playersJoin": 1,
            "playersMax": players_max,
            "tags": tags,
            "uid": uid,
            "playersInLobby": [{"uid": uid, "display_name": display_name}],
            "displayName": display_name
        }
        result = db.lobbys.insert_one(lobby_data)
        return db.lobbys.find_one({"_id": result.inserted_id})  # Return the newly created lobby details
    except Exception as e:
        return f"Error creating lobby: {e}"

# Join an existing lobby
def join_lobby(lobby_id, uid, display_name):
    db = connect()
    if not db:
        return "Failed to connect to the database."
    
    try:
        lobby = db.lobbys.find_one({"_id": ObjectId(lobby_id)})
        if lobby:
            players_in_lobby = lobby["playersInLobby"]
            players_in_lobby.append({"uid": uid, "display_name": display_name})
            db.lobbys.update_one(
                {"_id": ObjectId(lobby_id)},
                {"$set": {"playersInLobby": players_in_lobby}, "$inc": {"playersJoin": 1}}
            )
            return db.lobbys.find_one({"_id": ObjectId(lobby_id)})
        else:
            return "Lobby not found."
    except Exception as e:
        return f"Error joining lobby: {e}"

# Leave an existing lobby
def leave_lobby(lobby_id, uid, display_name):
    db = connect()
    if not db:
        return "Failed to connect to the database."
    
    try:
        lobby = db.lobbys.find_one({"_id": ObjectId(lobby_id)})
        if lobby:
            players_in_lobby = lobby["playersInLobby"]
            players_in_lobby = [player for player in players_in_lobby if player["uid"] != uid or player["display_name"] != display_name]
            db.lobbys.update_one(
                {"_id": ObjectId(lobby_id)},
                {"$set": {"playersInLobby": players_in_lobby}, "$inc": {"playersJoin": -1}}
            )
            return db.lobbys.find_one({"_id": ObjectId(lobby_id)})
        else:
            return "Lobby not found."
    except Exception as e:
        return f"Error leaving lobby: {e}"

# Retrieve all lobbies
def get_all_lobbies():
    db = connect()
    if not db:
        return "Failed to connect to the database."
    
    try:
        lobbies = list(db.lobbys.find())
        return lobbies
    except Exception as e:
        return f"Error fetching lobbies: {e}"

# Close (delete) a lobby
def close_lobby(lobby_id):
    db = connect()
    if not db:
        return "Failed to connect to the database."
    
    try:
        result = db.lobbys.delete_one({"_id": ObjectId(lobby_id)})
        if result.deleted_count == 1:
            return "Lobby closed successfully."
        else:
            return "Lobby not found."
    except Exception as e:
        return f"Error closing lobby: {e}"

# Get details of a specific lobby
def get_lobby_details(lobby_id):
    db = connect()
    if not db:
        return "Failed to connect to the database."
    
    try:
        lobby = db.lobbys.find_one({"_id": ObjectId(lobby_id)})
        if lobby:
            return lobby
        else:
            return "Lobby not found."
    except Exception as e:
        return f"Error fetching lobby details: {e}"

