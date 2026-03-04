import tkinter as tk
from tkinter import filedialog, messagebox
import socket
import threading
import math
import random
import time

# --- TACTICAL HUD THEME ---
BG = "#050805"
RADAR_GREEN = "#00FF41"
ALERT_RED = "#FF3333"
DIM_GREEN = "#003300"
TEXT_COLOR = "#E0FFE0"
FONT_MONO = ("Consolas", 9)
FONT_HEADER = ("Consolas", 12, "bold")

# Common Port Dictionary for rapid identification
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "TELNET", 25: "SMTP", 53: "DNS", 
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 3306: "MYSQL",
    3389: "RDP", 8080: "HTTP-ALT"
}

class NetProbeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NET_PROBE // ACTIVE_RECON_UNIT")
        self.root.geometry("950x700")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # --- Canvas ---
        self.canvas = tk.Canvas(root, width=950, height=700, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # --- State ---
        self.target_ip = tk.StringVar(value="scanme.nmap.org")
        self.start_port = tk.IntVar(value=1)
        self.end_port = tk.IntVar(value=100)
        self.is_scanning = False
        self.angle = 0
        self.found_hosts = [] # List of found ports/services

        self._build_ui()
        self._animate()

    def _build_ui(self):
        # --- Background Grid ---
        self._draw_grid()

        # --- Left Panel (Controls) ---
        self._draw_panel(30, 30, 300, 640, "COMMAND_UPLINK")
        
        self._create_label(50, 80, "TARGET_ADDRESS:")
        self._create_entry(50, 100, self.target_ip, 260)

        self._create_label(50, 150, "PORT_RANGE [START]:")
        self._create_entry(50, 170, self.start_port, 100)
        
        self._create_label(190, 150, "[END]:")
        self._create_entry(190, 170, self.end_port, 100)

        # Scan Button
        self._create_big_btn(50, 240, "INITIATE SCAN", RADAR_GREEN, self.start_scan)
        self._create_big_btn(50, 300, "EXPORT REPORT", "#0088FF", self.export_log)

        # --- Right Panel (Visualizer) ---
        # Radar Circle Center
        self.cx, self.cy = 630, 250
        
        # --- Bottom Panel (Live Terminal) ---
        self._draw_panel(350, 430, 570, 240, "LIVE_PACKET_FEED")
        
        # Text widget for logs (placed on top of canvas)
        self.log_text = tk.Text(self.root, bg="#020502", fg=RADAR_GREEN, font=FONT_MONO, 
                                bd=0, highlightthickness=0)
        self.log_text.place(x=360, y=460, width=550, height=200)
        self._log(">> NET_PROBE MODULE INITIALIZED...")
        self._log(">> READY FOR ACTIVE RECONNAISSANCE.")

    def _draw_grid(self):
        # Draw a tactical grid background
        w, h = 950, 700
        for x in range(0, w, 50):
            self.canvas.create_line(x, 0, x, h, fill="#001100", width=1)
        for y in range(0, h, 50):
            self.canvas.create_line(0, y, w, y, fill="#001100", width=1)

    def _draw_panel(self, x, y, w, h, title):
        # Cyberpunk Frame
        self.canvas.create_rectangle(x, y, x+w, y+h, outline=DIM_GREEN, width=2)
        self.canvas.create_rectangle(x, y, x+w, y+25, fill=DIM_GREEN, outline="")
        self.canvas.create_text(x+10, y+12, text=title, fill=RADAR_GREEN, font=FONT_HEADER, anchor="w")
        # Corner accents
        self.canvas.create_line(x, y+h, x, y+h-20, fill=RADAR_GREEN, width=3)
        self.canvas.create_line(x, y+h, x+20, y+h, fill=RADAR_GREEN, width=3)
        self.canvas.create_line(x+w, y+h, x+w, y+h-20, fill=RADAR_GREEN, width=3)
        self.canvas.create_line(x+w, y+h, x+w-20, y+h, fill=RADAR_GREEN, width=3)

    def _create_label(self, x, y, text):
        self.canvas.create_text(x, y, text=text, fill="#88AA88", font=("Consolas", 9, "bold"), anchor="w")

    def _create_entry(self, x, y, var, w):
        e = tk.Entry(self.root, textvariable=var, bg="#000000", fg=RADAR_GREEN, 
                     insertbackground=RADAR_GREEN, relief="flat", font=FONT_MONO)
        e.place(x=x, y=y, width=w, height=25)
        # Glowing Underline
        self.canvas.create_line(x, y+25, x+w, y+25, fill=RADAR_GREEN, width=1)

    def _create_big_btn(self, x, y, text, color, cmd):
        tk.Button(self.root, text=text, bg="#001100", fg=color, font=("Consolas", 11, "bold"),
                  activebackground=color, activeforeground="black", relief="solid", bd=1,
                  command=cmd).place(x=x, y=y, width=260, height=40)

    def _animate(self):
        self.canvas.delete("radar")
        
        # 1. Radar Rings
        for i in range(1, 4):
            self.canvas.create_oval(self.cx - i*60, self.cy - i*60, 
                                    self.cx + i*60, self.cy + i*60, 
                                    outline=DIM_GREEN, width=1, tags="radar")
        
        # 2. Crosshairs
        self.canvas.create_line(self.cx-180, self.cy, self.cx+180, self.cy, fill=DIM_GREEN, tags="radar")
        self.canvas.create_line(self.cx, self.cy-180, self.cx, self.cy+180, fill=DIM_GREEN, tags="radar")

        # 3. Sweep Line
        if self.is_scanning:
            rad = math.radians(self.angle)
            ex = self.cx + 180 * math.cos(rad)
            ey = self.cy + 180 * math.sin(rad)
            self.canvas.create_line(self.cx, self.cy, ex, ey, fill=RADAR_GREEN, width=2, tags="radar")
            
            # Draw trailing shadow
            for i in range(1, 15):
                trail_rad = math.radians(self.angle - i*2)
                tx = self.cx + 180 * math.cos(trail_rad)
                ty = self.cy + 180 * math.sin(trail_rad)
                color = "#004400" if i > 5 else "#008800"
                self.canvas.create_line(self.cx, self.cy, tx, ty, fill=color, width=1, tags="radar")

            self.angle = (self.angle + 4) % 360

        # 4. Found Targets (Blips)
        for host in self.found_hosts:
            # Randomly position blips within the radar for visual effect
            # In a real geospatial app, this would be coordinates
            bx = self.cx + math.cos(host['angle']) * host['dist']
            by = self.cy + math.sin(host['angle']) * host['dist']
            
            # Blinking effect
            color = ALERT_RED if int(time.time() * 5) % 2 == 0 else "#550000"
            self.canvas.create_oval(bx-3, by-3, bx+3, by+3, fill=color, outline="", tags="radar")
            self.canvas.create_text(bx+10, by, text=f"PORT {host['port']}", fill=TEXT_COLOR, font=("Consolas", 8), anchor="w", tags="radar")

        self.root.after(40, self._animate)

    # --- Logic ---
    def start_scan(self):
        if self.is_scanning: return
        self.is_scanning = True
        self.found_hosts = []
        self.log_text.delete(1.0, "end")
        self._log(f"TARGET ACQUIRED: {self.target_ip.get()}")
        self._log("SCANNING SEQUENCE INITIATED...")
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        target = self.target_ip.get()
        start = self.start_port.get()
        end = self.end_port.get()
        
        try:
            target_ip = socket.gethostbyname(target)
            self._log(f"RESOLVED IP: {target_ip}")
        except:
            self._log("ERROR: COULD NOT RESOLVE HOST", ALERT_RED)
            self.is_scanning = False
            return

        for port in range(start, end + 1):
            if not self.is_scanning: break
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5) # Fast timeout
                result = s.connect_ex((target_ip, port))
                
                if result == 0:
                    # Port is open! Let's try to grab a banner
                    service_name = COMMON_PORTS.get(port, "UNKNOWN")
                    banner = "NO_BANNER"
                    
                    # Banner Grabbing Attempt
                    try:
                        s.send(b'HEAD / HTTP/1.0\r\n\r\n')
                        banner_bytes = s.recv(1024)
                        banner = banner_bytes.decode().strip().split('\n')[0][:20] # First 20 chars
                    except:
                        pass

                    self._log(f"[!] OPEN PORT: {port} | SERVICE: {service_name}", RADAR_GREEN)
                    if banner != "NO_BANNER":
                         self._log(f"    BANNER: {banner}", "#88FF88")
                    
                    # Add to visual radar
                    self.found_hosts.append({
                        'port': port,
                        'angle': random.uniform(0, 6.28),
                        'dist': random.randint(50, 150)
                    })
                s.close()
            except:
                pass

        self.is_scanning = False
        self._log(">>> SCAN SEQUENCE COMPLETE.")

    def _log(self, msg, color=TEXT_COLOR):
        # Insert text with color tag
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        
    def export_log(self):
        out = filedialog.asksaveasfilename(defaultextension=".txt")
        if out:
            with open(out, "w") as f:
                f.write(self.log_text.get(1.0, "end"))
            messagebox.showinfo("SYS", "LOG EXPORTED SUCCESSFULLY")