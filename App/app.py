import json
import uuid

lobbys = {}

def create_lobby(title, players_max, tags, uid, display_name):
       
        json_tags = json.dumps(tags)
        json_uids = json.dumps([{"uid": uid, "display_name": display_name}])
        id = str(uuid.uuid4())
        lobbys[id] = {
            "id" : id,
            "title": title,
            "playersJoin": 1,
            "playersMax": players_max,
            "tags": json_tags,
            "uid": uid,
            "playersInLobby": json_uids,
            "displayName": display_name
        }
        lobby_details = lobbys[id]
        return lobby_details

def join_lobby(lobby_id, uid, display_name):
 
        lobby_details = lobbys[lobby_id]
        if lobby_details:
            player_list = json.loads(lobby_details["playersInLobby"])
            player_list.append({"uid": uid, "display_name": display_name})
            json_uids = json.dumps(player_list)
            lobby_details["playersInLobby"] = json_uids
            lobby_details["playersJoin"] += 1 
        else:
            return "Lobby not found."
    
def leave_lobby(lobby_id, uid, display_name):
  
        lobby_details = lobbys[lobby_id]
        if lobby_details:
            player_list = json.loads(lobby_details["playersInLobby"])
            player_list = [player for player in player_list if player["uid"] != uid or player["display_name"] != display_name]
            json_uids = json.dumps(player_list)
            lobby_details["playersInLobby"] = json_uids
            lobby_details["playersJoin"] -= 1 
        else:
            return "Lobby not found."

def get_all_lobbies(): 
    return lobbys

def close_lobby(lobby_id):
    del lobbys[lobby_id]

def get_lobby_details(lobby_id):
    return lobbys[lobby_id]


