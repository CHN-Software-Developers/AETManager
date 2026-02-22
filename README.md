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
- Python and ADB in PATH (the installer for Windows will try to automatically install Python if no installation is found).

From repository root:

```bat
cd src
python main.py
```

Or run:

```bat
src\aetmanager
```

## Install (Windows)

To install the tool on your computer, you can use the `install-windows.bat` script, which is under the root folder. This will add the program to PATH. Therefore, after, you can simply use the `aetmanager` command in the command prompt to open the tool at any time.

```bat
install-windows
```


