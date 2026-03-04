import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
import threading
import os

# --- BIO-SCANNER THEME ---
BG_COLOR = "#0A0F0D"      # Dark Bio-Organic Black
SCAN_COLOR = "#FF3D00"    # Laser Red/Orange
TEXT_COLOR = "#00E676"    # DNA Green
DIM_COLOR = "#1B5E20"
FONT_MONO = ("Consolas", 10)
FONT_HEADER = ("Consolas", 14, "bold")

class HashApp:
    def __init__(self, root):
        self.root = root
        self.root.title("INTEGRITY_CHECK // HASH_SCANNER")
        self.root.geometry("800x600")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # --- Canvas ---
        self.canvas = tk.Canvas(root, width=800, height=600, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # --- State ---
        self.file_path = tk.StringVar()
        self.md5_val = tk.StringVar(value="---")
        self.sha256_val = tk.StringVar(value="---")
        self.sha512_val = tk.StringVar(value="---")
        
        self.scan_line_y = 0
        self.is_scanning = False
        
        # --- UI Build ---
        self._build_ui()
        self._animate_scan()

    def _build_ui(self):
        # Header
        self.canvas.create_text(400, 40, text="FILE_INTEGRITY_VERIFIER", fill=TEXT_COLOR, font=FONT_HEADER)
        self.canvas.create_line(50, 60, 750, 60, fill=DIM_COLOR, width=2)

        # Input Zone
        self._create_label(50, 100, "TARGET_FILE:")
        self._create_entry(160, 100, self.file_path, 450)
        self._create_btn(630, 100, "[ LOAD ]", self.browse)

        # Hash Display Areas
        self._create_hash_display(50, 180, "MD5_FINGERPRINT", self.md5_val)
        self._create_hash_display(50, 260, "SHA-256_SIGNATURE", self.sha256_val)
        self._create_hash_display(50, 340, "SHA-512_DEEP_SCAN", self.sha512_val)

        # Action Button
        self._create_big_btn(300, 450, "INITIATE SCAN", SCAN_COLOR, self.run_scan)

        # Status
        self.status_text = self.canvas.create_text(400, 550, text="SYSTEM_READY // WAITING_FOR_INPUT", fill="#555", font=FONT_MONO)

    def _create_label(self, x, y, text):
        self.canvas.create_text(x, y, text=text, fill=TEXT_COLOR, font=FONT_MONO, anchor="w")

    def _create_entry(self, x, y, var, w):
        e = tk.Entry(self.root, textvariable=var, bg="#051005", fg="white", insertbackground=TEXT_COLOR, 
                     relief="flat", font=FONT_MONO)
        e.place(x=x, y=y-10, width=w, height=25)
        # Frame
        self.canvas.create_rectangle(x-2, y-12, x+w+2, y+15, outline=DIM_COLOR)

    def _create_btn(self, x, y, text, cmd):
        tk.Button(self.root, text=text, bg=BG_COLOR, fg=TEXT_COLOR, activebackground=TEXT_COLOR, activeforeground="black",
                  relief="flat", font=("Consolas", 9, "bold"), command=cmd).place(x=x, y=y-12, height=25)
        self.canvas.create_rectangle(x-2, y-12, x+70, y+13, outline=TEXT_COLOR)

    def _create_hash_display(self, x, y, label, var):
        self.canvas.create_text(x, y, text=label, fill=DIM_COLOR, font=("Consolas", 8), anchor="w")
        e = tk.Entry(self.root, textvariable=var, bg=BG_COLOR, fg="#CCC", relief="flat", font=("Consolas", 9), state="readonly")
        e.place(x=x, y=y+10, width=700, height=25)
        self.canvas.create_line(x, y+35, x+700, y+35, fill=DIM_COLOR, width=1)

    def _create_big_btn(self, x, y, text, color, cmd):
        tk.Button(self.root, text=text, bg=BG_COLOR, fg=color, font=("Consolas", 12, "bold"),
                  activebackground=color, activeforeground="black", relief="solid", bd=1,
                  command=cmd).place(x=x, y=y, width=200, height=45)

    def _animate_scan(self):
        self.canvas.delete("scan")
        if self.is_scanning:
            self.scan_line_y = (self.scan_line_y + 5) % 600
            self.canvas.create_line(0, self.scan_line_y, 800, self.scan_line_y, fill=SCAN_COLOR, width=2, tags="scan")
            self.canvas.create_rectangle(0, self.scan_line_y, 800, self.scan_line_y+30, fill=SCAN_COLOR, stipple="gray25", outline="", tags="scan")
        
        self.root.after(30, self._animate_scan)

    # --- Logic ---
    def browse(self):
        f = filedialog.askopenfilename()
        if f: self.file_path.set(f)

    def run_scan(self):
        if not self.file_path.get(): return
        self.is_scanning = True
        self.canvas.itemconfig(self.status_text, text="SCANNING_IN_PROGRESS...", fill=SCAN_COLOR)
        threading.Thread(target=self.process).start()

    def process(self):
        try:
            path = self.file_path.get()
            
            # Calculate MD5
            md5 = hashlib.md5()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5.update(chunk)
            self.md5_val.set(md5.hexdigest())

            # Calculate SHA256
            sha256 = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            self.sha256_val.set(sha256.hexdigest())

            # Calculate SHA512
            sha512 = hashlib.sha512()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha512.update(chunk)
            self.sha512_val.set(sha512.hexdigest())

            self.is_scanning = False
            self.canvas.itemconfig(self.status_text, text="INTEGRITY_CHECK_COMPLETE", fill=TEXT_COLOR)
            
        except Exception as e:
            self.is_scanning = False
            messagebox.showerror("ERR", str(e))
            self.canvas.itemconfig(self.status_text, text="SCAN_FAILED", fill="red")