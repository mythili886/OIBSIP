import ctypes
from plyer import notification
from emoji_utils import convert_emojis
import socket
import threading
import json
import queue
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from config import SERVER_HOST, SERVER_PORT, MAX_MESSAGE_LENGTH


class ConnectXClient:

    def __init__(self, root):
        self.root = root
        self.root.title("ConnectX | Real-Time Chat")
        self.root.geometry("1050x680")
        self.root.minsize(850, 550)
        self.root.configure(bg="#0B1120")

        self.client = None
        self.reader = None
        self.events = queue.Queue()
        self.username = None
        self.current_room = None
        self.rooms = []

        self.colors = {
            "background": "#0B1120",
            "panel": "#151F32",
            "input": "#1E2B42",
            "accent": "#8B5CF6",
            "cyan": "#22D3EE",
            "text": "#F1F5F9",
            "muted": "#94A3B8",
            "green": "#34D399"
        }

        self.connect_to_server()
        self.show_login()
        self.root.after(100, self.process_events)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def connect_to_server(self):
        try:
            self.client = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            self.client.connect((SERVER_HOST, SERVER_PORT))

            self.reader = threading.Thread(
                target=self.receive_messages,
                daemon=True
            )
            self.reader.start()

        except OSError as error:
            messagebox.showerror(
                "Connection Error",
                f"Could not connect to ConnectX server.\n\n{error}"
            )
            self.root.after(100, self.root.destroy)

    def send_data(self, data):
        try:
            self.client.sendall(
                (json.dumps(data) + "\n").encode("utf-8")
            )
            return True
        except (OSError, AttributeError):
            messagebox.showerror(
                "Connection Error",
                "Connection to the server was lost."
            )
            return False

    def receive_messages(self):
        try:
            reader = self.client.makefile(
                "r", encoding="utf-8"
            )

            for line in reader:
                try:
                    data = json.loads(line)
                    self.events.put(data)
                except json.JSONDecodeError:
                    continue

        except (OSError, ConnectionError):
            pass

        self.events.put({
            "type": "connection_lost"
        })

    def process_events(self):
        while not self.events.empty():
            data = self.events.get()
            event_type = data.get("type")

            if event_type == "connection_lost":
                if self.root.winfo_exists():
                    messagebox.showwarning(
                        "Disconnected",
                        "The server connection has ended."
                    )
                    self.root.destroy()
                return

            elif event_type == "register_result":
                messagebox.showinfo(
                    "Registration",
                    data.get("message", "")
                )

            elif event_type == "login_result":
                if data.get("success"):
                    self.username = data["username"]
                    self.rooms = data.get("rooms", [])
                    self.show_chat()
                else:
                    messagebox.showerror(
                        "Login Failed",
                        data.get("message", "Login failed.")
                    )

            elif event_type == "rooms":
                self.rooms = data.get("rooms", [])
                self.refresh_room_list()

            elif event_type == "room_created":
                messagebox.showinfo(
                    "Room Created",
                    data.get("message", "Room created.")
                )
                self.send_data({"action": "list_rooms"})

            elif event_type == "room_joined":
                self.current_room = data["room"]
                self.chat_display.config(state="normal")
                self.chat_display.delete("1.0", tk.END)

                self.add_system_message(
                    f"Welcome to #{self.current_room['room_name']}"
                )

                for item in data.get("history", []):
                    self.add_chat_message(
                        item["username"],
                        item["message"],
                        item["sent_at"]
                    )

                self.chat_display.config(state="disabled")
                self.room_title.config(
                    text=f"# {self.current_room['room_name']}"
                )

            elif event_type == "chat_message":
                username = data["username"]
                message = data["message"]
                self.add_chat_message(
                    username,
                    message,
                    data["timestamp"]
                )

                # Notify only for messages from other users when ConnectX
                # is not the active window.
                if username != self.username:
                    try:
                        app_is_unfocused = (
                            self.root.state() == "iconic"
                            or self.root.focus_displayof() is None
                        )
                    except tk.TclError:
                        app_is_unfocused = False

                    if app_is_unfocused:
                        self.show_desktop_notification(username, message)

            elif event_type == "notification":
                self.add_system_message(data["message"])

            elif event_type == "error":
                messagebox.showwarning(
                    "ConnectX",
                    data.get("message", "Something went wrong.")
                )

        if self.root.winfo_exists():
            self.root.after(100, self.process_events)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def make_button(self, parent, text, command, color=None):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color or self.colors["accent"],
            fg="white",
            activebackground="#7044D5",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=9
        )

    def show_login(self):
        self.clear_window()

        card = tk.Frame(
            self.root,
            bg=self.colors["panel"],
            padx=45,
            pady=35
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text="CONNECTX",
            font=("Segoe UI", 29, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["cyan"]
        ).pack(pady=(0, 5))

        tk.Label(
            card,
            text="Connect. Communicate. Collaborate.",
            font=("Segoe UI", 10),
            bg=self.colors["panel"],
            fg=self.colors["muted"]
        ).pack(pady=(0, 25))

        self.username_entry = self.make_entry(
            card, "Username"
        )
        self.password_entry = self.make_entry(
            card, "Password", show="*"
        )

        self.make_button(
            card, "LOGIN", self.login
        ).pack(fill="x", pady=(10, 7))

        self.make_button(
            card, "CREATE ACCOUNT", self.register,
            color="#263650"
        ).pack(fill="x")

        tk.Label(
            card,
            text="Python Socket-Based Messaging",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        ).pack(pady=(22, 0))

    def make_entry(self, parent, placeholder, show=None):
        tk.Label(
            parent,
            text=placeholder,
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(8, 5))

        entry = tk.Entry(
            parent,
            width=34,
            font=("Segoe UI", 11),
            bg=self.colors["input"],
            fg=self.colors["text"],
            insertbackground="white",
            relief="flat",
            show=show
        )
        entry.pack(ipady=10, pady=(0, 5))
        return entry

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Details",
                "Enter your username and password."
            )
            return

        self.send_data({
            "action": "login",
            "username": username,
            "password": password
        })

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Details",
                "Enter a username and password."
            )
            return

        self.send_data({
            "action": "register",
            "username": username,
            "password": password
        })

    def show_chat(self):
        self.clear_window()

        header = tk.Frame(
            self.root,
            bg=self.colors["panel"],
            height=65,
            padx=20
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="CONNECTX",
            font=("Segoe UI", 19, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["cyan"]
        ).pack(side="left", pady=12)

        tk.Label(
            header,
            text=f"●  {self.username}",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["green"]
        ).pack(side="right", pady=20)

        body = tk.Frame(
            self.root,
            bg=self.colors["background"]
        )
        body.pack(fill="both", expand=True, padx=15, pady=15)

        sidebar = tk.Frame(
            body,
            bg=self.colors["panel"],
            width=240,
            padx=12,
            pady=15
        )
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="CHAT ROOMS",
            bg=self.colors["panel"],
            fg=self.colors["cyan"],
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 12))

        self.room_list = tk.Listbox(
            sidebar,
            bg=self.colors["input"],
            fg=self.colors["text"],
            selectbackground=self.colors["accent"],
            font=("Segoe UI", 10),
            relief="flat",
            activestyle="none"
        )
        self.room_list.pack(fill="both", expand=True)

        self.make_button(
            sidebar, "+ CREATE ROOM", self.create_room
        ).pack(fill="x", pady=(12, 6))

        self.make_button(
            sidebar, "JOIN SELECTED", self.join_selected,
            color="#263650"
        ).pack(fill="x")

        self.make_button(
            sidebar, "REFRESH ROOMS",
            lambda: self.send_data({"action": "list_rooms"}),
            color="#263650"
        ).pack(fill="x", pady=6)

        chat_panel = tk.Frame(
            body,
            bg=self.colors["panel"],
            padx=15,
            pady=15
        )
        chat_panel.pack(side="left", fill="both", expand=True)

        self.room_title = tk.Label(
            chat_panel,
            text="Select a chat room",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Segoe UI", 15, "bold")
        )
        self.room_title.pack(anchor="w", pady=(0, 12))

        self.chat_display = tk.Text(
            chat_panel,
            bg=self.colors["input"],
            fg=self.colors["text"],
            font=("Segoe UI", 10),
            relief="flat",
            wrap="word",
            state="disabled",
            padx=12,
            pady=12
        )
        self.chat_display.pack(fill="both", expand=True)

        self.chat_display.tag_config(
            "system", foreground=self.colors["cyan"]
        )
        self.chat_display.tag_config(
            "username", foreground=self.colors["green"]
        )
        self.chat_display.tag_config(
            "time", foreground=self.colors["muted"]
        )

        input_area = tk.Frame(
            chat_panel,
            bg=self.colors["panel"]
        )
        input_area.pack(fill="x", pady=(12, 0))

        self.message_entry = tk.Entry(
            input_area,
            bg=self.colors["input"],
            fg=self.colors["text"],
            insertbackground="white",
            font=("Segoe UI", 11),
            relief="flat"
        )
        self.message_entry.pack(
            side="left", fill="x", expand=True, ipady=12
        )
        self.message_entry.bind(
            "<Return>", lambda event: self.send_message()
        )

        self.make_button(
            input_area, "SEND", self.send_message
        ).pack(side="right", padx=(8, 0))

        self.refresh_room_list()

    def refresh_room_list(self):
        if not hasattr(self, "room_list"):
            return

        self.room_list.delete(0, tk.END)

        for room in self.rooms:
            self.room_list.insert(
                tk.END,
                f"{room['id']}  |  #{room['room_name']}"
            )

    def create_room(self):
        room_name = simpledialog.askstring(
            "Create Room",
            "Enter a room name:",
            parent=self.root
        )

        if room_name:
            self.send_data({
                "action": "create_room",
                "room_name": room_name
            })

    def join_selected(self):
        selection = self.room_list.curselection()

        if not selection:
            messagebox.showwarning(
                "Select Room",
                "Please select a room first."
            )
            return

        room = self.rooms[selection[0]]

        self.send_data({
            "action": "join_room",
            "room_id": room["id"]
        })

    def send_message(self):
        message = convert_emojis(self.message_entry.get().strip())

        if not self.current_room:
            messagebox.showwarning(
                "Join a Room",
                "Please join a room before sending messages."
            )
            return

        if not message:
            return

        if len(message) > MAX_MESSAGE_LENGTH:
            messagebox.showwarning(
                "Message Too Long",
                f"Maximum {MAX_MESSAGE_LENGTH} characters allowed."
            )
            return

        if self.send_data({
            "action": "send_message",
            "message": message
        }):
            self.message_entry.delete(0, tk.END)

    def show_desktop_notification(self, username, message):
        try:
            notification.notify(
                title="ConnectX - New Message",
                message=f"{username}: {message}",
                app_name="ConnectX",
                timeout=5
            )
        except Exception as error:
            print("Desktop notification error:", error)

    def add_chat_message(self, username, message, timestamp):
        self.chat_display.config(state="normal")
        self.chat_display.insert(
            tk.END, f"[{timestamp}] ", "time"
        )
        self.chat_display.insert(
            tk.END, f"{username}: ", "username"
        )
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def add_system_message(self, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(
            tk.END, f"• {message}\n\n", "system"
        )
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def close_app(self):
        try:
            if self.client:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
        except OSError:
            pass

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectXClient(root)
    root.mainloop()
