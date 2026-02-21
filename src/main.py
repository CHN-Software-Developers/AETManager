import os
import sys

from updater import auto_update_if_available
from version import APP_VERSION


def main():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    if auto_update_if_available(APP_VERSION, app_dir):
        try:
            os.execv(sys.executable, [sys.executable, os.path.join(app_dir, "main.py")])
        except OSError as error:
            print(f"Restart after update failed: {error}")

    from aet_manager_app import AETManagerApp

    app = AETManagerApp()
    app.run()


if __name__ == "__main__":
    main()
