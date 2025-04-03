import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from client.gui.gui_client import ATMClientGUI

def main():
    root = tk.Tk()
    app = ATMClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
