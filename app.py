from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room


### TEST -----------------------------------------------

# https://flask-socketio.readthedocs.io/en/latest/
# https://github.com/socketio/socket.io-client

app = Flask(__name__)

app.config[ 'SECRET_KEY' ] = 'jsbcfsbfjefebw237u3gdbdc'
socketio = SocketIO( app , ping_interval=15)

users =  {}

@app.route('/')
def main():
    return render_template('./main-page.html')

@app.route("/", methods = ['POST', 'GET'])
def main2():
    return render_template('./main-page.html')


@app.route( "/chat", methods = ['POST'] )
def send():
    session['nickname'] = request.form["nickname"]
    session['ip'] = str(request.remote_addr)
    session['status'] = True
    print(session)
    return render_template( './ChatApp.html',  nickname = session['nickname'] )

def messageRecived():
    print( 'message was received!!!' )

@socketio.on( 'my event' )
def handle_my_custom( json ):
    print(session['room'])
    socketio.emit( 'show message', json, room = session['room'])

@socketio.on('add user')
def addUser(json):
    users[json['nickname']] = {'sid' : request.sid, 'ip': request.remote_addr, 'status' : 'ONLINE'}
    session['room'] = users[json['nickname']]['sid']
    print(session)
    print(users)

@socketio.on('print users')
def printUsers():
    socketio.emit( 'clear user list')
    socketio.emit( 'print user list', users)

@socketio.on('clear')
def clearUsers():
    socketio.emit( 'clear user list')

@socketio.on('request')
def sendRequest(json):
    socketio.emit('send request', json, room = users[json['requested']]['sid'])

@socketio.on('permit chat acceptor')
def permitAcceptor(json):
    if json['res'] == True :
        room = json['sender']+json['acceptor']
        if session['room'] != users[json['acceptor']]['sid']:
            leave_room(session['room'])
        session['room'] = room
        join_room(room)
        socketio.emit('permit sender', {'sender': json['sender'], 'acceptor': json['acceptor']}, room = users[json['sender']]['sid'])

@socketio.on('permit chat sender')
def permitSender(json):
    room = json['sender']+json['acceptor']
    if session['room'] != users[json['sender']]['sid']:
        leave_room(session['room'])
    session['room'] = room
    join_room(room)
    socketio.emit('clear messages', room = room)

@socketio.on('pingPy')
def sendPing():
    for index in users:
        print(index)
        users[index]['status'] = 'OFFLINE'
    for index in users:
        socketio.emit('control', {'index': index, 'status': users[index]['status']}, room = users[index]['sid'])


@socketio.on('still online')
def online(json):
    users[json['index']]['status'] = 'ONLINE'
    print(users)


if __name__ == '__main__':
    import _thread, time
    socketio.run( app, host='0.0.0.0', debug = True)
    #_thread.start_new_thread(lambda: socketio.run( app, host='0.0.0.0', debug = True, use_reloader=False ),())
    #sendPing()
