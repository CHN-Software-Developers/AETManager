import os
import sys

from updater import auto_update_if_available
from version import APP_VERSION


def main():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    startup_messages = []
    status_callback = startup_messages.append

    if auto_update_if_available(APP_VERSION, app_dir, status_callback=status_callback):
        try:
            os.execv(sys.executable, [sys.executable, os.path.join(app_dir, "main.py")])
        except OSError as error:
            startup_messages.append(f"Restart after update failed: {error}")

    from aet_manager_app import AETManagerApp

    app = AETManagerApp(startup_messages=startup_messages)
    app.run()


if __name__ == "__main__":
    main()
