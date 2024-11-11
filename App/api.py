from flask import Flask, request, jsonify, render_template_string
from flask_restful import Resource, Api
from flask_socketio import SocketIO
from app import create_lobby, join_lobby, leave_lobby, get_all_lobbies, close_lobby, get_lobby_details

app = Flask("co-opFinder")
api = Api(app)
socketio = SocketIO(app, async_mode='eventlet')

# HTML template for displaying the API paths
api_overview_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>API Overview</title>
</head>
<body>
    <h1>API Endpoints</h1>
    <ul>
        <li><strong>GET /</strong> - Get all available lobbies.</li>
        <li><strong>POST /update_lobbies</strong> - Create a new lobby (requires title, playersMax, tags, uid, displayName).</li>
        <li><strong>DELETE /update_lobbies</strong> - Close a lobby by ID.</li>
        <li><strong>PATCH /manage_lobby_players</strong> - Join a lobby (requires id, uid, displayName).</li>
        <li><strong>GET /manage_lobby_players</strong> - Leave a lobby (requires id, uid, displayName).</li>
    </ul>
</body>
</html>
"""

@app.route('/api_overview')
def api_overview():
    return render_template_string(api_overview_template)

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
