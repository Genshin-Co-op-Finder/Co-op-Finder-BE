from flask import Flask, request
from flask_restful import Resource, Api
from flask_socketio import SocketIO, emit
from app import get_all_lobbies, create_lobby, close_lobby, join_lobby, get_lobby_details, leave_lobby

app = Flask("co-opFinder")
api = Api(app)
socketio = SocketIO(app)

class GetAvailableLobbies(Resource):
    def get(self):
        lobbies = get_all_lobbies()
        return lobbies

class UpdateLobbies(Resource):
    def delete(self):
        lobby_id = request.args.get('id')
        if not lobby_id:
            return {'error': 'Lobby ID is required'}, 400
        
        close_lobby(lobby_id)
        all_lobbies = get_all_lobbies()
        if isinstance(all_lobbies, str):
            return all_lobbies, 400
        socketio.emit('updateLobbies', all_lobbies)
        return {'message': f'Lobby {lobby_id} closed', 'all_lobbies': all_lobbies}, 200
    
    def post(self):
        required_params = ['title', 'players_max', 'tags', 'uid', 'display_name']
        missing_params = [param for param in required_params if not request.args.get(param)]
        if missing_params:
            return {'error': f'Missing required parameters: {", ".join(missing_params)}'}, 400
        
        title = request.args.get('title')
        players_max = request.args.get('players_max')
        tags = request.args.get('tags')
        uid = request.args.get('uid')
        display_name = request.args.get('display_name')

        new_lobby = create_lobby(title, players_max, tags, uid, display_name)
        if isinstance(new_lobby, str):
            return new_lobby, 400
        
        all_lobbies = get_all_lobbies()
        if isinstance(all_lobbies, str):
            return all_lobbies, 400
        socketio.emit('updateLobbies', all_lobbies)
        return new_lobby, 201

class LobbyParticipation(Resource):
    def patch(self):
        required_params = ['id', 'uid', 'display_name']
        missing_params = [param for param in required_params if not request.args.get(param)]
        if missing_params:
            return {'error': f'Missing required parameters: {", ".join(missing_params)}'}, 400 
        
        lobby_id = request.args.get('id')
        uid = request.args.get('uid')
        display_name = request.args.get('display_name')
        lobby = get_lobby_details(lobby_id)
        if isinstance(lobby, str):
            return lobby, 400
        if lobby['playersJoin'] == lobby['playersMax']:
            return {'error': 'Lobby is full or unavailable'}, 400
        else:
            join_lobby(lobby_id, uid, display_name)
        lobby_details = get_lobby_details(lobby_id)
        
        if isinstance(lobby_details, str):
            return lobby_details, 400
        else:
            socketio.emit('updateCurrentLobby', lobby_details)
            return lobby_details, 200
        
    def get(self):
        required_params = ['id', 'uid', 'display_name']
        missing_params = [param for param in required_params if not request.args.get(param)]
        if missing_params:
            return {'error': f'Missing required parameters: {", ".join(missing_params)}'}, 400 
        
        lobby_id = request.args.get('id')
        uid = request.args.get('uid')
        display_name = request.args.get('display_name')

        leave_lobby(lobby_id, uid, display_name)
        lobby_details = get_lobby_details(lobby_id)
        
        if isinstance(lobby_details, str):
            return lobby_details, 400
        else:
            socketio.emit('updateCurrentLobby', lobby_details)
            return lobby_details, 200

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

api.add_resource(GetAvailableLobbies, '/get_available_lobbies')
api.add_resource(UpdateLobbies, '/update_lobbies')
api.add_resource(LobbyParticipation, '/lobby_participation')

if __name__ == '__main__':
    socketio.run(app, debug=True)
