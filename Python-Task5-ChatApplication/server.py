
import socket
import threading
import json

from config import SERVER_HOST, SERVER_PORT, MAX_MESSAGE_LENGTH
from database import get_connection, initialize_database
from auth import register_user, login_user


clients = {}
clients_lock = threading.Lock()


def send_data(client, data):
    """Send JSON data to one client."""
    try:
        response = json.dumps(data) + "\n"
        client.sendall(response.encode("utf-8"))
        return True
    except (OSError, ConnectionError) as error:
        print("Send error:", error)
        return False


def broadcast(room_id, data):
    """Send a message to everyone in a chat room."""
    with clients_lock:
        recipients = [
            client
            for client, info in clients.items()
            if info["room_id"] == room_id
        ]

    for client in recipients:
        send_data(client, data)


def get_rooms():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, room_name FROM rooms ORDER BY room_name"
        ).fetchall()

    return [dict(row) for row in rows]


def create_room(user_id, room_name):
    room_name = room_name.strip()

    if not room_name or len(room_name) > 30:
        return False, "Room name must contain 1 to 30 characters."

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO rooms (room_name, created_by)
                VALUES (?, ?)
                """,
                (room_name, user_id)
            )

            room_id = cursor.lastrowid

            connection.execute(
                """
                INSERT INTO room_members (user_id, room_id)
                VALUES (?, ?)
                """,
                (user_id, room_id)
            )

        return True, room_id

    except Exception as error:
        print("Room creation error:", error)
        return False, "Room already exists or could not be created."


def join_room(user_id, room_id):
    try:
        room_id = int(room_id)

        with get_connection() as connection:
            room = connection.execute(
                "SELECT id, room_name FROM rooms WHERE id = ?",
                (room_id,)
            ).fetchone()

            if room is None:
                return None

            connection.execute(
                """
                INSERT OR IGNORE INTO room_members (user_id, room_id)
                VALUES (?, ?)
                """,
                (user_id, room_id)
            )

        return dict(room)

    except (ValueError, TypeError) as error:
        print("Join room error:", error)
        return None


def get_history(room_id):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT messages.message,
                   messages.sent_at,
                   users.username
            FROM messages
            JOIN users ON messages.user_id = users.id
            WHERE messages.room_id = ?
            ORDER BY messages.id DESC
            LIMIT 50
            """,
            (room_id,)
        ).fetchall()

    return [dict(row) for row in reversed(rows)]


