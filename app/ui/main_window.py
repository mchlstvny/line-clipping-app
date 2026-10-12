import tkinter as tk
from tkinter import ttk
import math
from tkinter import colorchooser
from app.core.geometry import Line, Point, Rectangle
from app.services.clipping_service import clip_line
from app.ui.panels import Panels
from app.ui.toolbar import Toolbar


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root

        self.root.title("Line Clipping App")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)
        self._configure_theme()

        self.create_modes = {
            "line": tk.BooleanVar(value=True),
            "clipping-area": tk.BooleanVar(value=False),
            "rectangle": tk.BooleanVar(value=False),
            "circle": tk.BooleanVar(value=False),
        }
        self.selected_algorithm = tk.StringVar(value="cohen-sutherland")
        self.line_color = tk.StringVar(value="Black")
        self.line_width = tk.IntVar(value=2)

        self.start_x = None
        self.start_y = None
        self.preview_line = None
        self.lines = []
        self.original_line_items = []
        self.clipped_lines = []
        self.shapes = []

        self.clipping_window_item = None
        self.clipped_canvas_items = []
        self.clipped_shape_canvas_items = []

        self.gesture_modes = set()
        self.window_start_x = None
        self.window_start_y = None
        self.clipping_window = None
        self.window_preview = None
        self.shape_start_x = None
        self.shape_start_y = None
        self.shape_previews = {}

        self._build_ui()
        self._bind_events()

    def _configure_theme(self):
        self.root.configure(background="#f3f5f7")
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", font=("TkDefaultFont", 10), foreground="#202a36")
        style.configure("TFrame", background="#f3f5f7")
        style.configure("TLabel", background="#f3f5f7", foreground="#202a36")
        style.configure(
            "TLabelframe",
            background="#f3f5f7",
            bordercolor="#cbd3dd",
            relief="solid",
        )
        style.configure(
            "TLabelframe.Label",
            background="#f3f5f7",
            foreground="#24364b",
            font=("TkDefaultFont", 10, "bold"),
        )
        style.configure("TCheckbutton", background="#f3f5f7", padding=(2, 3))
        style.configure("TRadiobutton", background="#f3f5f7", padding=(2, 3))
        style.configure("TButton", padding=(9, 5))
        style.configure(
            "Primary.TButton",
            background="#2864c7",
            foreground="#ffffff",
            padding=(10, 6),
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#1e52a7"), ("disabled", "#aab8ca")],
            foreground=[("disabled", "#f3f5f7")],
        )
        style.configure("TCombobox", fieldbackground="#ffffff", padding=4)

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.canvas = tk.Canvas(
            self.root,
            background="white",
            highlightthickness=1,
            highlightbackground="#cbd3dd",
            highlightcolor="#2864c7",
            borderwidth=0,
        )
        self.canvas.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=(12, 5),
            pady=(0, 12),
        )

        self.lists_frame = ttk.Frame(self.root)
        self.lists_frame.grid(
            row=1,
            column=2,
            sticky="nsew",
            padx=(5, 12),
            pady=(0, 12),
        )
        self.lists_frame.columnconfigure(0, weight=1)
        self.lists_frame.rowconfigure(0, weight=1)
        self.lists_frame.rowconfigure(1, weight=0)

        self.panels = Panels(self.lists_frame)
        self.panels.grid(row=0, column=0, sticky="nsew")
        actions = ttk.Frame(self.lists_frame)
        actions.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        self.toolbar = Toolbar(
            self.root,
            self.create_modes,
            self.selected_algorithm,
            self.line_color,
            self.line_width,
            self._choose_line_color,
            self._on_create_mode_changed,
            self._clip_lines,
            self._clear_canvas,
            actions,
        )
        self.toolbar.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.clip_button = self.toolbar.clip_button
        self.clear_button = self.toolbar.clear_button

    def _bind_events(self):
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)

    def _choose_line_color(self):
        initial_color = self.line_color.get()
        if self._is_black_color(initial_color):
            initial_color = "#007aff"
        _, selected_color = colorchooser.askcolor(
            color=initial_color,
            parent=self.root,
            title="Choose Color",
        )
        if selected_color:
            self.line_color.set(selected_color)

    def _is_black_color(self, color: str) -> bool:
        try:
            return self.root.winfo_rgb(color) == (0, 0, 0)
        except tk.TclError:
            return color.lower() in ("black", "#000", "#000000")

    def _is_red_color(self, color: str) -> bool:
        try:
            return self.root.winfo_rgb(color) == (65535, 0, 0)
        except tk.TclError:
            return color.lower() == "red"

    def _on_create_mode_changed(self):
        if self.window_preview is not None:
            self.canvas.delete(self.window_preview)
            self.window_preview = None
        for preview in self.shape_previews.values():
            self.canvas.delete(preview)
        self.shape_previews.clear()
        if self.preview_line is not None:
            self.canvas.delete(self.preview_line)
            self.preview_line = None
        self.gesture_modes.clear()

    def _on_mouse_down(self, event):
        self.gesture_modes = {
            mode for mode, variable in self.create_modes.items() if variable.get()
        }
        if not self.gesture_modes:
            return

        if "clipping-area" in self.gesture_modes:
            self.gesture_modes = {"clipping-area"}
            self.window_start_x = event.x
            self.window_start_y = event.y

            self.window_preview = self.canvas.create_rectangle(
                event.x,
                event.y,
                event.x,
                event.y,
                outline="blue",
                width=2,
                dash=(5, 4),
            )

        if "line" in self.gesture_modes:
            self.start_x = event.x
            self.start_y = event.y
            self.preview_line = self.canvas.create_line(
                self.start_x,
                self.start_y,
                self.start_x,
                self.start_y,
                fill=self.line_color.get(),
                width=self.line_width.get(),
            )

        for mode in ("rectangle", "circle"):
            if mode not in self.gesture_modes:
                continue
            self.shape_start_x = event.x
            self.shape_start_y = event.y
            create_shape = (
                self.canvas.create_rectangle
                if mode == "rectangle"
                else self.canvas.create_oval
            )
            self.shape_previews[mode] = create_shape(
                event.x,
                event.y,
                event.x,
                event.y,
                outline=self.line_color.get().lower(),
                width=self.line_width.get(),
            )

    def _on_mouse_drag(self, event):
        if "clipping-area" in self.gesture_modes and self.window_preview is not None:
            self.canvas.coords(
                self.window_preview,
                self.window_start_x,
                self.window_start_y,
                event.x,
                event.y,
            )

        for preview in self.shape_previews.values():
            self.canvas.coords(
                preview,
                self.shape_start_x,
                self.shape_start_y,
                event.x,
                event.y,
            )

        if self.preview_line is not None:
            self.canvas.coords(
                self.preview_line,
                self.start_x,
                self.start_y,
                event.x,
                event.y,
            )

    def _on_mouse_up(self, event):
        if "clipping-area" in self.gesture_modes and self.window_preview is not None:
            self.canvas.coords(
                self.window_preview,
                self.window_start_x,
                self.window_start_y,
                event.x,
                event.y,
            )
            xmin = min(self.window_start_x, event.x)
            xmax = max(self.window_start_x, event.x)
            ymin = min(self.window_start_y, event.y)
            ymax = max(self.window_start_y, event.y)

            self._clear_clipped_results()

            if self.clipping_window_item is not None:
                self.canvas.delete(self.clipping_window_item)

            self.clipping_window = Rectangle(
                xmin=xmin,
                ymin=ymin,
                xmax=xmax,
                ymax=ymax,
            )

            self.clipping_window_item = self.window_preview
            self.window_preview = None
            self.create_modes["clipping-area"].set(False)

            print("Created clipping window:", self.clipping_window)
            self.gesture_modes.clear()
            return

        if self.preview_line is not None:
            self.canvas.coords(
                self.preview_line,
                self.start_x,
                self.start_y,
                event.x,
                event.y,
            )

            line = Line(
                start=Point(self.start_x, self.start_y),
                end=Point(event.x, event.y),
            )
            self.lines.append(line)
            self.original_line_items.append(
                (self.preview_line, self.line_color.get())
            )
            self._add_line_coordinates(
                self.panels.add_before_item,
                f"Line {len(self.lines)}",
                line,
            )
            self.preview_line = None
            print("Created line:", line)

        for mode, preview in self.shape_previews.items():
            self.canvas.coords(
                preview,
                self.shape_start_x,
                self.shape_start_y,
                event.x,
                event.y,
            )
            bounds = (
                min(self.shape_start_x, event.x),
                min(self.shape_start_y, event.y),
                max(self.shape_start_x, event.x),
                max(self.shape_start_y, event.y),
            )
            shape_number = 1 + sum(
                shape["kind"] == mode for shape in self.shapes
            )
            self.shapes.append(
                {
                    "kind": mode,
                    "number": shape_number,
                    "bounds": bounds,
                    "color": self.line_color.get().lower(),
                    "width": self.line_width.get(),
                    "canvas_item": preview,
                }
            )
            self.panels.add_before_item(self._format_shape_before(self.shapes[-1]))
        self.shape_previews.clear()
        self.gesture_modes.clear()

    @staticmethod
    def _format_coordinate(value: float) -> str:
        return f"{value:.3f}".rstrip("0").rstrip(".")

    @classmethod
    def _format_point(cls, point: Point) -> str:
        return (
            f"({cls._format_coordinate(point.x)}, "
            f"{cls._format_coordinate(point.y)})"
        )

    @classmethod
    def _add_line_coordinates(cls, add_item, heading: str, line: Line) -> None:
        add_item(f"{heading}:")
        add_item(f"  Point A: {cls._format_point(line.start)}")
        add_item(f"  Point B: {cls._format_point(line.end)}")

    @staticmethod
    def _format_shape_before(shape) -> str:
        xmin, ymin, xmax, ymax = shape["bounds"]
        number = shape["number"]
        if shape["kind"] == "rectangle":
            return f"Rectangle {number}: ({xmin:g}, {ymin:g}) -> ({xmax:g}, {ymax:g})"

        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        radius_x = (xmax - xmin) / 2
        radius_y = (ymax - ymin) / 2
        if math.isclose(radius_x, radius_y):
            return f"Circle {number}: Center ({center_x:g}, {center_y:g}), Radius {radius_x:g}"
        return (
            f"Circle {number}: Center ({center_x:g}, {center_y:g}), "
            f"Radii ({radius_x:g}, {radius_y:g})"
        )

    @staticmethod
    def _same_line(first: Line, second: Line) -> bool:
        return all(
            math.isclose(first_value, second_value, rel_tol=0, abs_tol=1e-7)
            for first_value, second_value in (
                (first.start.x, second.start.x),
                (first.start.y, second.start.y),
                (first.end.x, second.end.x),
                (first.end.y, second.end.y),
            )
        )

    @staticmethod
    def _rectangle_edges(shape):
        xmin, ymin, xmax, ymax = shape["bounds"]
        corners = (
            Point(xmin, ymin),
            Point(xmax, ymin),
            Point(xmax, ymax),
            Point(xmin, ymax),
        )
        labels = ("Top", "Right", "Bottom", "Left")
        return [
            (
                labels[index],
                Line(start=corners[index], end=corners[(index + 1) % len(corners)]),
            )
            for index in range(len(corners))
        ]

    @staticmethod
    def _shape_segments(shape):
        if shape["kind"] == "rectangle":
            return [segment for _, segment in MainWindow._rectangle_edges(shape)]

        xmin, ymin, xmax, ymax = shape["bounds"]
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        radius_x = (xmax - xmin) / 2
        radius_y = (ymax - ymin) / 2
        point_count = 360
        points = [
            Point(
                center_x + radius_x * math.cos(2 * math.pi * index / point_count),
                center_y + radius_y * math.sin(2 * math.pi * index / point_count),
            )
            for index in range(point_count)
        ]
        return [
            Line(start=points[index], end=points[(index + 1) % point_count])
            for index in range(point_count)
        ]

    def _clear_clipped_results(self):
        self._restore_original_colors()
        for item in self.clipped_canvas_items:
            self.canvas.delete(item)
        for item in self.clipped_shape_canvas_items:
            self.canvas.delete(item)

        self.clipped_canvas_items.clear()
        self.clipped_shape_canvas_items.clear()
        self.clipped_lines.clear()
        self.panels.clear_after()

    def _restore_original_colors(self):
        for item, color in self.original_line_items:
            self.canvas.itemconfigure(item, fill=color)
        for shape in self.shapes:
            self.canvas.itemconfigure(shape["canvas_item"], outline=shape["color"])

    def _fade_color(self, color: str) -> str:
        channels = self.root.winfo_rgb(color)
        faded = [
            round((channel / 257) * 0.3 + 255 * 0.7)
            for channel in channels
        ]
        return "#" + "".join(f"{channel:02x}" for channel in faded)

    def _fade_original_drawings(self):
        for item, color in self.original_line_items:
            self.canvas.itemconfigure(item, fill=self._fade_color(color))
        for shape in self.shapes:
            self.canvas.itemconfigure(
                shape["canvas_item"],
                outline=self._fade_color(shape["color"]),
            )

    def _clip_lines(self):
        self._clear_clipped_results()

        if self.clipping_window is None:
            print("No clipping window defined.")
            return

        if not self.lines and not self.shapes:
            print("No lines or shapes to clip.")
            return

        algorithm = self.selected_algorithm.get()

        print("Algorithm:", algorithm)

        for line_number, line in enumerate(self.lines, start=1):
            clipped = clip_line(
                line,
                self.clipping_window,
                algorithm,
            )

            print("Original:", line)
            print("Clipped:", clipped)
            print()

            if clipped is None:
                self.panels.add_after_item(f"Line {line_number}: Rejected / Outside")
                continue

            self.clipped_lines.append(clipped)
            self._add_line_coordinates(
                self.panels.add_after_item,
                f"Line {line_number}",
                clipped,
            )

            clipped_color = "red"

            if self._is_red_color(self.line_color.get()):
                clipped_color = "blue"

            item = self.canvas.create_line(
                clipped.start.x,
                clipped.start.y,
                clipped.end.x,
                clipped.end.y,
                fill=clipped_color,
                width=self.line_width.get(),
            )

            self.clipped_canvas_items.append(item)

        for shape in self.shapes:
            clipped_color = "blue" if self._is_red_color(shape["color"]) else "red"
            if shape["kind"] == "rectangle":
                edge_results = []
                for edge_name, segment in self._rectangle_edges(shape):
                    clipped = clip_line(
                        segment,
                        self.clipping_window,
                        algorithm,
                    )
                    edge_results.append((edge_name, segment, clipped))
                    if clipped is None:
                        continue

                    item = self.canvas.create_line(
                        clipped.start.x,
                        clipped.start.y,
                        clipped.end.x,
                        clipped.end.y,
                        fill=clipped_color,
                        width=shape["width"],
                    )
                    self.clipped_shape_canvas_items.append(item)

                accepted_edges = [result for result in edge_results if result[2] is not None]
                if not accepted_edges:
                    summary = "Rejected / Outside"
                elif len(accepted_edges) == len(edge_results) and all(
                    self._same_line(original, clipped)
                    for _, original, clipped in edge_results
                ):
                    summary = "Unchanged / Fully Inside"
                else:
                    summary = "Partially clipped"

                self.panels.add_after_item(f"Rectangle {shape['number']}: {summary}")
                for edge_name, original, clipped in edge_results:
                    if clipped is None:
                        self.panels.add_after_item(
                            f"  {edge_name}: Rejected / Outside"
                        )
                        continue

                    state = (
                        "visible segment"
                        if self._same_line(original, clipped)
                        else "clipped segment"
                    )
                    self._add_line_coordinates(
                        self.panels.add_after_item,
                        f"  {edge_name}: {state}",
                        clipped,
                    )
                continue

            circle_segments = self._shape_segments(shape)
            visible_segments = 0
            unchanged_segments = 0
            for segment in circle_segments:
                clipped = clip_line(
                    segment,
                    self.clipping_window,
                    algorithm,
                )
                if clipped is None:
                    continue

                visible_segments += 1
                if self._same_line(segment, clipped):
                    unchanged_segments += 1

                item = self.canvas.create_line(
                    clipped.start.x,
                    clipped.start.y,
                    clipped.end.x,
                    clipped.end.y,
                    fill=clipped_color,
                    width=shape["width"],
                )
                self.clipped_shape_canvas_items.append(item)

            if visible_segments == 0:
                summary = "Rejected / Outside"
            elif unchanged_segments == len(circle_segments):
                summary = f"Unchanged / Fully Inside ({visible_segments} visible segments)"
            else:
                summary = f"Partially clipped ({visible_segments} visible segments)"
            self.panels.add_after_item(f"Circle {shape['number']}: {summary}")

        self._fade_original_drawings()

    def _clear_canvas(self):
        self.canvas.delete("all")

        self.lines.clear()
        self.original_line_items.clear()
        self.clipped_lines.clear()
        self.shapes.clear()
        self.clipped_canvas_items.clear()
        self.clipped_shape_canvas_items.clear()
        self.panels.clear_before()
        self.panels.clear_after()

        self.clipping_window = None
        self.clipping_window_item = None

        self.preview_line = None
        self.window_preview = None
        self.shape_previews.clear()

        for mode, variable in self.create_modes.items():
            variable.set(mode == "line")
        self.gesture_modes.clear()

        self.start_x = None
        self.start_y = None
        self.window_start_x = None
        self.window_start_y = None
        self.shape_start_x = None
        self.shape_start_y = None