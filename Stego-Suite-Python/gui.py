import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import core_logic
from utils import file_io
import threading
import os
import logging
import random
import math

# --- TACTICAL CYBER-STEALTH THEME ---
APP_BG        = "#050607"   # Near-black
FRAME_BG      = "#14171A"   # Dark panel
PANEL_EDGE    = "#22262B"
TEXT_COLOR    = "#E0E0E0"   # Off-white
MUTED_TEXT    = "#6C7A80"
ACCENT_CYAN   = "#00B4D8"   # Neon blue-cyan
SUCCESS_COLOR = "#00E676"   # Matrix green
ERROR_COLOR   = "#FF1744"   # Neon red
WARN_COLOR    = "#F6C453"   # Tactical amber

FONT_MAIN  = ("Consolas", 10)
FONT_BOLD  = ("Consolas", 10, "bold")
FONT_TITLE = ("Consolas", 16, "bold")


class StegoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STEGO_SUITE // PROTOCOL_V1")
        self.root.geometry("900x620")
        self.root.configure(bg=APP_BG)
        self.root.resizable(False, False)

        # --- Variables ---
        self.secret_file = tk.StringVar(value="[NO FILE SELECTED]")
        self.cover_file = tk.StringVar(value="[NO FILE SELECTED]")
        self.stego_file = tk.StringVar(value="[NO FILE SELECTED]")

        # for carrier-morph preview text
        self.carrier_mode = tk.StringVar(value="IDLE")

        # --- Style Configuration ---
        style = ttk.Style()
        style.theme_use("clam")

        # Notebook (tabs)
        style.configure("TNotebook", background=APP_BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=FRAME_BG,
            foreground=TEXT_COLOR,
            padding=[18, 6],
            font=FONT_BOLD,
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", ACCENT_CYAN)],
            foreground=[("selected", "#000000")],
        )

        # Card-like frames
        style.configure("Card.TFrame", background=FRAME_BG, relief="flat")

        # Buttons
        style.configure(
            "Action.TButton",
            background=ACCENT_CYAN,
            foreground="#000000",
            font=("Consolas", 11, "bold"),
            padding=8,
            borderwidth=0,
        )
        style.map(
            "Action.TButton",
            background=[("active", "#0096C7")],
        )

        style.configure(
            "Browse.TButton",
            background="#252A30",
            foreground=ACCENT_CYAN,
            font=("Consolas", 9),
            padding=4,
            borderwidth=1,
        )
        style.map("Browse.TButton", background=[("active", "#323840")])

        # --- HEADER: RADAR / PACKET / BYTE STREAM ---
        header = tk.Frame(root, bg=APP_BG, pady=6)
        header.pack(fill="x")

        # Title block (left)
        title_block = tk.Frame(header, bg=APP_BG)
        title_block.pack(side="left", fill="y", padx=(18, 8))

        tk.Label(
            title_block,
            text="STEGO_SUITE // PROTOCOL_V1",
            font=("Consolas", 18, "bold"),
            bg=APP_BG,
            fg=ACCENT_CYAN,
        ).pack(anchor="w")

        tk.Label(
            title_block,
            text="COVERT PAYLOAD EMBEDDING • SIGNAL-SECURITY TERMINAL",
            font=("Consolas", 8),
            bg=APP_BG,
            fg=MUTED_TEXT,
        ).pack(anchor="w")

        # Header visual zone (right)
        visual_block = tk.Frame(header, bg=APP_BG)
        visual_block.pack(side="right", fill="both", expand=True, padx=(0, 18))

        self.header_canvas = tk.Canvas(
            visual_block, bg=APP_BG, height=140, highlightthickness=0
        )
        self.header_canvas.pack(fill="x")

        # Byte-stream label (encrypted stream simulation)
        self.byte_label = tk.Label(
            visual_block,
            text="",
            font=("Consolas", 8),
            bg=APP_BG,
            fg=SUCCESS_COLOR,
            anchor="e",
        )
        self.byte_label.pack(fill="x", pady=(2, 0))

        # Initialize animated elements
        self._init_header_scene()

        # --- NOTEBOOK (ENCODE / DECODE) ---
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both", padx=18, pady=(4, 4))

        self.encode_frame = ttk.Frame(notebook, style="Card.TFrame", padding=18)
        self.decode_frame = ttk.Frame(notebook, style="Card.TFrame", padding=18)

        notebook.add(self.encode_frame, text="  ENCODE  ")
        notebook.add(self.decode_frame, text="  DECODE  ")

        # Build tabs
        self._build_encode_tab()
        self._build_decode_tab()

        # --- TERMINAL LOG CONSOLE ---
        console_frame = tk.Frame(root, bg=APP_BG)
        console_frame.pack(fill="both", padx=18, pady=(0, 4))

        tk.Label(
            console_frame,
            text="TACTICAL_EVENT_LOG",
            font=("Consolas", 9, "bold"),
            bg=APP_BG,
            fg=MUTED_TEXT,
            anchor="w",
        ).pack(fill="x")

        self.log_console = tk.Text(
            console_frame,
            height=6,
            bg="#050708",
            fg="#A0AEC0",
            insertbackground=ACCENT_CYAN,
            relief="solid",
            bd=1,
            font=("Consolas", 9),
        )
        self.log_console.pack(fill="both", expand=True)
        self.log_console.insert("end", "[BOOT] Stego console online.\n")
        self.log_console.config(state="disabled")

        # --- STATUS BAR ---
        self.status_bar = tk.Label(
            root,
            text="SYSTEM READY • AWAITING OPERATION",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#000000",
            fg=ACCENT_CYAN,
            font=("Consolas", 9),
            pady=4,
            padx=10,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Kick off animations
        self._animate_header()
        self._animate_byte_stream()

    # ==================================================================
    #   HEADER SCENE: radar, hex grid, packet flow, carrier morph
    # ==================================================================
    def _init_header_scene(self):
        w = 600  # logical width, will stretch though
        h = 140
        self.header_canvas.config(scrollregion=(0, 0, w, h))

        # hex-grid style background (diagonal lines)
        spacing = 18
        for x in range(-40, w + 40, spacing):
            self.header_canvas.create_line(
                x, 0, x + 80, h, fill="#101317", width=1
            )
        for x in range(-40, w + 40, spacing):
            self.header_canvas.create_line(
                x, 0, x - 80, h, fill="#0B0E12", width=1
            )

        # Central radar circle
        self.radar_center = (w * 0.35, h * 0.55)
        cx, cy = self.radar_center
        self.radar_radius = 40

        self.header_canvas.create_oval(
            cx - self.radar_radius - 10,
            cy - self.radar_radius - 10,
            cx + self.radar_radius + 10,
            cy + self.radar_radius + 10,
            outline="#1E242C",
            width=2,
        )

        self.radar_main = self.header_canvas.create_oval(
            cx - self.radar_radius,
            cy - self.radar_radius,
            cx + self.radar_radius,
            cy + self.radar_radius,
            outline=ACCENT_CYAN,
            width=2,
        )

        # Radar rings
        for r in (14, 26):
            self.header_canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r, outline="#18323A", width=1
            )

        # Radar sweep (rotating line)
        self.radar_angle = 0
        self.radar_sweep = self.header_canvas.create_line(
            cx, cy, cx + self.radar_radius, cy, fill=ACCENT_CYAN, width=2
        )

        # Packets moving along a path (horizontal)
        self.packets = []
        for _ in range(8):
            px = random.randint(int(w * 0.45), int(w * 0.95))
            py = random.randint(int(h * 0.25), int(h * 0.75))
            size = random.randint(3, 6)
            rect = self.header_canvas.create_rectangle(
                px,
                py,
                px + size,
                py + size,
                outline="",
                fill=SUCCESS_COLOR,
            )
            speed = random.uniform(1.0, 2.5)
            self.packets.append([rect, px, py, speed])

        # Scanning bar (vertical)
        self.scan_x = 0
        self.scan_bar = self.header_canvas.create_rectangle(
            0, 0, 3, h, fill="#102027", outline=""
        )

        # "Carrier morphing" thumbnail (right side)
        thumb_x = w * 0.78
        thumb_y = h * 0.25
        thumb_w = 90
        thumb_h = 60
        self.thumb_rect = self.header_canvas.create_rectangle(
            thumb_x,
            thumb_y,
            thumb_x + thumb_w,
            thumb_y + thumb_h,
            outline=ACCENT_CYAN,
            width=2,
        )
        self.thumb_inner = self.header_canvas.create_rectangle(
            thumb_x + 6,
            thumb_y + 6,
            thumb_x + thumb_w - 6,
            thumb_y + thumb_h - 6,
            outline="#1A2A35",
            fill="#05090D",
            width=1,
        )

        self.thumb_label = self.header_canvas.create_text(
            thumb_x + thumb_w / 2,
            thumb_y + thumb_h / 2,
            text="CARRIER: IDLE",
            font=("Consolas", 8, "bold"),
            fill=MUTED_TEXT,
        )

        # Glitch flicker for thumbnail border
        self.thumb_glitch_phase = 0

    def _animate_header(self):
        # Radar sweep update
        self.radar_angle = (self.radar_angle + 4) % 360
        cx, cy = self.radar_center
        rad = math.radians(self.radar_angle)
        x2 = cx + self.radar_radius * math.cos(rad)
        y2 = cy + self.radar_radius * math.sin(rad)
        self.header_canvas.coords(self.radar_sweep, cx, cy, x2, y2)

        # Slight pulsation for radar main circle
        width = 1.5 + 0.7 * math.sin(math.radians(self.radar_angle * 2))
        self.header_canvas.itemconfig(self.radar_main, width=width)

        # Scan bar
        bbox = self.header_canvas.bbox(self.scan_bar)
        if bbox:
            _, _, _, h = self.header_canvas.bbox(self.scan_bar)
        else:
            h = 140
        self.scan_x = (self.scan_x + 2) % 600
        self.header_canvas.coords(self.scan_bar, self.scan_x, 0, self.scan_x + 3, h)

        # Packets movement
        for p in self.packets:
            rect, px, py, speed = p
            px += speed
            if px > 600:
                px = 350  # restart near radar
                py = random.randint(40, 110)
                speed = random.uniform(1.0, 2.5)
                p[2] = py
                p[3] = speed
            p[1] = px
            self.header_canvas.coords(rect, px, py, px + 5, py + 5)

        # Thumbnail glitch / morph
        self.thumb_glitch_phase = (self.thumb_glitch_phase + 1) % 60
        if self.thumb_glitch_phase in (0, 1, 2):
            # momentary glitch color
            self.header_canvas.itemconfig(self.thumb_rect, outline=ERROR_COLOR)
        else:
            # normal border with carrier mode color
            if self.carrier_mode.get() == "IMAGE":
                col = ACCENT_CYAN
            elif self.carrier_mode.get() == "AUDIO":
                col = SUCCESS_COLOR
            elif self.carrier_mode.get() == "STEGO":
                col = WARN_COLOR
            else:
                col = "#3A444E"
            self.header_canvas.itemconfig(self.thumb_rect, outline=col)

        # Schedule next frame
        self.root.after(40, self._animate_header)

    def _animate_byte_stream(self):
        # Generate fake encrypted byte stream
        groups = []
        for _ in range(8):
            byte = "".join(random.choice("0123456789ABCDEF") for _ in range(2))
            groups.append(byte)
        stream = " ".join(groups)
        prefix = random.choice(["TX", "RX", "KEY", "IV", "CHK"])
        self.byte_label.config(text=f"{prefix} :: {stream}")
        self.root.after(140, self._animate_byte_stream)

    # ==================================================================
    #   ENCODE TAB
    # ==================================================================
    def _build_encode_tab(self):
        frame = self.encode_frame
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)

        # Left column: file + key
        left = tk.Frame(frame, bg=FRAME_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Secret
        self._create_file_selector(
            left,
            "1. TARGET_DATA (SECRET PAYLOAD)",
            self.secret_file,
            self._select_secret_file,
            start_row=0,
        )

        # Cover (carrier)
        self._create_file_selector(
            left,
            "2. CARRIER_FILE (IMAGE / AUDIO)",
            self.cover_file,
            self._select_cover_file,
            start_row=1,
        )

        # Password
        tk.Label(
            left,
            text="3. ENCRYPTION_KEY",
            font=FONT_BOLD,
            bg=FRAME_BG,
            fg=TEXT_COLOR,
        ).grid(row=4, column=0, sticky="w", pady=(16, 5))

        self.encode_password = tk.Entry(
            left,
            show="*",
            width=40,
            bg="#22272C",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=FONT_MAIN,
        )
        self.encode_password.grid(
            row=5, column=0, columnspan=2, sticky="ew", ipady=5
        )

        # Encode action button
        ttk.Button(
            left,
            text="INITIALIZE_EMBEDDING_SEQUENCE",
            style="Action.TButton",
            command=self._run_encode_thread,
        ).grid(row=6, column=0, columnspan=2, pady=22, sticky="ew")

        # Right column: carrier preview / activity monitor
        right = tk.Frame(frame, bg=FRAME_BG)
        right.grid(row=0, column=1, sticky="ns")

        tk.Label(
            right,
            text="CARRIER_ACTIVITY_MONITOR",
            font=("Consolas", 9, "bold"),
            bg=FRAME_BG,
            fg=MUTED_TEXT,
        ).pack(anchor="w", pady=(0, 4))

        self.encode_monitor_canvas = tk.Canvas(
            right, width=200, height=140, bg="#050708", highlightthickness=1
        )
        self.encode_monitor_canvas.config(highlightbackground=PANEL_EDGE)
        self.encode_monitor_canvas.pack()

        # simple waveform-like animation
        self.monitor_phase = 0
        self._draw_encode_monitor_base()
        self._animate_encode_monitor()

    def _draw_encode_monitor_base(self):
        c = self.encode_monitor_canvas
        c.delete("base")
        w, h = 200, 140

        # Grid
        for x in range(0, w, 20):
            c.create_line(x, 0, x, h, fill="#101317", tags="base")
        for y in range(0, h, 20):
            c.create_line(0, y, w, y, fill="#101317", tags="base")

        # Label
        c.create_text(
            6,
            6,
            text="ENCODE LINK",
            anchor="nw",
            font=("Consolas", 7),
            fill="#555F6A",
            tags="base",
        )

    def _animate_encode_monitor(self):
        c = self.encode_monitor_canvas
        w, h = 200, 140
        c.delete("wave")

        self.monitor_phase = (self.monitor_phase + 1) % 360
        phase = math.radians(self.monitor_phase)

        last_x, last_y = 0, h / 2
        for x in range(0, w, 4):
            y = h / 2 + 22 * math.sin(phase + x * 0.08)
            c.create_line(last_x, last_y, x, y, fill=ACCENT_CYAN, tags="wave")
            last_x, last_y = x, y

        # pulsating node
        r = 4 + 1.5 * math.sin(phase * 3)
        c.create_oval(
            w - 30 - r,
            h / 2 - r,
            w - 30 + r,
            h / 2 + r,
            outline=SUCCESS_COLOR,
            tags="wave",
        )

        self.root.after(60, self._animate_encode_monitor)

    # ==================================================================
    #   DECODE TAB
    # ==================================================================
    def _build_decode_tab(self):
        frame = self.decode_frame
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)

        left = tk.Frame(frame, bg=FRAME_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Stego file
        self._create_file_selector(
            left,
            "1. SOURCE_CARRIER (STEGO FILE)",
            self.stego_file,
            self._select_stego_file,
            start_row=0,
        )

        # Password
        tk.Label(
            left,
            text="2. DECRYPTION_KEY",
            font=FONT_BOLD,
            bg=FRAME_BG,
            fg=TEXT_COLOR,
        ).grid(row=2, column=0, sticky="w", pady=(16, 5))

        self.decode_password = tk.Entry(
            left,
            show="*",
            width=40,
            bg="#22272C",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=FONT_MAIN,
        )
        self.decode_password.grid(
            row=3, column=0, columnspan=2, sticky="ew", ipady=5
        )

        ttk.Button(
            left,
            text="EXTRACT_HIDDEN_PAYLOAD",
            style="Action.TButton",
            command=self._run_decode_thread,
        ).grid(row=4, column=0, columnspan=2, pady=22, sticky="ew")

        # Right monitor
        right = tk.Frame(frame, bg=FRAME_BG)
        right.grid(row=0, column=1, sticky="ns")

        tk.Label(
            right,
            text="DECODE_ACTIVITY_MONITOR",
            font=("Consolas", 9, "bold"),
            bg=FRAME_BG,
            fg=MUTED_TEXT,
        ).pack(anchor="w", pady=(0, 4))

        self.decode_monitor_canvas = tk.Canvas(
            right, width=200, height=140, bg="#050708", highlightthickness=1
        )
        self.decode_monitor_canvas.config(highlightbackground=PANEL_EDGE)
        self.decode_monitor_canvas.pack()

        self.decode_phase = 0
        self._draw_decode_monitor_base()
        self._animate_decode_monitor()

    def _draw_decode_monitor_base(self):
        c = self.decode_monitor_canvas
        c.delete("base")
        w, h = 200, 140

        # vertical scan bars
        for x in range(0, w, 14):
            c.create_rectangle(
                x, 0, x + 6, h, outline="#101317", fill="#050708", tags="base"
            )

        c.create_text(
            6,
            6,
            text="DECODE LINK",
            anchor="nw",
            font=("Consolas", 7),
            fill="#555F6A",
            tags="base",
        )

    def _animate_decode_monitor(self):
        c = self.decode_monitor_canvas
        w, h = 200, 140
        c.delete("scan")

        self.decode_phase = (self.decode_phase + 4) % w
        x = self.decode_phase
        c.create_rectangle(
            x,
            0,
            x + 12,
            h,
            outline="",
            fill="#0A3742",
            tags="scan",
        )

        self.root.after(60, self._animate_decode_monitor)

    # ==================================================================
    #   Shared widgets
    # ==================================================================
    def _create_file_selector(self, parent, title, var, command, start_row):
        tk.Label(
            parent,
            text=title,
            font=FONT_BOLD,
            bg=FRAME_BG,
            fg=TEXT_COLOR,
        ).grid(row=start_row * 2, column=0, sticky="w", pady=(5, 4), columnspan=2)

        entry = tk.Entry(
            parent,
            textvariable=var,
            width=60,
            bg="#111418",
            fg="#A0AEC0",
            relief="flat",
            font=("Consolas", 9),
            state="readonly",
        )
        entry.grid(
            row=start_row * 2 + 1, column=0, sticky="ew", ipady=5, padx=(0, 6)
        )

        btn = ttk.Button(
            parent,
            text="BROWSE",
            style="Browse.TButton",
            command=command,
        )
        btn.grid(row=start_row * 2 + 1, column=1, padx=(0, 0))

    # ==================================================================
    #   Logic hooks
    # ==================================================================
    def _select_secret_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.secret_file.set(path)
            self._log(f"[ENC] Secret payload selected: {os.path.basename(path)}")

    def _select_cover_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.cover_file.set(path)
            self._log(f"[ENC] Carrier selected: {os.path.basename(path)}")

            # Update carrier morph thumbnail mode based on extension
            ext = os.path.splitext(path)[1].lower()
            if ext in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
                self.carrier_mode.set("IMAGE")
            elif ext in (".wav", ".mp3", ".flac", ".ogg"):
                self.carrier_mode.set("AUDIO")
            else:
                self.carrier_mode.set("UNKNOWN")

            # Update thumbnail label
            mode = self.carrier_mode.get()
            text = f"CARRIER: {mode}"
            self.header_canvas.itemconfig(self.thumb_label, text=text)

    def _select_stego_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.stego_file.set(path)
            self._log(f"[DEC] Stego source selected: {os.path.basename(path)}")
            self.carrier_mode.set("STEGO")
            self.header_canvas.itemconfig(self.thumb_label, text="CARRIER: STEGO")

    def _run_encode_thread(self):
        threading.Thread(target=self._run_encode, daemon=True).start()

    def _run_decode_thread(self):
        threading.Thread(target=self._run_decode, daemon=True).start()

    def _run_encode(self):
        try:
            secret = self.secret_file.get()
            cover = self.cover_file.get()
            password = self.encode_password.get()

            if "[NO FILE" in secret or "[NO FILE" in cover or not password:
                self._update_status("ERROR: MISSING_INPUTS", ERROR_COLOR)
                self._log("[ENC] Missing inputs. Aborting.")
                return

            original_ext = os.path.splitext(cover)[1]
            output_file = filedialog.asksaveasfilename(defaultextension=original_ext)
            if not output_file:
                self._log("[ENC] Save operation cancelled.")
                return

            self._update_status(
                "PROCESSING... EMBEDDING_PAYLOAD", ACCENT_CYAN
            )
            self._log(
                f"[ENC] Embedding '{os.path.basename(secret)}' into carrier '{os.path.basename(cover)}'"
            )

            core_logic.hide_data(secret, cover, output_file, password)

            self._update_status(
                f"SUCCESS: DATA_EMBEDDED -> {os.path.basename(output_file)}",
                SUCCESS_COLOR,
            )
            self._log(
                f"[ENC] Payload embedded successfully: {os.path.basename(output_file)}"
            )
        except Exception as e:
            self._update_status(f"CRITICAL_FAILURE: {str(e)}", ERROR_COLOR)
            self._log(f"[ENC][ERROR] {e}")

    def _run_decode(self):
        try:
            stego = self.stego_file.get()
            password = self.decode_password.get()

            if "[NO FILE" in stego or not password:
                self._update_status("ERROR: MISSING_INPUTS", ERROR_COLOR)
                self._log("[DEC] Missing inputs. Aborting.")
                return

            self._update_status(
                "PROCESSING... EXTRACTING_PAYLOAD", ACCENT_CYAN
            )
            self._log(
                f"[DEC] Extracting payload from '{os.path.basename(stego)}'"
            )

            fname, data = core_logic.extract_data(stego, password)

            output_file = filedialog.asksaveasfilename(initialfile=fname)
            if not output_file:
                self._log("[DEC] Save operation cancelled.")
                return

            file_io.write_bytes(output_file, data)

            self._update_status(
                f"SUCCESS: PAYLOAD_EXTRACTED -> {fname}", SUCCESS_COLOR
            )
            self._log(
                f"[DEC] Payload extracted and saved as '{os.path.basename(output_file)}'"
            )
        except Exception as e:
            self._update_status(f"DECRYPTION_FAILED: {str(e)}", ERROR_COLOR)
            self._log(f"[DEC][ERROR] {e}")

    def _update_status(self, message, color):
        self.status_bar.config(text=message, fg=color)
        self._log(f"[STATUS] {message}")

    def _log(self, message: str):
        self.log_console.config(state="normal")
        self.log_console.insert("end", message + "\n")
        self.log_console.see("end")
        self.log_console.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = StegoApp(root)
    root.mainloop()
