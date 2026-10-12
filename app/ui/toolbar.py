import tkinter as tk
from tkinter import ttk


class Toolbar:
	def __init__(
		self,
		parent,
		create_modes,
		selected_algorithm,
		line_color,
		line_width,
		on_choose_color,
		on_create_mode_changed,
		on_clip,
		on_clear,
		actions_parent,
	):
		self.frame = ttk.Frame(parent)
		self.frame.columnconfigure(0, weight=1, uniform="layout")
		self.frame.columnconfigure(1, weight=1, uniform="layout")
		self.frame.columnconfigure(2, weight=1, uniform="layout")

		create_frame = ttk.LabelFrame(self.frame, text="Create", padding=(10, 7))
		create_frame.grid(row=0, column=0, sticky="nsew", padx=(12, 5), pady=10)

		for row, (label, value) in enumerate(
			(("Line", "line"), ("Clipping Area", "clipping-area"),
			 ("Rectangle", "rectangle"), ("Circle", "circle"))
		):
			ttk.Checkbutton(
				create_frame,
				text=label,
				variable=create_modes[value],
				command=on_create_mode_changed,
			).grid(row=row, column=0, sticky="w")

		algorithm_frame = ttk.LabelFrame(self.frame, text="Algorithm", padding=(10, 7))
		algorithm_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)

		for row, (label, value) in enumerate(
			(("Cohen-Sutherland", "cohen-sutherland"),
			 ("Liang-Barsky", "liang-barsky"))
		):
			ttk.Radiobutton(
				algorithm_frame,
				text=label,
				value=value,
				variable=selected_algorithm,
			).grid(row=row, column=0, sticky="w")

		style_frame = ttk.LabelFrame(
			self.frame,
			text="Color & Thickness",
			padding=(10, 7),
		)
		style_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 12), pady=10)
		style_frame.columnconfigure(2, weight=1)

		ttk.Label(style_frame, text="Color").grid(row=0, column=0, sticky="w", padx=(0, 8))
		self.color_swatch = tk.Label(
			style_frame,
			text="    ",
			background=line_color.get(),
			relief="sunken",
		)
		self.color_swatch.grid(row=0, column=1, padx=(0, 5))
		self.color_hex = tk.Label(
			style_frame,
			text=self._to_hex(parent, line_color.get()),
			width=8,
			anchor="w",
			relief="sunken",
			padx=4,
		)
		self.color_hex.grid(row=0, column=2, sticky="ew", padx=(0, 5))
		ttk.Button(
			style_frame,
			text="Choose...",
			command=on_choose_color,
		).grid(row=0, column=3, sticky="ew")
		line_color.trace_add(
			"write",
			lambda *_: self._update_color_display(parent, line_color.get()),
		)

		ttk.Label(style_frame, text="Thickness").grid(
			row=1, column=0, sticky="w", padx=(0, 8)
		)
		ttk.Combobox(
			style_frame,
			textvariable=line_width,
			values=(1, 2, 3, 4, 5),
			state="readonly",
			width=7,
		).grid(row=1, column=1, columnspan=3, sticky="ew")

		self.clip_button = ttk.Button(
			actions_parent,
			text="Clip",
			command=on_clip,
			style="Primary.TButton",
		)
		self.clip_button.pack(side="left", fill="x", expand=True, padx=(0, 4))
		self.clear_button = ttk.Button(actions_parent, text="Clear", command=on_clear)
		self.clear_button.pack(side="left", fill="x", expand=True, padx=(4, 0))

	def grid(self, **kwargs):
		self.frame.grid(**kwargs)

	@staticmethod
	def _to_hex(widget, color):
		red, green, blue = widget.winfo_rgb(color)
		return f"#{red // 257:02x}{green // 257:02x}{blue // 257:02x}"

	def _update_color_display(self, widget, color):
		self.color_swatch.configure(background=color)
		self.color_hex.configure(text=self._to_hex(widget, color))
