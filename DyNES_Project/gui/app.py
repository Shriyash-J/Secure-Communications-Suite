import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import math
import random

from dynes.cipher import DynesCipher

# --- CYBERPUNK / HACKER THEME ---
BG_COLOR        = "#050814"   # Deep space
PANEL_COLOR     = "#050B1E"   # Dark panel
ACCENT_COLOR    = "#00F6FF"   # Neon cyan
ACCENT_GREEN    = "#27EF9F"   # Neon green
ACCENT_PURPLE   = "#7F5AF0"   # Soft neon purple
TEXT_COLOR      = "#E2E8F0"
LABEL_COLOR     = "#708090"

FONT_MAIN   = ("Consolas", 9)
FONT_BOLD   = ("Consolas", 9, "bold")
FONT_HEADER = ("Consolas", 15, "bold")
FONT_MONO   = ("Consolas", 8)


class DynesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DyNES • Quantum Network Cipher Console")
        self.root.geometry("900x720")          # taller so buttons are visible
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Animation state
        self.scan_y = 0
        self.globe_phase = 0
        self.particles = []

        # --- HOLOGRAPHIC HEADER / CANVAS ZONE ---
        self.header_canvas = tk.Canvas(
            root, bg=BG_COLOR, highlightthickness=0, height=210
        )
        self.header_canvas.pack(fill="x", side="top")

        self._init_bg_grid()
        self._init_globe()
        self._init_particles()

        # --- MAIN CONTAINER ---
        main_frame = tk.Frame(root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Title + subtitle
        title_bar = tk.Frame(main_frame, bg=BG_COLOR)
        title_bar.pack(fill="x", pady=(0, 8))

        tk.Label(
            title_bar,
            text="DyNES PROTOCOL // v3.0",
            font=FONT_HEADER,
            bg=BG_COLOR,
            fg=ACCENT_COLOR,
        ).pack(anchor="w")

        tk.Label(
            title_bar,
            text="Dynamic Network Encryption Standard • Quantum-Enhanced Cipher Suite",
            font=("Consolas", 8),
            bg=BG_COLOR,
            fg=LABEL_COLOR,
        ).pack(anchor="w")

        # Split main area
        body = tk.Frame(main_frame, bg=BG_COLOR)
        body.pack(fill="both", expand=True, pady=(10, 0))

        left = tk.Frame(body, bg=BG_COLOR)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right = tk.Frame(body, bg=BG_COLOR)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        # --- LEFT: INPUT & CONFIG PANELS ---
        self._create_section_label(left, "SOURCE & AUTHENTICATION")

        panel1 = tk.Frame(
            left, bg=PANEL_COLOR, padx=18, pady=16, highlightthickness=1
        )
        panel1.config(highlightbackground="#101826")
        panel1.pack(fill="x", pady=(4, 16))

        self.file_path = tk.StringVar()
        self._add_file_row(panel1, "TARGET PAYLOAD", self.file_path)

        self.password = tk.StringVar()
        self._add_pass_row(panel1, "SECURE KEY", self.password)

        self._create_section_label(left, "ENGINE CONFIGURATION")

        panel2 = tk.Frame(
            left, bg=PANEL_COLOR, padx=18, pady=16, highlightthickness=1
        )
        panel2.config(highlightbackground="#101826")
        panel2.pack(fill="x", pady=(4, 16))

        self.engine_var = tk.StringVar(value="standard")
        self.rounds_var = tk.IntVar(value=16)

        self._add_engine_opts(panel2)
        self._add_rounds_controls(panel2)

        # --- ACTION BUTTONS PANEL ---
        self._create_section_label(left, "ACTIONS")

        btn_frame = tk.Frame(
            left, bg=PANEL_COLOR, padx=18, pady=14, highlightthickness=1
        )
        btn_frame.config(highlightbackground="#1E293B")
        btn_frame.pack(fill="x", pady=(4, 0))

        encrypt_btn = tk.Button(
            btn_frame,
            text="ENCRYPT DATA",
            command=lambda: self.run("encrypt"),
            bg=ACCENT_PURPLE,
            fg="white",
            relief="solid",
            bd=1,
            font=("Consolas", 11, "bold"),
            pady=10,
            padx=10,
            activebackground="#FFFFFF",
            activeforeground="#050814",
            highlightthickness=1,
            highlightbackground="#2D3748",
        )
        encrypt_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        decrypt_btn = tk.Button(
            btn_frame,
            text="DECRYPT DATA",
            command=lambda: self.run("decrypt"),
            bg=ACCENT_GREEN,
            fg="#020617",
            relief="solid",
            bd=1,
            font=("Consolas", 11, "bold"),
            pady=10,
            padx=10,
            activebackground="#FFFFFF",
            activeforeground="#050814",
            highlightthickness=1,
            highlightbackground="#2D3748",
        )
        decrypt_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # --- RIGHT: LIVE DATA / LOG PANEL ---
        self._create_section_label(right, "LIVE ENCRYPTION TELEMETRY")

        log_panel = tk.Frame(
            right, bg=PANEL_COLOR, padx=14, pady=12, highlightthickness=1
        )
        log_panel.config(highlightbackground="#101826")
        log_panel.pack(fill="both", expand=True, pady=(4, 0))

        self.log_text = tk.Text(
            log_panel,
            bg="#020411",
            fg=ACCENT_GREEN,
            insertbackground=ACCENT_COLOR,
            relief="flat",
            font=FONT_MONO,
            height=10,
        )
        self.log_text.pack(fill="both", expand=True, pady=(18, 4))

        tk.Label(
            log_panel,
            text=">> ENCRYPTED TRAFFIC / STATUS FEED",
            font=("Consolas", 8, "bold"),
            bg=PANEL_COLOR,
            fg=ACCENT_COLOR,
            anchor="w",
        ).place(x=0, y=0)

        # --- STATUS BAR ---
        self.status_lbl = tk.Label(
            root,
            text="SYSTEM IDLE / AWAITING PAYLOAD",
            bg="#02030A",
            fg="#4A5568",
            font=("Consolas", 9),
            anchor="w",
            padx=24,
            pady=6,
        )
        self.status_lbl.pack(side="bottom", fill="x")

        # Start animations
        self._animate()

    # ------------------------------------------------------------------
    #  Holographic / animated background
    # ------------------------------------------------------------------
    def _init_bg_grid(self):
        h = 210
        spacing = 24
        for x in range(0, 1200, spacing):
            self.header_canvas.create_line(
                x, 0, x - 80, h,
                fill="#07101F",
                width=1
            )
        for y in range(0, h + spacing, spacing):
            self.header_canvas.create_line(
                0, y, 1200, y,
                fill="#050F1E",
                width=1
            )

        self.header_canvas.create_oval(
            280, 10, 620, 200,
            outline="#0B1F33",
            width=2
        )

        self.code_columns = []
        for _ in range(18):
            x = random.randint(40, 860)
            line = self.header_canvas.create_line(
                x, 30, x, 180,
                fill="#061922",
                width=2
            )
            self.code_columns.append(line)

    def _init_globe(self):
        self.globe_center = (450, 105)
        self.globe_radius = 70

        cx, cy = self.globe_center
        r = self.globe_radius

        self.header_canvas.create_oval(
            cx - r - 10,
            cy - r - 10,
            cx + r + 10,
            cy + r + 10,
            outline="#061D2D",
            width=3,
        )

        self.globe_base = self.header_canvas.create_oval(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            outline=ACCENT_COLOR,
            width=2,
        )

        self.globe_lines = []
        for angle in range(-60, 61, 30):
            a = math.radians(angle)
            x1 = cx - r * math.cos(a)
            x2 = cx + r * math.cos(a)
            self.globe_lines.append(
                self.header_canvas.create_oval(
                    x1, cy - r,
                    x2, cy + r,
                    outline="#073644",
                    width=1,
                )
            )

        for angle in range(-60, 61, 30):
            a = math.radians(angle)
            y1 = cy - r * math.cos(a)
            y2 = cy + r * math.cos(a)
            self.globe_lines.append(
                self.header_canvas.create_oval(
                    cx - r, y1,
                    cx + r, y2,
                    outline="#073644",
                    width=1,
                )
            )

        self.globe_orbit = self.header_canvas.create_oval(
            cx - r - 16,
            cy - r + 14,
            cx + r + 16,
            cy + r - 14,
            outline=ACCENT_GREEN,
            width=1,
            dash=(4, 4),
        )

        self.satellite = self.header_canvas.create_oval(
            cx + r + 10,
            cy - 4,
            cx + r + 18,
            cy + 4,
            fill=ACCENT_GREEN,
            outline="",
        )

    def _init_particles(self):
        self.particles = []
        for _ in range(35):
            x = random.randint(20, 880)
            y = random.randint(20, 190)
            vx = random.choice([-1, 1]) * random.uniform(0.5, 1.3)
            vy = random.choice([-1, 1]) * random.uniform(0.1, 0.6)
            size = random.randint(1, 3)
            item = self.header_canvas.create_oval(
                x, y, x + size, y + size,
                fill=ACCENT_COLOR,
                outline=""
            )
            self.particles.append([item, vx, vy])

        self.scan_line = self.header_canvas.create_line(
            0, 0, 900, 0,
            fill="#053E4F",
            width=2
        )

    def _animate(self):
        self.scan_y = (self.scan_y + 1.5) % 210
        self.header_canvas.coords(self.scan_line, 0, self.scan_y, 900, self.scan_y)

        for col in self.code_columns:
            offset = random.randint(20, 160)
            self.header_canvas.itemconfig(col, dash=(offset, 200), fill="#062533")

        self.globe_phase = (self.globe_phase + 3) % 360
        cx, cy = self.globe_center
        r = self.globe_radius + 18
        rad = math.radians(self.globe_phase)
        sx = cx + r * math.cos(rad)
        sy = cy + r * math.sin(rad) * 0.4

        self.header_canvas.coords(
            self.satellite, sx - 4, sy - 4, sx + 4, sy + 4
        )

        for p in self.particles:
            item, vx, vy = p
            self.header_canvas.move(item, vx, vy)
            x1, y1, x2, y2 = self.header_canvas.coords(item)

            if x2 < 0:
                self.header_canvas.move(item, 900 - x1, 0)
            elif x1 > 900:
                self.header_canvas.move(item, -x2, 0)

            if y2 < 0:
                self.header_canvas.move(item, 0, 210 - y1)
            elif y1 > 210:
                self.header_canvas.move(item, 0, -y2)

        glow_width = 2 + 1.0 * math.sin(math.radians(self.globe_phase))
        self.header_canvas.itemconfig(self.globe_base, width=max(1, glow_width))

        self.root.after(30, self._animate)

    # ------------------------------------------------------------------
    #  UI building blocks
    # ------------------------------------------------------------------
    def _create_section_label(self, parent, txt):
        tk.Label(
            parent,
            text=txt,
            font=("Consolas", 8, "bold"),
            bg=BG_COLOR,
            fg=LABEL_COLOR,
        ).pack(anchor="w", pady=(0, 2))

    def _add_file_row(self, parent, label, var):
        tk.Label(
            parent,
            text=label,
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=FONT_BOLD,
        ).pack(anchor="w")

        row = tk.Frame(parent, bg=PANEL_COLOR)
        row.pack(fill="x", pady=(6, 14))

        entry = tk.Entry(
            row,
            textvariable=var,
            bg="#020411",
            fg=ACCENT_COLOR,
            insertbackground=ACCENT_COLOR,
            relief="flat",
            font=FONT_MAIN,
        )
        entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        tk.Button(
            row,
            text="BROWSE",
            command=self.browse,
            bg="#0B1224",
            fg=TEXT_COLOR,
            activebackground="#151B32",
            activeforeground=ACCENT_COLOR,
            relief="solid",
            bd=1,
            font=("Consolas", 8, "bold"),
            padx=10,
            pady=4,
        ).pack(side="left")

    def _add_pass_row(self, parent, label, var):
        tk.Label(
            parent,
            text=label,
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=FONT_BOLD,
        ).pack(anchor="w")

        tk.Entry(
            parent,
            textvariable=var,
            show="•",
            bg="#020411",
            fg=ACCENT_GREEN,
            insertbackground=ACCENT_GREEN,
            relief="flat",
            font=FONT_MAIN,
        ).pack(fill="x", pady=(6, 4), ipady=6)

    def _add_engine_opts(self, parent):
        row = tk.Frame(parent, bg=PANEL_COLOR)
        row.pack(fill="x", pady=(0, 12))

        tk.Label(
            row,
            text="ALGORITHM",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=FONT_BOLD,
        ).pack(side="left")

        style = {
            "bg": PANEL_COLOR,
            "fg": LABEL_COLOR,
            "selectcolor": "#020411",
            "activebackground": PANEL_COLOR,
            "activeforeground": ACCENT_COLOR,
            "font": ("Consolas", 8),
        }

        tk.Radiobutton(
            row,
            text="Standard Bitwise",
            variable=self.engine_var,
            value="standard",
            **style,
        ).pack(side="left", padx=16)

        tk.Radiobutton(
            row,
            text="Chaos Theory",
            variable=self.engine_var,
            value="chaos",
            **style,
        ).pack(side="left")

    def _add_rounds_controls(self, parent):
        row = tk.Frame(parent, bg=PANEL_COLOR)
        row.pack(fill="x", pady=(4, 0))

        tk.Label(
            row,
            text="COMPLEXITY ROUNDS",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=FONT_BOLD,
        ).pack(side="left")

        controls = tk.Frame(row, bg=PANEL_COLOR)
        controls.pack(side="right")

        minus_btn = tk.Button(
            controls,
            text="-",
            command=lambda: self._adjust_rounds(-1),
            bg="#020411",
            fg=ACCENT_COLOR,
            relief="solid",
            bd=1,
            width=3,
            font=("Consolas", 9, "bold"),
            activebackground="#151B32",
            activeforeground=ACCENT_COLOR,
        )
        minus_btn.pack(side="left", padx=(0, 4))

        value_lbl = tk.Label(
            controls,
            textvariable=self.rounds_var,
            bg=PANEL_COLOR,
            fg=ACCENT_COLOR,
            font=FONT_BOLD,
            width=3,
            anchor="center",
        )
        value_lbl.pack(side="left")

        plus_btn = tk.Button(
            controls,
            text="+",
            command=lambda: self._adjust_rounds(1),
            bg="#020411",
            fg=ACCENT_COLOR,
            relief="solid",
            bd=1,
            width=3,
            font=("Consolas", 9, "bold"),
            activebackground="#151B32",
            activeforeground=ACCENT_COLOR,
        )
        plus_btn.pack(side="left", padx=(4, 0))

    def _adjust_rounds(self, delta: int):
        v = self.rounds_var.get() + delta
        if v < 8:
            v = 8
        if v > 64:
            v = 64
        self.rounds_var.set(v)

    # ------------------------------------------------------------------
    #  Actions
    # ------------------------------------------------------------------
    def browse(self):
        f = filedialog.askopenfilename()
        if f:
            self.file_path.set(f)
            self._log(f"[+] Target locked: {f}")

    def run(self, mode):
        if not self.file_path.get() or not self.password.get():
            messagebox.showwarning("Input Required", "Select a file and enter a key.")
            return

        operation = "ENCRYPT" if mode == "encrypt" else "DECRYPT"

        self.status_lbl.config(
            text=f"{operation}ION SEQUENCE ENGAGED • Working...",
            fg=ACCENT_COLOR,
        )
        self._log(f"[#] {operation}ION sequence initiated.")
        self._log(
            f"    Engine: {self.engine_var.get()} | Rounds: {self.rounds_var.get()}"
        )

        t = threading.Thread(target=self.process, args=(mode,), daemon=True)
        t.start()

    def process(self, mode):
        try:
            cipher = DynesCipher(
                self.password.get(), self.rounds_var.get(), self.engine_var.get()
            )

            path = self.file_path.get()
            d, f = os.path.split(path)

            if mode == "encrypt":
                out = os.path.join(d, f"ENC_{f}")
            else:
                base_name = f.replace("ENC_", "")
                out = os.path.join(d, f"DEC_{base_name}")

            self._log("[>] Processing payload...")
            cipher.process_file(path, out, mode)
            self._log(f"[✓] Operation complete. Output: {out}")

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success", f"Operation Complete.\nOutput: {out}"
                ),
            )
            self.root.after(
                0,
                lambda: self.status_lbl.config(
                    text="READY • Awaiting next payload", fg=ACCENT_GREEN
                ),
            )
        except Exception as e:
            self._log(f"[!] ERROR: {e}")
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", str(e)),
            )
            self.root.after(
                0,
                lambda: self.status_lbl.config(
                    text="FAULT DETECTED • Check logs", fg="#FF5555"
                ),
            )

    def _log(self, msg: str):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")


if __name__ == "__main__":
    root = tk.Tk()
    app = DynesApp(root)
    root.mainloop()
