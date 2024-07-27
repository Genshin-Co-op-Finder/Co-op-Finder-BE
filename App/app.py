import json
import uuid
import os
import boto3
from boto3.dynamodb.conditions import Key

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')

dynamodb = boto3.resource('dynamodb', 
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_REGION)

table = dynamodb.Table(DYNAMODB_TABLE_NAME)
client = boto3.client('dynamodb',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=AWS_REGION)

def create_lobby(title, players_max, tags, uid, display_name):
    try:
        item = {
            'id': str(uuid.uuid4()),  
            'title': title,
            'playersJoin': 1,
            'playersMax': players_max,
            'tags': tags,
            'uid': uid,
            'playersInLobby': [{'uid': uid, 'displayName': display_name}],
            'displayName': display_name
        }
        table.put_item(Item=item)
        return item
    except Exception as e:
        return f"Error creating lobby: {e}"

def join_lobby(id, uid, display_name):
    try:
        response = table.get_item(Key={'id': id})
        if 'Item' not in response:
            return "Lobby not found."

        lobby = response['Item']
        if lobby['playersJoin'] >= lobby['playersMax']:
            return "Lobby is full."

        lobby['playersInLobby'].append({'uid': uid, 'displayName': display_name})
        lobby['playersJoin'] += 1

        table.update_item(
            Key={'id': id},
            UpdateExpression="set playersInLobby=:p, playersJoin=:j",
            ExpressionAttributeValues={
                ':p': lobby['playersInLobby'],
                ':j': lobby['playersJoin']
            }
        )
        return lobby
    except Exception as e:
        return f"Error joining lobby: {e}"

def leave_lobby(id, uid):
    try:
        response = table.get_item(Key={'id': id})
        if 'Item' not in response:
            return "Lobby not found."

        lobby = response['Item']
        lobby['playersInLobby'] = [p for p in lobby['playersInLobby'] if p['uid'] != uid]
        lobby['playersJoin'] -= 1

        table.update_item(
            Key={'id': id},
            UpdateExpression="set playersInLobby=:p, playersJoin=:j",
            ExpressionAttributeValues={
                ':p': lobby['playersInLobby'],
                ':j': lobby['playersJoin']
            }
        )
        return lobby
    except Exception as e:
        return f"Error leaving lobby: {e}"

def get_all_lobbies():
    try:
        response = table.scan()
        return response.get('Items', [])
    except Exception as e:
        return f"Error fetching lobbies: {e}"

def close_lobby(id):
    try:
        table.delete_item(Key={'id': id})
        return f"Lobby {id} closed successfully."
    except Exception as e:
        return f"Error closing lobby: {e}"

def get_lobby_details(id):
    try:
        response = table.get_item(Key={'id': id})
        if 'Item' not in response:
            return "Lobby not found."
        return response['Item']
    except Exception as e:
        return f"Error fetching lobby details: {e}"
