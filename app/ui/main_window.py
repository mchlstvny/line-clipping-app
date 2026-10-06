import tkinter as tk
from app.core.geometry import Line, Point, Rectangle
from app.services.clipping_service import clip_line


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root

        self.root.title("Line Clipping App")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        self.start_x = None
        self.start_y = None
        self.preview_line = None
        self.lines = []
        self.clipped_lines = []
        self.selected_algorithm = tk.StringVar(
            value="cohen-sutherland"
        )

        self.clipping_window_item = None
        self.clipped_canvas_items = []

        self.is_drawing_window = False
        self.window_start_x = None
        self.window_start_y = None
        self.clipping_window = None
        self.window_preview = None

        self._build_ui()
        self._bind_events()

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

        algorithm_label = tk.Label(
            self.control_panel,
            text="Clipping Algorithm",
            background="#f80b0b",
        )

        algorithm_label.pack(
            padx=15,
            pady=(15, 5),
            anchor="w",
        )

        algorithm_menu = tk.OptionMenu(
            self.control_panel,
            self.selected_algorithm,
            "cohen-sutherland",
            "liang-barsky",
        )

        algorithm_menu.pack(
            padx=15,
            pady=(0, 15),
            fill="x",
        )

        self.draw_window_button = tk.Button(
            self.control_panel,
            text="Draw Clipping Window",
            command=self._start_drawing_window,
        )

        self.draw_window_button.pack(
            padx=15,
            pady=15,
            fill="x",
        )

        self.clip_button = tk.Button(
            self.control_panel,
            text="Clip Line",
            command=self._clip_lines,
        )

        self.clip_button.pack(
            padx=15,
            pady=(0, 15),
            fill="x",
        )

    def _bind_events(self):
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)

    def _on_mouse_down(self, event):
        if self.is_drawing_window:
            self.window_start_x = event.x
            self.window_start_y = event.y

            self.window_preview = self.canvas.create_rectangle(
                event.x,
                event.y,
                event.x,
                event.y,
                outline="blue",
                width=2,
            )

            return

        self.start_x = event.x
        self.start_y = event.y

        self.preview_line = self.canvas.create_line(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            fill="black",
            width=2,
        )

    def _on_mouse_drag(self, event):
        if self.is_drawing_window:
            if self.window_preview is None:
                return

            self.canvas.coords(
                self.window_preview,
                self.window_start_x,
                self.window_start_y,
                event.x,
                event.y,
            )

            return

        if self.preview_line is None:
            return

        self.canvas.coords(
            self.preview_line,
            self.start_x,
            self.start_y,
            event.x,
            event.y,
        )

    def _on_mouse_up(self, event):
        if self.is_drawing_window:
            if self.window_preview is None:
                return

            xmin = min(self.window_start_x, event.x)
            xmax = max(self.window_start_x, event.x)
            ymin = min(self.window_start_y, event.y)
            ymax = max(self.window_start_y, event.y)

            self.clipping_window = Rectangle(
                xmin=xmin,
                ymin=ymin,
                xmax=xmax,
                ymax=ymax,
            )

            self.window_preview = None
            self.is_drawing_window = False

            print("Created clipping window:", self.clipping_window)

            return

        if self.preview_line is None:
            return

        line = Line(
            start=Point(self.start_x, self.start_y),
            end=Point(event.x, event.y),
        )

        self.lines.append(line)

        self.preview_line = None

        print("Created line:", line)

    def _start_drawing_window(self):
        self.is_drawing_window = True

    def _clip_lines(self):
        if self.clipping_window is None:
            print("No clipping window defined.")
            return

        if not self.lines:
            print("No lines to clip.")
            return

        for item in self.clipped_canvas_items:
            self.canvas.delete(item)

        self.clipped_canvas_items.clear()

        algorithm = self.selected_algorithm.get()

        print("Algorithm:", algorithm)

        self.clipped_lines.clear()

        for line in self.lines:
            clipped = clip_line(
                line,
                self.clipping_window,
                algorithm,
            )

            print("Original:", line)
            print("Clipped:", clipped)
            print()

            if clipped is None:
                continue

            self.clipped_lines.append(clipped)

            item = self.canvas.create_line(
                clipped.start.x,
                clipped.start.y,
                clipped.end.x,
                clipped.end.y,
                fill="red",
                width=3,
            )

            self.clipped_canvas_items.append(item)