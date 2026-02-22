import tkinter as tk
from tkinter import font
import queue

from adb_controller import ADBController
import theme


class AETManagerApp:
    def __init__(self, startup_messages=None):
        self.root = tk.Tk()
        self.root.title("AETManager")
        self.root.geometry("570x480")
        self.root.configure(bg=theme.WINDOW_BG)
        self.root.resizable(False, False)

        # Smaller fonts
        self.title_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=10)
        self.icon_font = font.Font(family="Segoe UI", size=16)
        self.status_font = font.Font(family="Segoe UI", size=9, weight="bold")

        self._build_ui()
        self.startup_messages = startup_messages or []
        self._show_startup_messages()
        self.controller = ADBController(self.update_cmd_output)
        self.logs_window = None
        self.logs_text = None
        self.logs_filter_entry = None
        self.logs_level_var = None
        self.logs_start_button = None
        self.logs_stop_button = None
        self.logs_lines = []
        self.logs_queue = queue.Queue()
        self.logs_update_job = None
        self.log_level_options = ("All", "Errors", "Warnings", "Info", "Debug", "Verbose")
        self._set_initial_density()
        self.schedule_update()
        self.root.protocol("WM_DELETE_WINDOW", self._on_app_close)

    def _build_ui(self):
        # Title
        title_label = tk.Label(
            self.root,
            text="AETManager",
            font=self.title_font,
            bg=theme.WINDOW_BG,
            fg=theme.TEXT_COLOR,
            pady=10,
        )
        title_label.pack()

        # Controls container
        controls_frame = tk.Frame(self.root, bg=theme.WINDOW_BG, padx=15, pady=5)
        controls_frame.pack(fill=tk.BOTH, expand=True)

        # ----- Wi-Fi Row -----
        wifi_row = tk.Frame(controls_frame, bg=theme.ROW_BG, bd=1, relief=tk.SOLID, pady=8, padx=10)
        wifi_row.pack(fill=tk.X, pady=5)

        wifi_label = tk.Label(wifi_row, text="Wi-Fi", font=self.label_font, bg=theme.ROW_BG, fg=theme.TEXT_COLOR, width=15, anchor="w")
        wifi_label.pack(side=tk.LEFT)

        self.wifi_status_label = tk.Label(wifi_row, text="OFF", font=self.status_font, bg=theme.ROW_BG, fg=theme.ERROR_COLOR, width=3)
        self.wifi_status_label.pack(side=tk.RIGHT, padx=(6, 0))

        self.btn_wifi_toggle = tk.Button(wifi_row, text="📵", font=self.icon_font, command=self.toggle_wifi, cursor="hand2", bd=0, width=2, height=1)
        self.btn_wifi_toggle.pack(side=tk.RIGHT)

        # ----- Mobile Data Row -----
        data_row = tk.Frame(controls_frame, bg=theme.ROW_BG, bd=1, relief=tk.SOLID, pady=8, padx=10)
        data_row.pack(fill=tk.X, pady=5)

        data_label = tk.Label(data_row, text="Mobile Data", font=self.label_font, bg=theme.ROW_BG, fg=theme.TEXT_COLOR, width=15, anchor="w")
        data_label.pack(side=tk.LEFT)

        self.data_status_label = tk.Label(data_row, text="OFF", font=self.status_font, bg=theme.ROW_BG, fg=theme.ERROR_COLOR, width=3)
        self.data_status_label.pack(side=tk.RIGHT, padx=(6, 0))

        self.btn_data_toggle = tk.Button(data_row, text="📴", font=self.icon_font, command=self.toggle_data, cursor="hand2", bd=0, width=2, height=1)
        self.btn_data_toggle.pack(side=tk.RIGHT)

        # ----- Density Row -----
        density_row = tk.Frame(controls_frame, bg=theme.ROW_BG, bd=1, relief=tk.SOLID, pady=20, padx=10)
        density_row.pack(fill=tk.X, pady=5)

        density_label = tk.Label(density_row, text="Density (DPI)", font=self.label_font, bg=theme.ROW_BG, fg=theme.TEXT_COLOR, width=15, anchor="w")
        density_label.pack(side=tk.LEFT)

        self.density_entry = tk.Entry(
            density_row,
            font=("Segoe UI", 12),
            width=10,
            bg=theme.WINDOW_BG,
            fg=theme.TEXT_COLOR,
            insertbackground=theme.TEXT_COLOR,
        )
        self.btn_density_reset = tk.Button(
            density_row,
            text="Reset",
            font=self.label_font,
            command=self.reset_density,
            cursor="hand2",
            bd=0,
            bg=theme.ERROR_COLOR,
            fg=theme.TEXT_COLOR,
            width=8,
            height=1,
        )
        self.btn_density_change = tk.Button(
            density_row,
            text="Change",
            font=self.label_font,
            command=self.change_density,
            cursor="hand2",
            bd=0,
            bg=theme.SUCCESS_COLOR,
            fg=theme.TEXT_COLOR,
            width=8,
            height=1,
        )

        self.btn_density_reset.pack(side=tk.RIGHT)
        self.btn_density_change.pack(side=tk.RIGHT, padx=(0, 6))
        self.density_entry.pack(side=tk.RIGHT, padx=(0, 10))

        # ----- Emulator Logs Row -----
        logs_row = tk.Frame(controls_frame, bg=theme.ROW_BG, bd=1, relief=tk.SOLID, pady=8, padx=10)
        logs_row.pack(fill=tk.X, pady=5)

        logs_label = tk.Label(logs_row, text="Emulator Logs", font=self.label_font, bg=theme.ROW_BG, fg=theme.TEXT_COLOR, width=15, anchor="w")
        logs_label.pack(side=tk.LEFT)

        self.btn_logs_open = tk.Button(
            logs_row,
            text="Open",
            font=self.label_font,
            command=self.open_logs_window,
            cursor="hand2",
            bd=0,
            bg=theme.SUCCESS_COLOR,
            fg=theme.TEXT_COLOR,
            width=8,
            height=1,
        )
        self.btn_logs_open.pack(side=tk.RIGHT)

        # Bottom commands output display container
        cmd_output_frame = tk.Frame(self.root, bg=theme.OUTPUT_BG, padx=15, pady=10, height=150)
        cmd_output_frame.pack(fill=tk.BOTH, expand=False)

        self.cmd_output_text = tk.Text(
            cmd_output_frame,
            font=self.label_font,
            bg=theme.OUTPUT_BG,
            fg=theme.OUTPUT_TEXT_COLOR,
            height=8,
            width=60,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.cmd_output_text.pack(fill=tk.BOTH, expand=True)

        # Footer
        status_label = tk.Label(
            self.root,
            text="⟳ 2s",
            font=("Segoe UI", 8),
            bg=theme.WINDOW_BG,
            fg=theme.FOOTER_TEXT_COLOR,
            pady=6,
        )
        status_label.pack()

    def _show_startup_messages(self):
        for message in self.startup_messages:
            self.update_cmd_output(message)

    def _set_initial_density(self):
        current_density = self.controller.get_current_density()
        if current_density:
            self.density_entry.insert(0, current_density)

    def _apply_status(self, wifi_state, data_state):
        if wifi_state:
            self.btn_wifi_toggle.config(bg=theme.SUCCESS_COLOR, text="📶")
            self.wifi_status_label.config(text="ON", fg=theme.SUCCESS_COLOR)
        else:
            self.btn_wifi_toggle.config(bg=theme.INACTIVE_BUTTON_COLOR, text="📵")
            self.wifi_status_label.config(text="OFF", fg=theme.ERROR_COLOR)

        if data_state:
            self.btn_data_toggle.config(bg=theme.SUCCESS_COLOR, text="📡")
            self.data_status_label.config(text="ON", fg=theme.SUCCESS_COLOR)
        else:
            self.btn_data_toggle.config(bg=theme.INACTIVE_BUTTON_COLOR, text="📴")
            self.data_status_label.config(text="OFF", fg=theme.ERROR_COLOR)

    # Update command output
    def update_cmd_output(self, output_text):
        # Append new output to existing text
        self.cmd_output_text.config(state=tk.NORMAL)
        self.cmd_output_text.insert(tk.END, output_text + "\n")
        self.cmd_output_text.see(tk.END)
        self.cmd_output_text.config(state=tk.DISABLED)

    # Update status labels and button states
    def update_status(self):
        wifi_state, data_state = self.controller.update_status()
        self._apply_status(wifi_state, data_state)

    # Schedule periodic updates every 2 seconds
    def schedule_update(self):
        self.update_status()
        self.root.after(2000, self.schedule_update)

    # Toggle wifi connection
    def toggle_wifi(self):
        wifi_state, data_state = self.controller.toggle_wifi()
        self._apply_status(wifi_state, data_state)

    # Toggle mobile data connection
    def toggle_data(self):
        wifi_state, data_state = self.controller.toggle_data()
        self._apply_status(wifi_state, data_state)

    # Change density (DPI)
    def change_density(self):
        self.controller.change_density(self.density_entry.get())

    # Reset density to system default
    def reset_density(self):
        self.controller.reset_density()

    def open_logs_window(self):
        if self.logs_window and self.logs_window.winfo_exists():
            self.logs_window.lift()
            self.logs_window.focus_force()
            return

        self.logs_window = tk.Toplevel(self.root)
        self.logs_window.title("Emulator Logs")
        self.logs_window.geometry("900x520")
        self.logs_window.configure(bg=theme.WINDOW_BG)
        self.logs_window.protocol("WM_DELETE_WINDOW", self.close_logs_window)

        controls_frame = tk.Frame(self.logs_window, bg=theme.WINDOW_BG, padx=10, pady=8)
        controls_frame.pack(fill=tk.X)

        filter_label = tk.Label(controls_frame, text="Filter", font=self.label_font, bg=theme.WINDOW_BG, fg=theme.TEXT_COLOR)
        filter_label.pack(side=tk.LEFT)

        self.logs_filter_entry = tk.Entry(
            controls_frame,
            font=self.label_font,
            width=32,
            bg=theme.ROW_BG,
            fg=theme.TEXT_COLOR,
            insertbackground=theme.TEXT_COLOR,
        )
        self.logs_filter_entry.pack(side=tk.LEFT, padx=(8, 10))
        self.logs_filter_entry.bind("<KeyRelease>", lambda _event: self.refresh_logs_view())

        level_label = tk.Label(controls_frame, text="Level", font=self.label_font, bg=theme.WINDOW_BG, fg=theme.TEXT_COLOR)
        level_label.pack(side=tk.LEFT, padx=(0, 8))

        self.logs_level_var = tk.StringVar(self.logs_window, value=self.log_level_options[0])
        level_menu = tk.OptionMenu(controls_frame, self.logs_level_var, *self.log_level_options, command=self.on_logs_level_change)
        level_menu.config(
            font=self.label_font,
            bg=theme.INACTIVE_BUTTON_COLOR,
            fg=theme.TEXT_COLOR,
            activebackground=theme.ROW_BG,
            activeforeground=theme.TEXT_COLOR,
            bd=0,
            highlightthickness=0,
        )
        level_menu["menu"].config(font=self.label_font, bg=theme.ROW_BG, fg=theme.TEXT_COLOR)
        level_menu.pack(side=tk.LEFT, padx=(0, 10))

        self.logs_start_button = tk.Button(
            controls_frame,
            text="Start",
            font=self.label_font,
            command=self.start_logs_stream,
            cursor="hand2",
            bd=0,
            bg=theme.SUCCESS_COLOR,
            fg=theme.TEXT_COLOR,
            width=8,
        )
        self.logs_start_button.pack(side=tk.LEFT, padx=(0, 6))

        self.logs_stop_button = tk.Button(
            controls_frame,
            text="Stop",
            font=self.label_font,
            command=self.stop_logs_stream,
            cursor="hand2",
            bd=0,
            bg=theme.ERROR_COLOR,
            fg=theme.TEXT_COLOR,
            width=8,
        )
        self.logs_stop_button.pack(side=tk.LEFT, padx=(0, 6))

        clear_button = tk.Button(
            controls_frame,
            text="Clear",
            font=self.label_font,
            command=self.clear_logs,
            cursor="hand2",
            bd=0,
            bg=theme.INACTIVE_BUTTON_COLOR,
            fg=theme.TEXT_COLOR,
            width=8,
        )
        clear_button.pack(side=tk.LEFT)

        logs_output_frame = tk.Frame(self.logs_window, bg=theme.OUTPUT_BG, padx=10, pady=8)
        logs_output_frame.pack(fill=tk.BOTH, expand=True)

        self.logs_text = tk.Text(
            logs_output_frame,
            font=self.label_font,
            bg=theme.OUTPUT_BG,
            fg=theme.OUTPUT_TEXT_COLOR,
            wrap=tk.NONE,
            state=tk.DISABLED,
        )
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        y_scrollbar = tk.Scrollbar(logs_output_frame, orient=tk.VERTICAL, command=self.logs_text.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.logs_text.configure(yscrollcommand=y_scrollbar.set)

        self.refresh_logs_view()
        self._update_logs_buttons()
        if self.logs_update_job is None:
            self._pump_logs_queue()
        self.start_logs_stream()

    def _pump_logs_queue(self):
        has_new_data = False
        while True:
            try:
                line = self.logs_queue.get_nowait()
            except queue.Empty:
                break
            self.logs_lines.append(line)
            has_new_data = True

        if has_new_data and self.logs_window and self.logs_window.winfo_exists():
            self.refresh_logs_view()

        if self.logs_window and self.logs_window.winfo_exists():
            self._update_logs_buttons()
            self.logs_update_job = self.root.after(250, self._pump_logs_queue)
        else:
            self.logs_update_job = None

    def refresh_logs_view(self):
        if not self.logs_text:
            return

        filter_value = self.logs_filter_entry.get().strip().lower() if self.logs_filter_entry else ""
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete("1.0", tk.END)
        for line in self.logs_lines:
            if not filter_value or filter_value in line.lower():
                self.logs_text.insert(tk.END, line + "\n")
        self.logs_text.see(tk.END)
        self.logs_text.config(state=tk.DISABLED)

    def _queue_log_line(self, line):
        self.logs_queue.put(line)

    def _update_logs_buttons(self):
        running = self.controller.is_log_stream_running()
        if self.logs_start_button:
            self.logs_start_button.config(state=tk.DISABLED if running else tk.NORMAL)
        if self.logs_stop_button:
            self.logs_stop_button.config(state=tk.NORMAL if running else tk.DISABLED)

    def _selected_log_level(self):
        level_mapping = {
            "All": "ALL",
            "Errors": "ERROR",
            "Warnings": "WARNING",
            "Info": "INFO",
            "Debug": "DEBUG",
            "Verbose": "VERBOSE",
        }
        selected_level = self.logs_level_var.get() if self.logs_level_var else "All"
        return level_mapping.get(selected_level, "ALL")

    def on_logs_level_change(self, _selected_level=None):
        if self.controller.is_log_stream_running():
            self.controller.stop_log_stream(notify=False)
            self.start_logs_stream()

    def start_logs_stream(self):
        if self.controller.start_log_stream(self._queue_log_line, self._selected_log_level()):
            self._update_logs_buttons()

    def stop_logs_stream(self):
        self.controller.stop_log_stream()
        self._update_logs_buttons()

    def clear_logs(self):
        self.logs_lines.clear()
        self.refresh_logs_view()

    def close_logs_window(self):
        if self.logs_update_job is not None:
            self.root.after_cancel(self.logs_update_job)
            self.logs_update_job = None

        self.stop_logs_stream()

        if self.logs_window and self.logs_window.winfo_exists():
            self.logs_window.destroy()

        self.logs_window = None
        self.logs_text = None
        self.logs_filter_entry = None
        self.logs_level_var = None
        self.logs_start_button = None
        self.logs_stop_button = None

    def _on_app_close(self):
        if self.logs_update_job is not None:
            self.root.after_cancel(self.logs_update_job)
            self.logs_update_job = None
        self.controller.stop_log_stream(notify=False)
        self.root.destroy()

    def run(self):
        self.root.mainloop()
