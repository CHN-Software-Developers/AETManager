# AETManager

#### (A)ndroid (E)mulator (T)asks Manager

Simplify all your android emulator related tasks that require command executions in one place.

## Download

You can download the latest release of the tool [here](https://github.com/CHN-Software-Developers/AETManager/releases/latest).

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

## Features

- Handle network connections of the emulator
- Configure the density (dpi) of the connected device
- File transferring/sharing
- _View and filter the emulator logs (upcoming feature)_
- _Switch between multiple emulators (upcoming feature)_
- _Start/re-start/reset emulator device (upcoming feature)_

## Run Locally

Prerequisites:

- Windows, Linux, or MacOS (installer only supports Windows. Additional configuration may required for other operating systems).
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

## Tool updates or uninstallation (Windows)

The tool is capable of auto-updating itself as soon as a new update is available. If you need to uninstall the tool in any case, you can use the `uninstall-windows.bat` script.

```bat
uninstall-windows
```

## Issues

If you have any questions or issues, don't hesitate to contact us at [contact@chnsoftwaredevelopers.com](mailto:contact@chnsoftwaredevelopers.com) or raise an issue [here](https://github.com/CHN-Software-Developers/AETManager/issues).
