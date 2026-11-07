
import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string

# -------------------- COLORS --------------------
BG = "#0B1120"
CARD = "#151F32"
CARD_LIGHT = "#1C2940"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"
ACCENT = "#8B5CF6"
CYAN = "#22D3EE"
GREEN = "#34D399"

# -------------------- APP WINDOW --------------------
root = tk.Tk()
root.title("SecurePass | Password Generator")
root.geometry("900x650")
root.minsize(800, 600)
root.configure(bg=BG)

# -------------------- PASSWORD SETTINGS --------------------
length_var = tk.IntVar(value=16)
upper_var = tk.BooleanVar(value=True)
lower_var = tk.BooleanVar(value=True)
number_var = tk.BooleanVar(value=True)
symbol_var = tk.BooleanVar(value=True)
reveal_var = tk.BooleanVar(value=False)

current_password = ""
password_history = []

# Ambiguous characters are excluded for readability.
CHARSETS = {
    "Uppercase": "ABCDEFGHJKLMNPQRSTUVWXYZ",
    "Lowercase": "abcdefghijkmnopqrstuvwxyz",
    "Numbers": "23456789",
    "Symbols": "!@#$%^&*()-_=+?"
}

# -------------------- HELPER FUNCTIONS --------------------
def get_selected_charsets():
    selected = []

    if upper_var.get():
        selected.append(CHARSETS["Uppercase"])
    if lower_var.get():
        selected.append(CHARSETS["Lowercase"])
    if number_var.get():
        selected.append(CHARSETS["Numbers"])
    if symbol_var.get():
        selected.append(CHARSETS["Symbols"])

    return selected


def update_strength(password, category_count):
    score = 0

    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    if category_count >= 3:
        score += 1
    if category_count == 4:
        score += 1

    if score <= 1:
        strength_label.config(text="●  Moderate", fg="#FBBF24")
        strength_bar["value"] = 35
    elif score <= 2:
        strength_label.config(text="●  Strong", fg=CYAN)
        strength_bar["value"] = 70
    else:
        strength_label.config(text="●  Very Strong", fg=GREEN)
        strength_bar["value"] = 100


def display_password(password):
    password_var.set(password)
    password_entry.config(show="" if reveal_var.get() else "•")


def toggle_password_visibility():
    password_entry.config(show="" if reveal_var.get() else "•")


# -------------------- GENERATE PASSWORD --------------------
def generate_password():
    global current_password

    selected = get_selected_charsets()

    if len(selected) < 2:
        messagebox.showwarning(
            "Selection Required",
            "Please select at least TWO character types."
        )
        return

    length = length_var.get()

    if length < 8 or length > 64:
        messagebox.showwarning(
            "Invalid Length",
            "Password length must be between 8 and 64."
        )
        return

    # Guarantee at least one character from every selected type.
    password_chars = [secrets.choice(charset) for charset in selected]

    # Fill the remaining positions securely.
    all_chars = "".join(selected)

    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(all_chars))

    # Securely shuffle the characters.
    secrets.SystemRandom().shuffle(password_chars)

    current_password = "".join(password_chars)
    display_password(current_password)

    # Keep only the latest five passwords in this session.
    password_history.insert(0, current_password)
    del password_history[5:]

    update_history()
    update_strength(current_password, len(selected))
    status_label.config(text="Password generated successfully!", fg=GREEN)


# -------------------- COPY PASSWORD --------------------
def copy_password():
    if not current_password:
        messagebox.showinfo("No Password", "Generate a password first.")
        return

    root.clipboard_clear()
    root.clipboard_append(current_password)
    root.update()

    status_label.config(text="Password copied to clipboard!", fg=GREEN)


# -------------------- HISTORY --------------------
def update_history():
    history_list.delete(0, tk.END)

    for index, password in enumerate(password_history, start=1):
        history_list.insert(
            tk.END,
            f"  {index}.  {'•' * len(password)}  ({len(password)} characters)"
        )


def load_history(event=None):
    selection = history_list.curselection()

    if selection:
        index = selection[0]
        selected_password = password_history[index]
        display_password(selected_password)
        current_status = f"Selected password {index + 1} from session history."
        status_label.config(text=current_status, fg=CYAN)


# -------------------- UI HELPERS --------------------
def make_label(parent, text, size=11, color=TEXT, weight="normal"):
    return tk.Label(
        parent,
        text=text,
        bg=parent.cget("bg"),
        fg=color,
        font=("Segoe UI", size, weight)
    )


def make_card(parent):
    return tk.Frame(parent, bg=CARD, highlightthickness=1,
                    highlightbackground="#26344D")


# -------------------- HEADER --------------------
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=35, pady=(25, 18))

make_label(header, "SECUREPASS", 25, CYAN, "bold").pack(anchor="w")
make_label(
    header,
    "Create strong, random passwords in seconds.",
    11,
    MUTED
).pack(anchor="w", pady=(3, 0))

# -------------------- MAIN CONTENT --------------------
main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=35, pady=5)

main.columnconfigure(0, weight=1)
main.columnconfigure(1, weight=1)
main.rowconfigure(0, weight=1)

# LEFT: SETTINGS CARD
settings_card = make_card(main)
settings_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

settings_inner = tk.Frame(settings_card, bg=CARD)
settings_inner.pack(fill="both", expand=True, padx=22, pady=22)

make_label(settings_inner, "Password Settings", 16, TEXT, "bold").pack(anchor="w")
make_label(
    settings_inner,
    "Customize your password",
    10,
    MUTED
).pack(anchor="w", pady=(3, 20))

