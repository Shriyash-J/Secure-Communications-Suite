import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import threading
import os

# --- SCRUBBER THEME ---
BG_COLOR = "#1A1A1A"      # Dark Grey
ACCENT_COLOR = "#FFD700"  # Gold
TEXT_COLOR = "#FFFFFF"
FONT_MONO = ("Consolas", 10)
FONT_HEADER = ("Consolas", 14, "bold")

class MetaWiperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PRIVACY_TOOL // META_WIPER")
        self.root.geometry("800x600")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # --- Canvas ---
        self.canvas = tk.Canvas(root, width=800, height=600, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # --- State ---
        self.file_path = tk.StringVar()
        self.status_msg = tk.StringVar(value="WAITING FOR INPUT...")
        
        # --- UI Build ---
        self._build_ui()

    def _build_ui(self):
        # Header
        self.canvas.create_text(400, 50, text="METADATA SCRUBBER", fill=ACCENT_COLOR, font=FONT_HEADER)
        self.canvas.create_line(100, 70, 700, 70, fill=ACCENT_COLOR, width=2)

        # Input Zone
        self._create_label(100, 150, "TARGET_IMAGE:")
        self._create_entry(250, 150, self.file_path, 350)
        self._create_btn(620, 150, "[ SELECT ]", self.browse)

        # Info Display
        self.canvas.create_text(400, 250, text="This tool removes hidden EXIF data (GPS, Camera Info, Timestamps)\nfrom your images to protect your privacy.", 
                                fill=TEXT_COLOR, font=FONT_MONO, justify="center")

        # Action Button
        self._create_big_btn(300, 350, "SANITIZE FILE", ACCENT_COLOR, self.wipe_metadata)

        # Status
        self.status_text = self.canvas.create_text(400, 500, text=self.status_msg.get(), fill=TEXT_COLOR, font=FONT_MONO)

    def _create_label(self, x, y, text):
        self.canvas.create_text(x, y, text=text, fill=TEXT_COLOR, font=FONT_MONO, anchor="w")

    def _create_entry(self, x, y, var, w):
        e = tk.Entry(self.root, textvariable=var, bg="#333", fg=TEXT_COLOR, insertbackground=TEXT_COLOR, 
                     relief="flat", font=FONT_MONO)
        e.place(x=x, y=y-10, width=w, height=25)
        # Frame
        self.canvas.create_rectangle(x-2, y-12, x+w+2, y+15, outline=ACCENT_COLOR)

    def _create_btn(self, x, y, text, cmd):
        tk.Button(self.root, text=text, bg=BG_COLOR, fg=ACCENT_COLOR, activebackground=ACCENT_COLOR, activeforeground="black",
                  relief="flat", font=("Consolas", 9, "bold"), command=cmd).place(x=x, y=y-12, height=25)
        self.canvas.create_rectangle(x-2, y-12, x+80, y+13, outline=ACCENT_COLOR)

    def _create_big_btn(self, x, y, text, color, cmd):
        tk.Button(self.root, text=text, bg=BG_COLOR, fg=color, font=("Consolas", 12, "bold"),
                  activebackground=color, activeforeground="black", relief="solid", bd=1,
                  command=cmd).place(x=x, y=y, width=200, height=45)

    # --- Logic ---
    def browse(self):
        f = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.tiff")])
        if f: self.file_path.set(f)

    def wipe_metadata(self):
        if not self.file_path.get(): return
        self.canvas.itemconfig(self.status_text, text="PROCESSING...", fill=ACCENT_COLOR)
        threading.Thread(target=self.process).start()

    def process(self):
        try:
            path = self.file_path.get()
            img = Image.open(path)

            # We create a new image without copying the exif data
            data = list(img.getdata())
            image_without_exif = Image.new(img.mode, img.size)
            image_without_exif.putdata(data)

            dir_name, file_name = os.path.split(path)
            new_path = os.path.join(dir_name, "CLEAN_" + file_name)
            
            image_without_exif.save(new_path)

            self.canvas.itemconfig(self.status_text, text=f"SUCCESS! SAVED AS: CLEAN_{file_name}", fill=ACCENT_COLOR)
            messagebox.showinfo("Success", "Metadata removed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.canvas.itemconfig(self.status_text, text="ERROR OCCURRED", fill="red")