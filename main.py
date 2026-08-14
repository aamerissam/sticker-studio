import tkinter as tk
from app import StickerStudio


def main():
    root = tk.Tk()
    app = StickerStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
