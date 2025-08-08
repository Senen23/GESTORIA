import tkinter as tk
from ui.login import LoginWindow
def main():
    root = tk.Tk()
    root.state("zoomed")
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    