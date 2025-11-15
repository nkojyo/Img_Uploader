import tkinter as tk
from gui import UploadGUI

def main():
    print("Starting GUI...")  # コンソール確認用
    root = tk.Tk()
    app = UploadGUI(root)
    root.mainloop()
    print("GUI closed.")       # GUI終了確認

if __name__ == "__main__":
    main()
