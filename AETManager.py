import tkinter as tk
from tkinter import font
import subprocess

# Run adb commands
def run_adb_command(command, is_core_command=False):
    try:
        # Skip device check and output update for core commands (used for status checks)
        if not is_core_command:
            # Check is device online before running any command
            check_device_online = subprocess.run("adb get-state", capture_output=True, text=True, shell=True)
            if "device" not in check_device_online.stdout:
                update_cmd_output("ERROR: No device running.")
                return "No device connected"

            # Print the command being executed in the output area
            update_cmd_output(f"RUN: {command}")

        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        resultText = result.stdout

        if not is_core_command:
            update_cmd_output(resultText if resultText else "RETURN NULL")
        return resultText
    except Exception as e:
        update_cmd_output(f"Error running command: {command}\nError: {str(e)}")
        return str(e)

wifi_state = False
data_state = False
reboot_executed = False

# Toggle wifi connection
def toggle_wifi():
    global wifi_state
    if wifi_state:
        run_adb_command("adb shell svc wifi disable")
    else:
        run_adb_command("adb shell svc wifi enable")
    update_status()

# Toggle mobile data connection
def toggle_data():
    global data_state
    if data_state:
        run_adb_command("adb shell svc data disable")
    else:
        run_adb_command("adb shell svc data enable")
    update_status()

# Change density (DPI)
def change_density(value):
    global reboot_executed

    # Validate input and print command being executed
    update_cmd_output(f"RUN: VALIDATE {value}")

    # Validate input
    if not value.isdigit():
        update_cmd_output("INVALID_INPUT: density must be a number.")
        return
    
    run_adb_command(f"adb shell wm density {int(value)} && adb reboot")
    reboot_executed = True

    update_cmd_output(f"Density changed to: {value}\nRebooting device...")
    

# Reset density to system default
def reset_density():
    global reboot_executed

    run_adb_command("adb shell wm density reset && adb reboot")
    reboot_executed = True
    update_cmd_output("Density reset to default.\nRebooting device...")


# Get the currently effective density (override if available)
def get_current_density():
    density_output = run_adb_command("adb shell wm density", is_core_command=True)
    if not density_output:
        return ""

    physical_density = ""
    for line in density_output.splitlines():
        line = line.strip()
        if line.startswith("Override density:"):
            override_density = line.split(":", 1)[1].strip()
            if override_density.isdigit():
                return override_density
        elif line.startswith("Physical density:"):
            value = line.split(":", 1)[1].strip()
            if value.isdigit():
                physical_density = value

    return physical_density


# Update status labels and button states
def update_status():
    global wifi_state, data_state, reboot_executed
    # Print reboot successful message if reboot was executed in the last command
    if reboot_executed:
        check_device_online = run_adb_command("adb get-state", is_core_command=True)
        if "device" in check_device_online:
            update_cmd_output("RETURN: device rebooted successfully.")
            reboot_executed = False


    wifi_status = run_adb_command("adb shell dumpsys wifi | findstr Wi-Fi", is_core_command=True)
    data_status = run_adb_command("adb shell dumpsys connectivity | findstr MOBILE", is_core_command=True)

    if "enabled" in wifi_status.strip().lower():
        wifi_state = True
        btn_wifi_toggle.config(bg="#4CAF50", text="📶")
        wifi_status_label.config(text="ON", fg="#4CAF50")
    else:
        wifi_state = False
        btn_wifi_toggle.config(bg="#37474F", text="📵")
        wifi_status_label.config(text="OFF", fg="#F44336")

    if "CONNECTED" in data_status.strip().upper():
        data_state = True
        btn_data_toggle.config(bg="#4CAF50", text="📡")
        data_status_label.config(text="ON", fg="#4CAF50")
    else:
        data_state = False
        btn_data_toggle.config(bg="#37474F", text="📴")
        data_status_label.config(text="OFF", fg="#F44336")

# Schedule periodic updates every 2 seconds
def schedule_update():
    update_status()
    root.after(2000, schedule_update)

# Update command output
def update_cmd_output(outputText):
    # Append new output to existing text
    cmd_output_text.config(state=tk.NORMAL)
    cmd_output_text.insert(tk.END, outputText + "\n")
    cmd_output_text.see(tk.END)
    cmd_output_text.config(state=tk.DISABLED)

# GUI
root = tk.Tk()
root.title("AETManager")
root.geometry("570x480")
root.configure(bg="#1E1E1E")
root.resizable(False, False)

