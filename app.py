from flask import Flask, render_template, request, jsonify
from routes import home, connect, messages
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app, manage_session=False)

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
    
blueprints = [home.bp, connect.bp, messages.bp]
for blueprint in blueprints:
    app.register_blueprint(blueprint)


if __name__ == '__main__':
    socketio.run(app, debug=True) 
