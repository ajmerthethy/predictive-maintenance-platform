"""Create (or reset the password of) a login user for the pilot instance.

Usage:
    python scripts/create_user.py <username> <email> <password> [role]

There's no self-serve signup by design (single-customer pilot auth) -
this is how we provision the one or two accounts a pilot customer needs.
"""

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_or_update_user(username, email, password, role="operator"):

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if user:
            user.email = email
            user.hashed_password = hash_password(password)
            user.role = role
            db.commit()
            print(f"Updated existing user '{username}'.")
            return

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )

        db.add(user)
        db.commit()
        print(f"Created user '{username}'.")

    finally:
        db.close()


if __name__ == "__main__":

    if len(sys.argv) < 4:
        print(
            "Usage: python scripts/create_user.py "
            "<username> <email> <password> [role]"
        )
        sys.exit(1)

    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    role = sys.argv[4] if len(sys.argv) > 4 else "operator"

    create_or_update_user(username, email, password, role)