make_label(settings_inner, "PASSWORD LENGTH", 9, CYAN, "bold").pack(anchor="w")

length_display = make_label(settings_inner, "16 characters", 12, TEXT, "bold")
length_display.pack(anchor="w", pady=(5, 4))


def change_length(value):
    length_display.config(text=f"{int(float(value))} characters")


length_slider = tk.Scale(
    settings_inner,
    from_=8,
    to=64,
    orient="horizontal",
    variable=length_var,
    command=change_length,
    bg=CARD,
    fg=TEXT,
    troughcolor=CARD_LIGHT,
    activebackground=ACCENT,
    highlightthickness=0,
    bd=0,
    font=("Segoe UI", 9)
)
length_slider.pack(fill="x", pady=(0, 20))

make_label(settings_inner, "CHARACTER TYPES", 9, CYAN, "bold").pack(anchor="w", pady=(0, 10))

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Secure.TCheckbutton",
    background=CARD,
    foreground=TEXT,
    font=("Segoe UI", 11)
)
style.map(
    "Secure.TCheckbutton",
    background=[("active", CARD)],
    foreground=[("active", CYAN)]
)

for label, variable in [
    ("Uppercase letters (A–Z)", upper_var),
    ("Lowercase letters (a–z)", lower_var),
    ("Numbers (2–9)", number_var),
    ("Symbols (!@#$...)", symbol_var)
]:
    ttk.Checkbutton(
        settings_inner,
        text=label,
        variable=variable,
        style="Secure.TCheckbutton"
    ).pack(anchor="w", pady=5)

make_label(
    settings_inner,
    "ℹ  Ambiguous characters are excluded.",
    9,
    MUTED
).pack(anchor="w", pady=(18, 0))


# RIGHT: OUTPUT CARD
output_card = make_card(main)
output_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

output_inner = tk.Frame(output_card, bg=CARD)
output_inner.pack(fill="both", expand=True, padx=22, pady=22)

make_label(output_inner, "Your Password", 16, TEXT, "bold").pack(anchor="w")
make_label(
    output_inner,
    "Your secure password will appear below.",
    10,
    MUTED
).pack(anchor="w", pady=(3, 18))

password_var = tk.StringVar()

password_entry = tk.Entry(
    output_inner,
    textvariable=password_var,
    font=("Consolas", 15, "bold"),
    bg=CARD_LIGHT,
    fg=CYAN,
    insertbackground=TEXT,
    relief="flat",
    bd=0,
    show="•"
)
password_entry.pack(fill="x", ipady=14, pady=(0, 8))

ttk.Checkbutton(
    output_inner,
    text="Show password",
    variable=reveal_var,
    command=toggle_password_visibility,
    style="Secure.TCheckbutton"
).pack(anchor="w", pady=(0, 15))

generate_button = tk.Button(
    output_inner,
    text="✦  Generate Password",
    command=generate_password,
    bg=ACCENT,
    fg="white",
    activebackground="#7C3AED",
    activeforeground="white",
    font=("Segoe UI", 11, "bold"),
    relief="flat",
    cursor="hand2",
    pady=12
)
generate_button.pack(fill="x", pady=(0, 9))

copy_button = tk.Button(
    output_inner,
    text="Copy to Clipboard",
    command=copy_password,
    bg=CARD_LIGHT,
    fg=CYAN,
    activebackground="#26344D",
    activeforeground="white",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    cursor="hand2",
    pady=10
)
copy_button.pack(fill="x")

# STRENGTH INDICATOR
make_label(output_inner, "PASSWORD STRENGTH", 9, MUTED, "bold").pack(anchor="w", pady=(22, 8))

strength_label = make_label(output_inner, "●  Not generated", 11, MUTED, "bold")
strength_label.pack(anchor="w")

style.configure(
    "Secure.Horizontal.TProgressbar",
    troughcolor=CARD_LIGHT,
    background=GREEN,
    bordercolor=CARD_LIGHT,
    lightcolor=GREEN,
    darkcolor=GREEN
)

strength_bar = ttk.Progressbar(
    output_inner,
    style="Secure.Horizontal.TProgressbar",
    maximum=100,
    value=0
)
strength_bar.pack(fill="x", pady=(8, 15))

# SESSION HISTORY
make_label(output_inner, "RECENT PASSWORDS", 9, MUTED, "bold").pack(anchor="w", pady=(3, 8))

history_list = tk.Listbox(
    output_inner,
    height=5,
    bg=CARD_LIGHT,
    fg=TEXT,
    selectbackground=ACCENT,
    selectforeground="white",
    font=("Segoe UI", 9),
    relief="flat",
    highlightthickness=0,
    activestyle="none"
)
history_list.pack(fill="both", expand=True)
history_list.bind("<<ListboxSelect>>", load_history)

make_label(
    output_inner,
    "History is temporary and clears when you close the app.",
    8,
    MUTED
).pack(anchor="w", pady=(8, 0))

# -------------------- FOOTER --------------------
footer = tk.Frame(root, bg=BG)
footer.pack(fill="x", padx=35, pady=(5, 18))

status_label = make_label(footer, "Ready to generate a password.", 9, MUTED)
status_label.pack(side="left")

make_label(footer, "SECUREPASS  •  PYTHON PROJECT", 8, MUTED).pack(side="right")

# -------------------- START APPLICATION --------------------
root.mainloop()
