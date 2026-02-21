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

Requirements:

- Windows, Linux, or MacOS (installer only supports Windows. Additional configuration required for other operating systems).
- Python in PATH.
- ADB in PATH.

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

Installer behavior:

- Installs Python if missing
- Installs dependencies from `requirements.txt`
- Copies all files from `src\` to:
  - `%LOCALAPPDATA%\CHN Software Developers\AETManager`
- Copies `LICENSE.txt` to the same install directory
- Adds the install directory to User `PATH`

## Uninstall (Windows)

Run:

```bat
uninstall-windows.bat
```

Uninstaller behavior:

- Removes the install directory:
  - `%LOCALAPPDATA%\CHN Software Developers\AETManager`
- Removes that directory from User `PATH`
