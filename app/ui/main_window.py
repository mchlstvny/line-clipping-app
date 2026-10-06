import tkinter as tk


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root

        self.root.title("Line Clipping App")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        self._build_ui()

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)
        self.root.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self.root,
            background="white",
        )

        self.canvas.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(15, 0),
            pady=15,
        )

        self.control_panel = tk.Frame(
            self.root,
            width=250,
            background="#eeeeee",
        )

        self.control_panel.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=15,
            pady=15,
        )

        self.control_panel.grid_propagate(False)