"""Create (or reset the password of) a login user for a pilot customer.

Usage:
    python scripts/create_user.py <account_name> <username> <email> <password> [role]

There's no self-serve signup by design (single-tier auth per account) -
this is how we provision the one or two logins a pilot customer needs.
<account_name> identifies the customer/tenant: reuse the same name to add
a second user to an existing customer's account, or use a new name to
spin up a brand-new customer account from scratch.
"""

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from app.db.database import SessionLocal
from app.models.account import Account
from app.models.user import User
from app.core.security import hash_password


def get_or_create_account(db, account_name):

    account = (
        db.query(Account)
        .filter(Account.name == account_name)
        .first()
    )

    if account:
        return account

    account = Account(name=account_name)
    db.add(account)
    db.commit()
    db.refresh(account)
    print(f"Created new account '{account_name}'.")

    return account


def create_or_update_user(account_name, username, email, password, role="operator"):

    db = SessionLocal()

    try:
        account = get_or_create_account(db, account_name)

        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if user:
            user.email = email
            user.hashed_password = hash_password(password)
            user.role = role
            user.account_id = account.id
            db.commit()
            print(f"Updated existing user '{username}' (account: '{account_name}').")
            return

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=role,
            account_id=account.id,
        )

        db.add(user)
        db.commit()
        print(f"Created user '{username}' (account: '{account_name}').")

    finally:
        db.close()


if __name__ == "__main__":

    if len(sys.argv) < 5:
        print(
            "Usage: python scripts/create_user.py "
            "<account_name> <username> <email> <password> [role]"
        )
        sys.exit(1)

    account_name = sys.argv[1]
    username = sys.argv[2]
    email = sys.argv[3]
    password = sys.argv[4]
    role = sys.argv[5] if len(sys.argv) > 5 else "operator"

    create_or_update_user(account_name, username, email, password, role)