# Smaller fonts
title_font = font.Font(family="Segoe UI", size=12, weight="bold")
label_font = font.Font(family="Segoe UI", size=10)
icon_font = font.Font(family="Segoe UI", size=16)
status_font = font.Font(family="Segoe UI", size=9, weight="bold")

# Title
title_label = tk.Label(root, text="AETManager",
                       font=title_font, bg="#1E1E1E",
                       fg="#FFFFFF", pady=10)
title_label.pack()

# Controls container
controls_frame = tk.Frame(root, bg="#1E1E1E", padx=15, pady=5)
controls_frame.pack(fill=tk.BOTH, expand=True)

# ----- Wi-Fi Row -----
wifi_row = tk.Frame(controls_frame, bg="#2D2D30", bd=1, relief=tk.SOLID, pady=8, padx=10)
wifi_row.pack(fill=tk.X, pady=5)

wifi_label = tk.Label(wifi_row, text="Wi-Fi", font=label_font, bg="#2D2D30", fg="#FFFFFF", width=15, anchor="w")
wifi_label.pack(side=tk.LEFT)

wifi_status_label = tk.Label(wifi_row, text="OFF", font=status_font, 
                             bg="#2D2D30", fg="#F44336", width=3)
wifi_status_label.pack(side=tk.RIGHT, padx=(6, 0))

btn_wifi_toggle = tk.Button(wifi_row, text="📵", font=icon_font, 
                            command=toggle_wifi, cursor="hand2", bd=0, 
                            width=2, height=1)
btn_wifi_toggle.pack(side=tk.RIGHT)

# ----- Mobile Data Row -----
data_row = tk.Frame(controls_frame, bg="#2D2D30", bd=1, relief=tk.SOLID, pady=8, padx=10)
data_row.pack(fill=tk.X, pady=5)

data_label = tk.Label(data_row, text="Mobile Data", font=label_font, bg="#2D2D30", fg="#FFFFFF", width=15, anchor="w")
data_label.pack(side=tk.LEFT)

data_status_label = tk.Label(data_row, text="OFF", font=status_font, 
                             bg="#2D2D30", fg="#F44336", width=3)
data_status_label.pack(side=tk.RIGHT, padx=(6, 0))

btn_data_toggle = tk.Button(data_row, text="📴", font=icon_font, 
                            command=toggle_data, cursor="hand2", bd=0, 
                            width=2, height=1)
btn_data_toggle.pack(side=tk.RIGHT)

# ----- Density Row -----
density_row = tk.Frame(controls_frame, bg="#2D2D30", bd=1, relief=tk.SOLID, pady=20, padx=10)
density_row.pack(fill=tk.X, pady=5)

density_label = tk.Label(density_row, text="Density (DPI)", font=label_font, bg="#2D2D30", fg="#FFFFFF", width=15, anchor="w")
density_label.pack(side=tk.LEFT)

density_entry = tk.Entry(density_row, font=("Segoe UI", 12), width=10, bg="#1E1E1E", fg="#FFFFFF", insertbackground="#FFFFFF")
current_density = get_current_density()
if current_density:
    density_entry.insert(0, current_density)
btn_density_reset = tk.Button(density_row, text="Reset", font=label_font,
                              command=reset_density,
                                cursor="hand2", bd=0, bg="#F44336", fg="#FFFFFF", width=8, height=1)
btn_density_change = tk.Button(density_row, text="Change", font=label_font, 
                              command=lambda: change_density(density_entry.get()),
                                cursor="hand2", bd=0, bg="#4CAF50", fg="#FFFFFF", width=8, height=1)

btn_density_reset.pack(side=tk.RIGHT)
btn_density_change.pack(side=tk.RIGHT, padx=(0, 6))
density_entry.pack(side=tk.RIGHT, padx=(0, 10))

# Bottom commands output display container
cmd_output_frame = tk.Frame(root, bg="#000000", padx=15, pady=10, height=150)
cmd_output_frame.pack(fill=tk.BOTH, expand=False)

cmd_output_text = tk.Text(cmd_output_frame, font=label_font, bg="#000000", 
                          fg="#2FF116", height=8, width=60, wrap=tk.WORD, 
                          state=tk.DISABLED)
cmd_output_text.pack(fill=tk.BOTH, expand=True)


# Footer
status_label = tk.Label(root, text="⟳ 2s", font=("Segoe UI", 8), 
                       bg="#1E1E1E", fg="#808080", pady=6)
status_label.pack()

schedule_update()
root.mainloop()
