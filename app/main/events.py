from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio

import json
list_messages = []
clients = []

import pika

credentials = pika.PlainCredentials('guest','guest')
parameters = pika.ConnectionParameters('127.0.0.1',
                                       5672,
                                       '/',
                                       credentials)
connection = pika.BlockingConnection((parameters))


channel = connection.channel()

'''channel.queue_declare(queue='hello')'''

def addNewMsg(message,session):
	global channel
	channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=json.dumps({'message': message,'session':{'sessionId':session.get('csrf_token')  } }))
                      #body=  jsonpickle.encode({'message': message,'session': session.__dict__},unpicklable=False))






@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    global list_messages
    room = session.get('room')
    join_room(room)
    print ('joined session list_messages ' + str(len(list_messages)) + ' , session ' + str(session) +'\n')
    emit('status', {'msg': str(clients)})
    for x in list_messages:
        emit('status', {'msg': x})
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    global list_messages
    room = session.get('room')
    msg = session.get('name') + ':' + message['msg']
    list_messages.append(msg)
    addNewMsg(message,session)
    print ('size of list_messages ' + str(len(list_messages)) + ', session ' + str(session))
    emit('message', {'msg': msg}, room=room)



@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)

