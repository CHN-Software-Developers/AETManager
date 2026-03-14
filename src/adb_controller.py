import subprocess
import threading


class ADBController:
    LOG_LEVEL_ARGUMENTS = {
        "ALL": "*:V",
        "VERBOSE": "*:V",
        "DEBUG": "*:D",
        "INFO": "*:I",
        "WARNING": "*:W",
        "ERROR": "*:E",
    }

    def __init__(self, output_callback):
        self.output_callback = output_callback
        self.wifi_state = False
        self.data_state = False
        self.reboot_executed = False
        self.logcat_process = None
        self.logcat_thread = None
        self.logcat_stop_event = threading.Event()
        self.log_line_callback = None

    def _is_device_online(self):
        check_device_online = subprocess.run("adb get-state", capture_output=True, text=True, shell=True)
        return "device" in check_device_online.stdout

    def _normalize_remote_path(self, remote_path):
        normalized_path = (remote_path or "/").strip()
        if not normalized_path.startswith("/"):
            normalized_path = f"/{normalized_path}"
        normalized_path = normalized_path.rstrip("/")
        return normalized_path if normalized_path else "/"

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

    def _read_log_stream(self):
        try:
            while not self.logcat_stop_event.is_set() and self.logcat_process and self.logcat_process.stdout:
                line = self.logcat_process.stdout.readline()
                if not line:
                    break
                log_line = line.rstrip()
                if log_line and self.log_line_callback:
                    self.log_line_callback(log_line)
        except Exception as error:
            self.output_callback(f"ERROR: Failed reading log stream. {error}")
        finally:
            self.logcat_process = None
            if not self.logcat_stop_event.is_set():
                self.output_callback("ERROR: Log stream stopped unexpectedly.")

    def is_log_stream_running(self):
        return self.logcat_process is not None and self.logcat_process.poll() is None

    def start_log_stream(self, log_line_callback, level="ALL"):
        normalized_level = (level or "ALL").strip().upper()
        priority_argument = self.LOG_LEVEL_ARGUMENTS.get(normalized_level, self.LOG_LEVEL_ARGUMENTS["ALL"])

        if self.is_log_stream_running():
            self.output_callback("RETURN: Log stream already running.")
            return True

        check_device_online = subprocess.run("adb get-state", capture_output=True, text=True, shell=True)
        if "device" not in check_device_online.stdout:
            self.output_callback("ERROR: No device running.")
            return False

        self.log_line_callback = log_line_callback
        self.logcat_stop_event.clear()

        try:
            self.logcat_process = subprocess.Popen(
                ["adb", "logcat", "-v", "time", priority_argument],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            self.logcat_thread = threading.Thread(target=self._read_log_stream, daemon=True)
            self.logcat_thread.start()
            self.output_callback(f"RETURN: Log stream started ({normalized_level}).")
            return True
        except Exception as error:
            self.output_callback(f"ERROR: Failed to start log stream. {error}")
            self.stop_log_stream(notify=False)
            return False

    def stop_log_stream(self, notify=True):
        self.logcat_stop_event.set()

        if self.logcat_process and self.logcat_process.poll() is None:
            self.logcat_process.terminate()
            try:
                self.logcat_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.logcat_process.kill()

        if self.logcat_thread and self.logcat_thread.is_alive():
            self.logcat_thread.join(timeout=1)

        self.logcat_process = None
        self.logcat_thread = None
        self.log_line_callback = None

        if notify:
            self.output_callback("RETURN: Log stream stopped.")

    def list_remote_directories(self, remote_path):
        normalized_path = self._normalize_remote_path(remote_path)
        self.output_callback(f'RUN: adb shell ls -pa "{normalized_path}"')

        if not self._is_device_online():
            error_message = "ERROR: No device running."
            self.output_callback(error_message)
            return [], error_message

        try:
            result = subprocess.run(
                ["adb", "shell", f'ls -pa "{normalized_path}"'],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except OSError as error:
            error_message = f"ERROR: Failed to list emulator directories. {error}"
            self.output_callback(error_message)
            return [], error_message

        if result.returncode != 0:
            command_output = result.stderr.strip() if result.stderr else result.stdout.strip()
            error_message = f"ERROR: Unable to access {normalized_path}. {command_output or 'Unknown error.'}"
            self.output_callback(error_message)
            return [], error_message

        directories = []
        for line in result.stdout.splitlines():
            entry = line.strip()
            if not entry or entry in (".", ".."):
                continue
            if entry.endswith("/"):
                directory_name = entry[:-1]
                if directory_name and directory_name not in (".", ".."):
                    directories.append(directory_name)

        return sorted(set(directories), key=str.lower), None

    def push_file_to_emulator(self, local_file_path, remote_directory):
        if not local_file_path:
            self.output_callback("INVALID_INPUT: Select a local file first.")
            return False

        normalized_destination = self._normalize_remote_path(remote_directory)
        remote_target = f"{normalized_destination}/" if normalized_destination != "/" else "/"
        self.output_callback(f'RUN: adb push "{local_file_path}" "{remote_target}"')

        if not self._is_device_online():
            self.output_callback("ERROR: No device running.")
            return False

        try:
            result = subprocess.run(
                ["adb", "push", local_file_path, remote_target],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except OSError as error:
            self.output_callback(f"ERROR: File transfer failed. {error}")
            return False

        if result.returncode != 0:
            command_output = result.stderr.strip() if result.stderr else result.stdout.strip()
            self.output_callback(f"ERROR: File transfer failed. {command_output or 'Unknown error.'}")
            return False

        self.output_callback(result.stdout.strip() if result.stdout else "RETURN NULL")
        self.output_callback(f"RETURN: File transferred to {normalized_destination}")
        return True

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
