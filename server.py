import asyncio
import json
from asyncio import Queue, StreamReader, StreamWriter


class User:
    def __init__(self, writer: StreamWriter, room: 'Room', name: str):
        self.writer = writer
        self.room = room
        self.name = name


class Message:
    def __init__(self, user: User, data: dict[str, str]):
        self.user = user
        self.data = data


class Room:
    def __init__(self):
        self.users = []


class Server:
    def __init__(self):
        self.messages: Queue[Message] = Queue()
        self.rooms: dict[str, Room] = {'test': Room()}

    async def start(self, host: str, port: int) -> None:
        # Start server
        self.server = await asyncio.start_server(self.accept_connection, host, port)
        print(f'Сервер запущен {host}: {port}')

        async with self.server:
            asyncio.create_task(self.process_messages())
            await self.server.serve_forever()

    async def accept_connection(self, reader: StreamReader, writer: StreamWriter) -> None:
        username = 'Undefined'
        try:
            # Send available rooms
            writer.write(('\n'.join(self.rooms.keys()) + '\n').encode())
            await writer.drain()

            # Receive user info
            info = json.loads((await reader.read(100)))
            if 'username' not in info or 'room' not in info:
                raise ConnectionError

            username, room_name = info['username'], info['room']
            print(f'Пользователь {username} подключился')

            # Create new room
            if room_name not in self.rooms:
                self.rooms[room_name] = Room()

            # Connect to the room
            user = User(writer, self.rooms[room_name], username)
            self.rooms[room_name].users.append(user)
            print(f'Пользователь {username} вошёл {room_name} в чат')
        except (ConnectionResetError, ConnectionError):
            print(f'Пользователь {username} отключился')
            return

        try:
            while True:
                data = await reader.read(100)
                if not data:
                    break

                await self.messages.put(Message(user, json.loads(data)))
        finally:
            user.room.users.remove(user)
            print(f'Disconnected {username}')

    async def process_messages(self) -> None:
        while True:
            message = await self.messages.get()
            for room_user in message.user.room.users:
                if room_user == message.user:
                    continue

                room_user.writer.write(json.dumps(
                    {'user': message.user.name, 'data': message.data}).encode())
                await room_user.writer.drain()


if __name__ == '__main__':
    server = Server()
    asyncio.run(server.start('0.0.0.0', 8800))
