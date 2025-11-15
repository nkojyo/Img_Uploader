# gui.py（プログレスバー付き）
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from img_uploader import remote_file_exists, upload_directory
import json
import os
from ftplib import FTP_TLS

class UploadGUI:
    def __init__(self, master):
        self.master = master
        master.title("FTPS Uploader")
        master.geometry("800x600")

        self.info_label = tk.Label(master,
            text="まず『ファイル選択』ボタンを押してアップロード対象を確認・選択してください。",
            wraplength=780, justify="left")
        self.info_label.pack(pady=5)

        self.server_label = tk.Label(master, text="")
        self.server_label.pack(pady=5)

        self.pick_btn = tk.Button(master, text="ファイル選択", width=20, command=self.pick_files)
        self.pick_btn.pack(pady=5)

        self.selected_frame = tk.Frame(master)
        self.selected_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        self.start_btn = tk.Button(master, text="アップロード開始", width=20, command=self.start_upload)
        self.start_btn.pack(pady=5)

        self.log_box = scrolledtext.ScrolledText(master, width=100, height=20)
        self.log_box.pack(padx=10, pady=10)

        self.settings = self.load_settings()
        self.update_server_info()

        self.file_vars = {}
        self.file_list = []
        self.selected_files = []

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json") as f:
                return json.load(f)
        return {}

    def update_server_info(self):
        host = self.settings.get("host", "未設定")
        remote_base = self.settings.get("remote_base", "/")
        self.server_label.config(text=f"サーバ: {host} | リモートベース: {remote_base}")

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.master.update()

    # ---------------------------
    # ファイル選択
    # ---------------------------
    def pick_files(self):
        local_base = self.settings.get("local_base", "common")
        remote_base = self.settings.get("remote_base", "/")

        if not os.path.exists(local_base):
            messagebox.showerror("Error", f"{local_base} が存在しません")
            return

        host = self.settings["host"]
        port = self.settings.get("port", 21)
        user = self.settings["user"]
        passwd = self.settings["password"]
        ftps = FTP_TLS()
        ftps.connect(host, port)
        ftps.login(user, passwd)
        ftps.prot_p()

        self.file_list.clear()
        for root, dirs, files in os.walk(local_base):
            rel_path = os.path.relpath(root, local_base)
            for file in files:
                local_file = os.path.join(root, file)
                remote_file = os.path.join(remote_base, rel_path, file).replace("\\", "/")
                self.file_list.append((local_file, remote_file))

        if not self.file_list:
            messagebox.showinfo("Info", "アップロード対象ファイルがありません")
            ftps.quit()
            return

        self.file_vars.clear()

        # ---------------------------
        # 一覧ウィンドウ作成（非表示）
        # ---------------------------
        win = tk.Toplevel(self.master)
        win.withdraw()
        win.title("アップロードファイル選択")
        win.geometry("700x500")
        win.minsize(400, 300)
        win.resizable(True, True)
        win.transient(self.master)
        win.grab_set()

        self.master.update_idletasks()
        main_x = self.master.winfo_x()
        main_y = self.master.winfo_y()
        main_width = self.master.winfo_width()
        main_height = self.master.winfo_height()
        win_width = 700
        win_height = 500
        pos_x = main_x + (main_width - win_width) // 2
        pos_y = main_y + (main_height - win_height) // 2
        win.geometry(f"{win_width}x{win_height}+{pos_x}+{pos_y}")

        # ---------------------------
        # 読み込み中インジケーター
        # ---------------------------
        status_frame = tk.Frame(win)
        status_frame.pack(fill=tk.BOTH, expand=True)
        lbl = tk.Label(status_frame, text="ファイル一覧取得中…")
        lbl.pack(pady=10)
        progress = ttk.Progressbar(status_frame, mode="determinate", maximum=len(self.file_list))
        progress.pack(fill=tk.X, padx=20, pady=10)

        # ---------------------------
        # スクロールフレーム（非表示）
        # ---------------------------
        canvas = tk.Canvas(win)
        scrollbar_y = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(win, orient="horizontal", command=canvas.xview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # ---------------------------
        # チェックボックス生成（非同期風に after() で更新）
        # ---------------------------
        def build_checkboxes(idx=0):
            if idx >= len(self.file_list):
                # 完了したらスクロールフレーム表示
                status_frame.destroy()
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar_y.pack(side="right", fill="y")
                scrollbar_x.pack(side="bottom", fill="x")

                btn_confirm = tk.Button(win, text="確定", command=confirm_selection)
                btn_confirm.pack(pady=5)
                return

            local_file, remote_file = self.file_list[idx]
            try:
                exists = remote_file_exists(ftps, remote_file)
            except Exception:
                exists = False
            var = tk.BooleanVar(value=not exists)
            chk_text = f"{local_file}" + (" (既存)" if exists else "")
            chk = tk.Checkbutton(scroll_frame, text=chk_text, variable=var, anchor="w", justify="left")
            chk.pack(fill=tk.X, anchor="w")
            self.file_vars[(local_file, remote_file)] = var

            progress['value'] = idx + 1
            win.update_idletasks()
            win.after(1, lambda: build_checkboxes(idx + 1))

        # ---------------------------
        # 確定ボタン動作
        # ---------------------------
        def confirm_selection():
            self.selected_files.clear()
            for f, var in self.file_vars.items():
                if var.get():
                    self.selected_files.append(f)
            self.display_selected_files()
            win.destroy()

        win.deiconify()
        build_checkboxes()

        self.master.wait_window(win)

        ftps.quit()

    # ---------------------------
    # 選択済みファイル表示
    # ---------------------------
    def display_selected_files(self):
        for widget in self.selected_frame.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.selected_frame)
        scrollbar_y = ttk.Scrollbar(self.selected_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")

        for local_file, remote_file in self.selected_files:
            tk.Label(scroll_frame, text=f"{local_file} -> {remote_file}", anchor="w", justify="left").pack(fill=tk.X, anchor="w")

        self.log(f"{len(self.selected_files)} ファイルを選択済みです。")

    # ---------------------------
    # アップロード開始
    # ---------------------------
    def start_upload(self):
        if not self.selected_files:
            messagebox.showinfo("Info", "アップロード対象ファイルが選択されていません")
            return

        self.log("=== Upload開始 ===")
        try:
            upload_directory(self.settings, log_callback=self.log, target_list=self.selected_files)
            self.log("=== Upload完了 ===")
        except Exception as e:
            self.log(f"Error: {e}")
