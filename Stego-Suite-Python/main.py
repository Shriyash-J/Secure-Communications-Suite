import tkinter as tk
from gui import StegoApp
import logging

if __name__ == "__main__":
    # Setup basic logging to see errors in the console
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    root = tk.Tk()
    app = StegoApp(root)
    root.mainloop()