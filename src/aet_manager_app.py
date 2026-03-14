import tkinter as tk
from tkinter import filedialog, font, ttk
import queue

from adb_controller import ADBController
import theme


class AETManagerApp:
    def __init__(self, startup_messages=None):
        self.root = tk.Tk()
        self.root.title("AETManager")
        self.root.geometry("570x580")
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
        self.transfer_window = None
        self.transfer_tree = None
        self.transfer_local_file_var = None
        self.transfer_destination_var = None
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

        # ----- Transfer Files Row -----
        transfer_row = tk.Frame(controls_frame, bg=theme.ROW_BG, bd=1, relief=tk.SOLID, pady=8, padx=10)
        transfer_row.pack(fill=tk.X, pady=5)

        transfer_label = tk.Label(transfer_row, text="Transfer Files", font=self.label_font, bg=theme.ROW_BG, fg=theme.TEXT_COLOR, width=15, anchor="w")
        transfer_label.pack(side=tk.LEFT)

        self.btn_transfer_open = tk.Button(
            transfer_row,
            text="Open",
            font=self.label_font,
            command=self.open_transfer_window,
            cursor="hand2",
            bd=0,
            bg=theme.SUCCESS_COLOR,
            fg=theme.TEXT_COLOR,
            width=8,
            height=1,
        )
        self.btn_transfer_open.pack(side=tk.RIGHT)

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

    def open_transfer_window(self):
        if self.transfer_window and self.transfer_window.winfo_exists():
            self.transfer_window.lift()
            self.transfer_window.focus_force()
            return

        self.transfer_window = tk.Toplevel(self.root)
        self.transfer_window.title("Transfer Files")
        self.transfer_window.geometry("920x560")
        self.transfer_window.configure(bg=theme.WINDOW_BG)
        self.transfer_window.protocol("WM_DELETE_WINDOW", self.close_transfer_window)

        self.transfer_local_file_var = tk.StringVar(self.transfer_window, value="")
        self.transfer_destination_var = tk.StringVar(self.transfer_window, value="/")

        source_frame = tk.Frame(self.transfer_window, bg=theme.WINDOW_BG, padx=10, pady=8)
        source_frame.pack(fill=tk.X)

        source_label = tk.Label(source_frame, text="Local File", font=self.label_font, bg=theme.WINDOW_BG, fg=theme.TEXT_COLOR)
        source_label.pack(side=tk.LEFT)

        source_entry = tk.Entry(
            source_frame,
            textvariable=self.transfer_local_file_var,
            font=self.label_font,
            state="readonly",
            readonlybackground=theme.ROW_BG,
            fg=theme.TEXT_COLOR,
            width=78,
        )
        source_entry.pack(side=tk.LEFT, padx=(8, 8))

        browse_button = tk.Button(
            source_frame,
            text="Browse",
            font=self.label_font,
            command=self.select_transfer_local_file,
            cursor="hand2",
            bd=0,
            bg=theme.INACTIVE_BUTTON_COLOR,
            fg=theme.TEXT_COLOR,
            width=10,
        )
        browse_button.pack(side=tk.LEFT)

        destination_frame = tk.Frame(self.transfer_window, bg=theme.WINDOW_BG, padx=10, pady=4)
        destination_frame.pack(fill=tk.X)

        destination_label = tk.Label(destination_frame, text="Destination", font=self.label_font, bg=theme.WINDOW_BG, fg=theme.TEXT_COLOR)
        destination_label.pack(side=tk.LEFT)

        destination_value = tk.Label(
            destination_frame,
            textvariable=self.transfer_destination_var,
            font=self.label_font,
            bg=theme.WINDOW_BG,
            fg=theme.SUCCESS_COLOR,
            anchor="w",
        )
        destination_value.pack(side=tk.LEFT, padx=(8, 0))

        browser_frame = tk.Frame(self.transfer_window, bg=theme.OUTPUT_BG, padx=10, pady=8)
        browser_frame.pack(fill=tk.BOTH, expand=True)

        self.transfer_tree = ttk.Treeview(browser_frame, columns=("path",), show="tree", selectmode="browse")
        self.transfer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        browser_scrollbar = tk.Scrollbar(browser_frame, orient=tk.VERTICAL, command=self.transfer_tree.yview)
        browser_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transfer_tree.configure(yscrollcommand=browser_scrollbar.set)

        self.transfer_tree.bind("<<TreeviewOpen>>", self._on_transfer_tree_open)
        self.transfer_tree.bind("<<TreeviewSelect>>", self._on_transfer_tree_select)

        action_frame = tk.Frame(self.transfer_window, bg=theme.WINDOW_BG, padx=10, pady=8)
        action_frame.pack(fill=tk.X)

        refresh_button = tk.Button(
            action_frame,
            text="Refresh",
            font=self.label_font,
            command=self.refresh_transfer_locations,
            cursor="hand2",
            bd=0,
            bg=theme.INACTIVE_BUTTON_COLOR,
            fg=theme.TEXT_COLOR,
            width=10,
        )
        refresh_button.pack(side=tk.LEFT)

        transfer_button = tk.Button(
            action_frame,
            text="Transfer",
            font=self.label_font,
            command=self.transfer_file_to_emulator,
            cursor="hand2",
            bd=0,
            bg=theme.SUCCESS_COLOR,
            fg=theme.TEXT_COLOR,
            width=10,
        )
        transfer_button.pack(side=tk.LEFT, padx=(8, 8))

        close_button = tk.Button(
            action_frame,
            text="Close",
            font=self.label_font,
            command=self.close_transfer_window,
            cursor="hand2",
            bd=0,
            bg=theme.ERROR_COLOR,
            fg=theme.TEXT_COLOR,
            width=10,
        )
        close_button.pack(side=tk.LEFT)

        self.refresh_transfer_locations()

    def _join_remote_path(self, base_path, child_name):
        if base_path == "/":
            return f"/{child_name}"
        return f"{base_path.rstrip('/')}/{child_name}"

    def _tree_item_remote_path(self, item_id):
        if not self.transfer_tree:
            return "/"
        values = self.transfer_tree.item(item_id, "values")
        return values[0] if values else "/"

    def _insert_transfer_placeholder(self, parent_id):
        if not self.transfer_tree:
            return
        self.transfer_tree.insert(parent_id, tk.END, text="...", values=("__placeholder__",))

    def _load_transfer_tree_children(self, node_id, remote_path):
        if not self.transfer_tree:
            return

        children = self.transfer_tree.get_children(node_id)
        for child_id in children:
            self.transfer_tree.delete(child_id)

        directories, error_message = self.controller.list_remote_directories(remote_path)
        if error_message:
            return

        for directory_name in directories:
            directory_path = self._join_remote_path(remote_path, directory_name)
            child_node = self.transfer_tree.insert(node_id, tk.END, text=directory_name, values=(directory_path,))
            self._insert_transfer_placeholder(child_node)

    def refresh_transfer_locations(self):
        if not self.transfer_tree:
            return

        root_nodes = self.transfer_tree.get_children("")
        for node_id in root_nodes:
            self.transfer_tree.delete(node_id)

        root_node = self.transfer_tree.insert("", tk.END, text="/", values=("/",))
        self._insert_transfer_placeholder(root_node)
        self.transfer_tree.item(root_node, open=True)
        self._load_transfer_tree_children(root_node, "/")
        self.transfer_tree.focus(root_node)
        self.transfer_tree.selection_set(root_node)
        if self.transfer_destination_var:
            self.transfer_destination_var.set("/")

    def _on_transfer_tree_open(self, _event):
        if not self.transfer_tree:
            return

        node_id = self.transfer_tree.focus()
        if not node_id:
            return

        child_nodes = self.transfer_tree.get_children(node_id)
        if len(child_nodes) != 1:
            return

        placeholder_id = child_nodes[0]
        placeholder_values = self.transfer_tree.item(placeholder_id, "values")
        if not placeholder_values or placeholder_values[0] != "__placeholder__":
            return

        remote_path = self._tree_item_remote_path(node_id)
        self._load_transfer_tree_children(node_id, remote_path)

    def _on_transfer_tree_select(self, _event):
        if not self.transfer_tree or not self.transfer_destination_var:
            return

        selected_nodes = self.transfer_tree.selection()
        if not selected_nodes:
            return

        selected_path = self._tree_item_remote_path(selected_nodes[0])
        self.transfer_destination_var.set(selected_path)

    def select_transfer_local_file(self):
        selected_file_path = filedialog.askopenfilename(title="Select file to transfer")
        if not selected_file_path:
            return
        if self.transfer_local_file_var:
            self.transfer_local_file_var.set(selected_file_path)

    def transfer_file_to_emulator(self):
        local_file_path = self.transfer_local_file_var.get().strip() if self.transfer_local_file_var else ""
        destination_path = self.transfer_destination_var.get().strip() if self.transfer_destination_var else "/"

        if not local_file_path:
            self.update_cmd_output("INVALID_INPUT: Select a local file first.")
            return

        if not destination_path:
            self.update_cmd_output("INVALID_INPUT: Select a destination directory first.")
            return

        self.controller.push_file_to_emulator(local_file_path, destination_path)

    def close_transfer_window(self):
        if self.transfer_window and self.transfer_window.winfo_exists():
            self.transfer_window.destroy()

        self.transfer_window = None
        self.transfer_tree = None
        self.transfer_local_file_var = None
        self.transfer_destination_var = None

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
        self.close_transfer_window()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
