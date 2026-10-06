import tkinter as tk


class Toolbar:
	def __init__(
		self,
		parent,
		create_mode,
		selected_algorithm,
		line_color,
		line_width,
		on_create_mode_changed,
		on_clip,
		on_clear,
		actions_parent,
	):
		self.frame = tk.Frame(parent)
		self.frame.columnconfigure(0, weight=1, uniform="layout")
		self.frame.columnconfigure(1, weight=1, uniform="layout")
		self.frame.columnconfigure(2, weight=1, uniform="layout")

		create_frame = tk.LabelFrame(self.frame, text="Create", padx=8, pady=5)
		create_frame.grid(row=0, column=0, sticky="nsew", padx=(12, 5), pady=10)

		for row, (label, value) in enumerate(
			(("Line", "line"), ("Clipping Area", "clipping-area"),
			 ("Rectangle", "rectangle"), ("Circle", "circle"))
		):
			tk.Radiobutton(
				create_frame,
				text=label,
				value=value,
				variable=create_mode,
				command=on_create_mode_changed,
			).grid(row=row, column=0, sticky="w")

		algorithm_frame = tk.LabelFrame(self.frame, text="Algorithm", padx=8, pady=5)
		algorithm_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)

		for row, (label, value) in enumerate(
			(("Cohen-Sutherland", "cohen-sutherland"),
			 ("Liang-Barsky", "liang-barsky"))
		):
			tk.Radiobutton(
				algorithm_frame,
				text=label,
				value=value,
				variable=selected_algorithm,
			).grid(row=row, column=0, sticky="w")

		style_frame = tk.LabelFrame(
			self.frame,
			text="Color & Thickness",
			padx=8,
			pady=5,
		)
		style_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 12), pady=10)
		style_frame.columnconfigure(1, weight=1)

		tk.Label(style_frame, text="Color").grid(row=0, column=0, sticky="w", padx=(0, 8))
		tk.OptionMenu(
			style_frame,
			line_color,
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
			line_width,
			1,
			2,
			3,
			4,
			5,
		).grid(row=1, column=1, sticky="ew")

		self.clip_button = tk.Button(actions_parent, text="Clip", command=on_clip)
		self.clip_button.pack(side="left", fill="x", expand=True, padx=(0, 4))
		self.clear_button = tk.Button(actions_parent, text="Clear", command=on_clear)
		self.clear_button.pack(side="left", fill="x", expand=True, padx=(4, 0))

	def grid(self, **kwargs):
		self.frame.grid(**kwargs)
