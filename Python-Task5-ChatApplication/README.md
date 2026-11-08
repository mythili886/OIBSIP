# ConnectX – Real-Time Chat Application

ConnectX is a Python-based real-time chat application that allows multiple users to communicate through chat rooms.

## Features

- User Registration and Login
- Real-Time Messaging using Python Sockets
- Multiple Chat Rooms
- SQLite Database Integration
- Message History
- Timestamped Messages
- Desktop Notifications
- Emoji Shortcode Support
- Graceful Client Disconnection
- Tkinter GUI

## Technologies Used

- Python
- Socket Programming
- Threading
- Tkinter
- SQLite
- JSON
- Plyer

## Project Structure

```text
Python-Task5-ChatApplication/
│
├── server.py
├── client.py
├── config.py
├── emoji_utils.py
├── README.md
└── requirements.txt
```

## How to Run

1. Install Python.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the server:

```bash
python server.py
```

4. Open another terminal and run:

```bash
python client.py
```

5. Open multiple clients and log in with different accounts to chat.

## Security Notes

- User credentials and chat messages are stored in a local SQLite database.
- Chat messages are not end-to-end encrypted.
- Socket communication is not encrypted.
- Do not use real passwords or sensitive personal information in this demonstration project.

## Project Purpose

This project was developed as part of the OIBSIP Python Programming Internship to practice socket programming, multithreading, GUI development, database integration, and real-time communication.