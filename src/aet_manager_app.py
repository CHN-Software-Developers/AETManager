import tkinter as tk
from tkinter import font

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
        self._set_initial_density()
        self.schedule_update()

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

    def run(self):
        self.root.mainloop()
