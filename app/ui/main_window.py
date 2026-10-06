import tkinter as tk
import math
from app.core.geometry import Line, Point, Rectangle
from app.services.clipping_service import clip_line


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root

        self.root.title("Line Clipping App")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        self.create_mode = tk.StringVar(value="line")
        self.selected_algorithm = tk.StringVar(value="cohen-sutherland")
        self.line_color = tk.StringVar(value="Black")
        self.line_width = tk.IntVar(value=2)

        self.start_x = None
        self.start_y = None
        self.preview_line = None
        self.lines = []
        self.clipped_lines = []
        self.shapes = []

        self.clipping_window_item = None
        self.clipped_canvas_items = []
        self.clipped_shape_canvas_items = []

        self.is_drawing_window = False
        self.window_start_x = None
        self.window_start_y = None
        self.clipping_window = None
        self.window_preview = None
        self.shape_start_x = None
        self.shape_start_y = None
        self.shape_preview = None
        self.shape_mode = None

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        for column in range(3):
            self.root.columnconfigure(column, weight=1, uniform="layout")
        self.root.rowconfigure(1, weight=1)

        create_frame = tk.LabelFrame(self.root, text="Create", padx=8, pady=5)
        create_frame.grid(row=0, column=0, sticky="nsew", padx=(12, 5), pady=10)

        for row, (label, value) in enumerate(
            (("Line", "line"), ("Clipping Area", "clipping-area"),
             ("Rectangle", "rectangle"), ("Circle", "circle"))
        ):
            tk.Radiobutton(
                create_frame,
                text=label,
                value=value,
                variable=self.create_mode,
                command=self._on_create_mode_changed,
            ).grid(row=row, column=0, sticky="w")

        algorithm_frame = tk.LabelFrame(self.root, text="Algorithm", padx=8, pady=5)
        algorithm_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)

        for row, (label, value) in enumerate(
            (("Cohen-Sutherland", "cohen-sutherland"),
             ("Liang-Barsky", "liang-barsky"))
        ):
            tk.Radiobutton(
                algorithm_frame,
                text=label,
                value=value,
                variable=self.selected_algorithm,
            ).grid(row=row, column=0, sticky="w")

        style_frame = tk.LabelFrame(
            self.root,
            text="Color & Thickness",
            padx=8,
            pady=5,
        )
        style_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 12), pady=10)
        style_frame.columnconfigure(1, weight=1)

        tk.Label(style_frame, text="Color").grid(row=0, column=0, sticky="w", padx=(0, 8))
        tk.OptionMenu(
            style_frame,
            self.line_color,
            "Black",
            "Red",
            "Blue",
            "Green",
        ).grid(row=0, column=1, sticky="ew")

        tk.Label(style_frame, text="Thickness").grid(
            row=1, column=0, sticky="w", padx=(0, 8)
        )
        tk.OptionMenu(
            style_frame,
            self.line_width,
            1,
            2,
            3,
            4,
            5,
        ).grid(row=1, column=1, sticky="ew")

        self.canvas = tk.Canvas(self.root, background="white", highlightthickness=1)
        self.canvas.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=(12, 5),
            pady=(0, 12),
        )

        lists_frame = tk.Frame(self.root)
        lists_frame.grid(
            row=1,
            column=2,
            sticky="nsew",
            padx=(5, 12),
            pady=(0, 12),
        )
        lists_frame.columnconfigure(0, weight=1)
        lists_frame.rowconfigure(0, weight=1)
        lists_frame.rowconfigure(1, weight=1)

        before_frame = tk.LabelFrame(lists_frame, text="Lines Before Clipping", padx=5, pady=5)
        before_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        before_frame.rowconfigure(0, weight=1)
        before_frame.columnconfigure(0, weight=1)
        self.lines_before_list = tk.Listbox(before_frame, height=6, exportselection=False)
        self.lines_before_list.grid(row=0, column=0, sticky="nsew")

        after_frame = tk.LabelFrame(lists_frame, text="Lines After Clipping", padx=5, pady=5)
        after_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        after_frame.rowconfigure(0, weight=1)
        after_frame.columnconfigure(0, weight=1)
        self.lines_after_list = tk.Listbox(after_frame, height=6, exportselection=False)
        self.lines_after_list.grid(row=0, column=0, sticky="nsew")

        actions = tk.Frame(lists_frame)
        actions.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.clip_button = tk.Button(actions, text="Clip", command=self._clip_lines)
        self.clip_button.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.clear_button = tk.Button(actions, text="Clear", command=self._clear_canvas)
        self.clear_button.pack(side="left", fill="x", expand=True, padx=(4, 0))

    def _bind_events(self):
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)

    def _on_create_mode_changed(self):
        self.is_drawing_window = self.create_mode.get() == "clipping-area"
        if not self.is_drawing_window and self.window_preview is not None:
            self.canvas.delete(self.window_preview)
            self.window_preview = None
        if self.shape_preview is not None:
            self.canvas.delete(self.shape_preview)
            self.shape_preview = None
        if self.preview_line is not None:
            self.canvas.delete(self.preview_line)
            self.preview_line = None

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

        mode = self.create_mode.get()
        if mode in ("rectangle", "circle"):
            self.shape_mode = mode
            self.shape_start_x = event.x
            self.shape_start_y = event.y
            create_shape = (
                self.canvas.create_rectangle
                if mode == "rectangle"
                else self.canvas.create_oval
            )
            self.shape_preview = create_shape(
                event.x,
                event.y,
                event.x,
                event.y,
                outline=self.line_color.get().lower(),
                width=self.line_width.get(),
            )
            return

        if mode != "line":
            return

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

        if self.shape_preview is not None:
            self.canvas.coords(
                self.shape_preview,
                self.shape_start_x,
                self.shape_start_y,
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

            for item in self.clipped_canvas_items:
                self.canvas.delete(item)
            for item in self.clipped_shape_canvas_items:
                self.canvas.delete(item)
            self.clipped_canvas_items.clear()
            self.clipped_shape_canvas_items.clear()
            self.clipped_lines.clear()
            self.lines_after_list.delete(0, tk.END)

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

            print("Created clipping window:", self.clipping_window)

            return

        if self.shape_preview is not None:
            self.canvas.coords(
                self.shape_preview,
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
                shape["kind"] == self.shape_mode for shape in self.shapes
            )
            self.shapes.append(
                {
                    "kind": self.shape_mode,
                    "number": shape_number,
                    "bounds": bounds,
                    "color": self.line_color.get().lower(),
                    "width": self.line_width.get(),
                }
            )
            self.lines_before_list.insert(
                tk.END,
                self._format_shape_before(self.shapes[-1]),
            )
            self.shape_preview = None
            self.shape_mode = None
            return

        if self.preview_line is None:
            return

        line = Line(
            start=Point(self.start_x, self.start_y),
            end=Point(event.x, event.y),
        )

        self.lines.append(line)
        self.lines_before_list.insert(
            tk.END,
            f"Line {len(self.lines)}: {self._format_line(line)}",
        )

        self.preview_line = None

        print("Created line:", line)

    @staticmethod
    def _format_line(line: Line) -> str:
        return (
            f"({line.start.x:g}, {line.start.y:g}) -> "
            f"({line.end.x:g}, {line.end.y:g})"
        )

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
        for item in self.clipped_canvas_items:
            self.canvas.delete(item)
        for item in self.clipped_shape_canvas_items:
            self.canvas.delete(item)

        self.clipped_canvas_items.clear()
        self.clipped_shape_canvas_items.clear()
        self.clipped_lines.clear()
        self.lines_after_list.delete(0, tk.END)

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
                self.lines_after_list.insert(
                    tk.END,
                    f"Line {line_number}: Rejected / Outside",
                )
                continue

            self.clipped_lines.append(clipped)
            self.lines_after_list.insert(
                tk.END,
                f"Line {line_number}: {self._format_line(clipped)}",
            )

            clipped_color = "red"

            if self.line_color.get().lower() == "red":
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
            clipped_color = "blue" if shape["color"] == "red" else "red"
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

                self.lines_after_list.insert(
                    tk.END,
                    f"Rectangle {shape['number']}: {summary}",
                )
                for edge_name, original, clipped in edge_results:
                    if clipped is None:
                        edge_result = "Rejected / Outside"
                    else:
                        state = (
                            "visible segment"
                            if self._same_line(original, clipped)
                            else "clipped segment"
                        )
                        edge_result = f"{state} {self._format_line(clipped)}"
                    self.lines_after_list.insert(
                        tk.END,
                        f"  {edge_name}: {edge_result}",
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
            self.lines_after_list.insert(
                tk.END,
                f"Circle {shape['number']}: {summary}",
            )

    def _clear_canvas(self):
        self.canvas.delete("all")

        self.lines.clear()
        self.clipped_lines.clear()
        self.shapes.clear()
        self.clipped_canvas_items.clear()
        self.clipped_shape_canvas_items.clear()
        self.lines_before_list.delete(0, tk.END)
        self.lines_after_list.delete(0, tk.END)

        self.clipping_window = None
        self.clipping_window_item = None

        self.preview_line = None
        self.window_preview = None
        self.shape_preview = None
        self.shape_mode = None

        self.create_mode.set("line")
        self.is_drawing_window = False

        self.start_x = None
        self.start_y = None
        self.window_start_x = None
        self.window_start_y = None
        self.shape_start_x = None
        self.shape_start_y = None