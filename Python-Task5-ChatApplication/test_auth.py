from database import initialize_database
from auth import register_user, login_user

initialize_database()

success, message = register_user("testuser", "TestPass123!")
print("Registration:", message)

success, result = login_user("testuser", "TestPass123!")
print("Login:", result if success else result)