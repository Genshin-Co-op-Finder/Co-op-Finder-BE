from flask import Flask, request
from flask_restful import Resource, Api
from flask_socketio import SocketIO
from app import create_lobby, join_lobby, leave_lobby, get_all_lobbies, close_lobby, get_lobby_details

app = Flask("co-opFinder")
api = Api(app)
socketio = SocketIO(app, async_mode='eventlet')

class GetAvailableLobbies(Resource):
    def get(self):
        lobbies = get_all_lobbies()
        return lobbies

class UpdateLobbies(Resource):
    def delete(self):
        id = request.args.get('id')
        if not id:
            return {'error': 'Lobby ID is required'}, 400
        
        close_lobby(id)
        all_lobbies = get_all_lobbies()
        socketio.emit('updateLobbies', all_lobbies)
        return {'message': f'Lobby {id} closed', 'all_lobbies': all_lobbies}
    
    def post(self):
        required_params = ['title', 'playersMax', 'tags', 'uid', 'displayName']
        missing_params = [param for param in required_params if not request.args.get(param)]
        if missing_params:
            return {'error': f'Missing required parameters: {", ".join(missing_params)}'}, 400
        
        title = request.args.get('title')
        players_max = request.args.get('playersMax')
        tags = request.args.get('tags')
        uid = request.args.get('uid')
        display_name = request.args.get('displayName')

        new_lobby = create_lobby(title, players_max, tags, uid, display_name)
        all_lobbies = get_all_lobbies()
        socketio.emit('updateLobbies', all_lobbies)
        return new_lobby

class ManageLobbyPlayers(Resource):
    def patch(self):
        required_params = ['id', 'uid', 'displayName']
        missing_params = [param for param in required_params if not request.args.get(param)]
        if missing_params:
            return {'error': f'Missing required parameters: {", ".join(missing_params)}'}, 400
        
        id = request.args.get('id')
        uid = request.args.get('uid')
        display_name = request.args.get('displayName')
        lobby = get_lobby_details(id)
        if isinstance(lobby, str):
            return {'error': lobby}, 400
        if lobby['playersJoin'] == lobby['playersMax']:
            return {'error': 'Lobby is full or unavailable'}, 400
        else:
            join_lobby(id, uid, display_name)
        lobby_details = get_lobby_details(id)
        socketio.emit('updateCurrentLobby', lobby_details)
        return lobby_details
    
    def get(self):
        required_params = ['id', 'uid', 'displayName']
        missing_params = [param for param in required_params if not request.args.get(param)]
        if missing_params:
            return {'error': f'Missing required parameters: {", ".join(missing_params)}'}, 400
        id = request.args.get('id')
        uid = request.args.get('uid')
        display_name = request.args.get('displayName')

        leave_lobby(id, uid, display_name)
        lobby_details = get_lobby_details(id)
        socketio.emit('updateCurrentLobby', lobby_details)
        return lobby_details

api.add_resource(GetAvailableLobbies, '/')
api.add_resource(UpdateLobbies, '/update_lobbies')
api.add_resource(ManageLobbyPlayers, '/manage_lobby_players')

if __name__ == "__main__":
    socketio.run(app, debug=True)
