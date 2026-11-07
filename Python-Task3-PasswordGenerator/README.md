# SecurePass – Random Password Generator

A professional desktop application built with Python and Tkinter to generate strong, random passwords using secure randomization.

## Project Overview

SecurePass helps users generate customizable passwords with different character combinations. It provides a clean graphical interface, password strength feedback, clipboard support, and temporary session history.

## Features

- **Custom Password Length:** Generate passwords from 8 to 64 characters.
- **Character Selection:** Choose uppercase letters, lowercase letters, numbers, and symbols.
- **Secure Generation:** Uses Python's built-in `secrets` module.
- **Character Guarantee:** Includes at least one character from each selected category.
- **Password Strength Indicator:** Displays a strength estimate based on length and character variety.
- **Copy to Clipboard:** Copy generated passwords with one click.
- **Show/Hide Password:** Control password visibility.
- **Recent History:** Keeps the latest five generated passwords during the current session.
- **Input Validation:** Requires at least two character categories.
- **Ambiguous Character Exclusion:** Excludes visually confusing characters such as `0`, `O`, `1`, and `l`.

## Technologies Used

- Python 3
- Tkinter
- Secrets module
- String module

## Project Structure

```text
Python-Task3-PasswordGenerator/
│
├── password_generator.py
├── README.md
├── requirements.txt
└── screenshots/
    ├── securepass_main.png
    ├── password_generated.png
    └── password_validation.png
```

## Installation and Execution

### 1. Clone the repository

```bash
git clone https://github.com/mythili886/OIBSIP.git
```

### 2. Open the project folder

```bash
cd OIBSIP/Python-Task3-PasswordGenerator
```

### 3. Run the application

```bash
python password_generator.py
```

**Note:** Tkinter and the other required modules are part of Python's standard library. No additional pip packages are required.

## How It Works

1. Select a password length between 8 and 64 characters.
2. Choose at least two character categories.
3. Click **Generate Password**.
4. View the password strength indicator.
5. Use **Show Password** to reveal or hide the generated password.
6. Click **Copy to Clipboard** to copy it.
7. Select a recent entry to view it again during the current session.

## Security and Privacy

- Passwords are generated using Python's cryptographically secure `secrets` module.
- Password history is kept temporarily in application memory.
- Passwords are not saved to files or databases.
- Closing the application clears the session history.

## Learning Outcomes

- Building desktop applications using Tkinter.
- Using secure random number generation.
- Working with Python modules and functions.
- Implementing input validation.
- Managing temporary application state.
- Designing a user-friendly graphical interface.

## Internship

**Organization:** Oasis Infobyte  
**Track:** Python Development  
**Task:** Task 3 – Random Password Generator

## Author

M. Mythili

**GitHub:** https://github.com/mythili886