def save_message(room_id, user_id, message):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO messages (room_id, user_id, message)
            VALUES (?, ?, ?)
            """,
            (room_id, user_id, message)
        )

        row = connection.execute(
            "SELECT sent_at FROM messages WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

    return row["sent_at"]


def handle_client(client, address):
    username = None
    user_id = None
    current_room = None

    print(f"\nNew connection: {address}")

    try:
        reader = client.makefile("r", encoding="utf-8")

        for line in reader:

            if len(line) > 10000:
                send_data(client, {
                    "type": "error",
                    "message": "Request is too large."
                })
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                send_data(client, {
                    "type": "error",
                    "message": "Invalid request."
                })
                continue

            action = data.get("action")

            print(f"Received action: {action}")

            # USER REGISTRATION
            if action == "register":

                success, message = register_user(
                    str(data.get("username", "")),
                    str(data.get("password", ""))
                )

                print("Registration result:", success, message)

                send_data(client, {
                    "type": "register_result",
                    "success": success,
                    "message": message
                })

            # USER LOGIN
            elif action == "login":

                if username:
                    send_data(client, {
                        "type": "error",
                        "message": "Already logged in."
                    })
                    continue

                success, result = login_user(
                    str(data.get("username", "")),
                    str(data.get("password", ""))
                )

                if success:
                    username = result["username"]
                    user_id = result["id"]

                    print(f"Login successful: {username}")

                    send_data(client, {
                        "type": "login_result",
                        "success": True,
                        "username": username,
                        "rooms": get_rooms()
                    })

                else:
                    send_data(client, {
                        "type": "login_result",
                        "success": False,
                        "message": result
                    })

            # REQUIRE LOGIN
            elif not username:
                send_data(client, {
                    "type": "error",
                    "message": "Please log in first."
                })

            # CREATE ROOM
            elif action == "create_room":

                success, result = create_room(
                    user_id,
                    str(data.get("room_name", ""))
                )

                if success:
                    print("Room created:", result)

                    send_data(client, {
                        "type": "room_created",
                        "room_id": result,
                        "message": "Room created successfully."
                    })
                else:
                    send_data(client, {
                        "type": "error",
                        "message": result
                    })

            # JOIN ROOM
            elif action == "join_room":

                room = join_room(
                    user_id,
                    data.get("room_id")
                )

                if room is None:
                    send_data(client, {
                        "type": "error",
                        "message": "Room not found."
                    })
                    continue

                # Remove previous room membership from active session
                if current_room is not None:
                    with clients_lock:
                        clients.pop(client, None)

                    broadcast(current_room, {
                        "type": "notification",
                        "message": f"{username} left the room."
                    })

                current_room = room["id"]

                with clients_lock:
                    clients[client] = {
                        "username": username,
                        "user_id": user_id,
                        "room_id": current_room
                    }

                print(f"{username} joined room: {room['room_name']}")

                send_data(client, {
                    "type": "room_joined",
                    "room": room,
                    "history": get_history(current_room)
                })

                broadcast(current_room, {
                    "type": "notification",
                    "message": f"{username} joined the room."
                })

            # SEND MESSAGE
            elif action == "send_message":

                print("SEND MESSAGE REQUEST RECEIVED")

                message = str(
                    data.get("message", "")
                ).strip()

                if current_room is None:
                    send_data(client, {
                        "type": "error",
                        "message": "Join a room first."
                    })
                    continue

                if not message or len(message) > MAX_MESSAGE_LENGTH:
                    send_data(client, {
                        "type": "error",
                        "message": (
                            f"Message must contain 1 to "
                            f"{MAX_MESSAGE_LENGTH} characters."
                        )
                    })
                    continue

                try:
                    timestamp = save_message(
                        current_room,
                        user_id,
                        message
                    )

                    print(
                        f"Message saved: {username}: {message}"
                    )

                    broadcast(current_room, {
                        "type": "chat_message",
                        "username": username,
                        "message": message,
                        "timestamp": timestamp
                    })

                    print("Message broadcast successfully!")

                except Exception as error:
                    print("MESSAGE DATABASE ERROR:", error)

                    send_data(client, {
                        "type": "error",
                        "message": "Could not save the message."
                    })

            # REFRESH ROOM LIST
            elif action == "list_rooms":

                send_data(client, {
                    "type": "rooms",
                    "rooms": get_rooms()
                })

            # LEAVE ROOM
            elif action == "leave_room":

                if current_room is not None:

                    with clients_lock:
                        clients.pop(client, None)

                    broadcast(current_room, {
                        "type": "notification",
                        "message": f"{username} left the room."
                    })

                    current_room = None

            else:
                send_data(client, {
                    "type": "error",
                    "message": "Unknown action."
                })

    except (OSError, ConnectionError) as error:
        print("Client connection error:", error)

    except Exception as error:
        print("Unexpected client error:", error)

    finally:

        if current_room is not None:

            with clients_lock:
                clients.pop(client, None)

            broadcast(current_room, {
                "type": "notification",
                "message": f"{username or 'A user'} disconnected."
            })

        try:
            client.close()
        except OSError:
            pass

        print(f"Disconnected: {address}")


def start_server():

    initialize_database()

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen()

    print("=" * 45)
    print("          CONNECTX CHAT SERVER")
    print("=" * 45)
    print(f"Server running at {SERVER_HOST}:{SERVER_PORT}")
    print("Waiting for connections...")

    try:
        while True:

            client, address = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(client, address),
                daemon=True
            )

            thread.start()

    except KeyboardInterrupt:
        print("\nServer shutting down...")

    finally:
        server.close()


if __name__ == "__main__":
    start_server()
