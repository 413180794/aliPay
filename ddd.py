from socket import SocketIO

from socketio.namespace import BaseNamespace


class ChatNamespace(BaseNamespace):

    def on_aaa_response(self, *args):
        print('on_aaa_response', args)

class NewsNamespace(BaseNamespace):

    def on_aaa_response(self, *args):
        print('on_aaa_response', args)

socketIO = SocketIO('http://49.234.143.49', 8000)
chat_namespace = socketIO.define(ChatNamespace, '/?chat=sadf')


chat_namespace.emit('aaa')

socketIO.wait(seconds=1)