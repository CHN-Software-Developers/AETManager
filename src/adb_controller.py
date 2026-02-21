import subprocess


class ADBController:
    def __init__(self, output_callback):
        self.output_callback = output_callback
        self.wifi_state = False
        self.data_state = False
        self.reboot_executed = False

    def run_adb_command(self, command, is_core_command=False):
        try:
            # Skip device check and output update for core commands (used for status checks)
            if not is_core_command:
                # Check is device online before running any command
                check_device_online = subprocess.run("adb get-state", capture_output=True, text=True, shell=True)
                if "device" not in check_device_online.stdout:
                    self.output_callback("ERROR: No device running.")
                    return "No device connected"

                # Print the command being executed in the output area
                self.output_callback(f"RUN: {command}")

            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            result_text = result.stdout

            if not is_core_command:
                self.output_callback(result_text if result_text else "RETURN NULL")
            return result_text
        except Exception as error:
            self.output_callback(f"Error running command: {command}\nError: {str(error)}")
            return str(error)

    def toggle_wifi(self):
        if self.wifi_state:
            self.run_adb_command("adb shell svc wifi disable")
        else:
            self.run_adb_command("adb shell svc wifi enable")
        return self.update_status()

    def toggle_data(self):
        if self.data_state:
            self.run_adb_command("adb shell svc data disable")
        else:
            self.run_adb_command("adb shell svc data enable")
        return self.update_status()

    def change_density(self, value):
        # Validate input and print command being executed
        self.output_callback(f"RUN: VALIDATE {value}")

        # Validate input
        if not value.isdigit():
            self.output_callback("INVALID_INPUT: density must be a number.")
            return

        self.run_adb_command(f"adb shell wm density {int(value)} && adb reboot")
        self.reboot_executed = True
        self.output_callback(f"Density changed to: {value}\nRebooting device...")

    def reset_density(self):
        self.run_adb_command("adb shell wm density reset && adb reboot")
        self.reboot_executed = True
        self.output_callback("Density reset to default.\nRebooting device...")

    def get_current_density(self):
        # Get the currently effective density (override if available)
        density_output = self.run_adb_command("adb shell wm density", is_core_command=True)
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

    def update_status(self):
        # Print reboot successful message if reboot was executed in the last command
        if self.reboot_executed:
            check_device_online = self.run_adb_command("adb get-state", is_core_command=True)
            if "device" in check_device_online:
                self.output_callback("RETURN: device rebooted successfully.")
                self.reboot_executed = False

        wifi_status = self.run_adb_command("adb shell dumpsys wifi | findstr Wi-Fi", is_core_command=True)
        data_status = self.run_adb_command("adb shell dumpsys connectivity | findstr MOBILE", is_core_command=True)

        self.wifi_state = "enabled" in wifi_status.strip().lower()
        self.data_state = "CONNECTED" in data_status.strip().upper()
        return self.wifi_state, self.data_state
