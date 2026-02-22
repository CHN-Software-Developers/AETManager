# AETManager

Simplify all your android emulator related tasks that require command executions in one place.

## Project Structure

```text
src/
  main.py              # App entry point
  aet_manager_app.py   # Tkinter UI
  adb_controller.py    # ADB command/state logic
  theme.py             # UI color theme constants
  updater.py           # Release update logic
  version.py           # APP_VERSION (example: v0.0.1)
  aetmanager.bat       # Convenience launcher
```

## Run Locally

Prerequisites:

- Windows, Linux, or MacOS (installer only supports Windows. Additional configuration required for other operating systems).
- Python and ADB in PATH (the installer for Windows will try to automatically install python if no installation found).

From repository root:

```bat
cd src
python main.py
```

Or run:

```bat
src\aetmanager.bat
```

## Install (Windows)

Run:

```bat
install-windows.bat
```

