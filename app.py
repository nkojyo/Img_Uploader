import tkinter as tk
from gui import UploadGUI
from logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Starting GUI...")
    root = tk.Tk()
    app = UploadGUI(root)
    root.mainloop()
    logger.info("GUI closed.")

if __name__ == "__main__":
    main()
