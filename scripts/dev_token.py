import argparse

from opspilot.api.auth import create_dev_token
from opspilot.db.seed import SEEDED_USERS


def main() -> None:
    parser = argparse.ArgumentParser(description="Mint a local token for a seeded OpsPilot identity.")
    parser.add_argument("user_id", choices=[user.id for user in SEEDED_USERS])
    args = parser.parse_args()
    print(create_dev_token(args.user_id))


if __name__ == "__main__":
    main()
