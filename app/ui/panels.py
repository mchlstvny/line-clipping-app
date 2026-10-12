import tkinter as tk
from tkinter import ttk


class Panels:
	def __init__(self, parent):
		self.frame = ttk.Frame(parent)
		self.frame.columnconfigure(0, weight=1)
		self.frame.rowconfigure(0, weight=1)
		self.frame.rowconfigure(1, weight=1)

		before_frame = ttk.LabelFrame(
			self.frame,
			text="Lines Before Clipping",
			padding=5,
		)
		before_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
		before_frame.rowconfigure(0, weight=1)
		before_frame.columnconfigure(0, weight=1)
		before_frame.rowconfigure(1, weight=0)
		self.before_list = tk.Listbox(
			before_frame,
			height=6,
			exportselection=False,
			font=("TkFixedFont", 10),
			background="#ffffff",
			foreground="#202a36",
			selectbackground="#dbe8fb",
			selectforeground="#172a43",
			borderwidth=0,
			highlightthickness=0,
			yscrollcommand=lambda *args: self.before_scrollbar.set(*args),
			xscrollcommand=lambda *args: self.before_xscrollbar.set(*args),
		)
		self.before_list.grid(row=0, column=0, sticky="nsew")
		self.before_scrollbar = ttk.Scrollbar(
			before_frame,			orient="vertical", command=self.before_list.yview
		)
		self.before_scrollbar.grid(row=0, column=1, sticky="ns")
		self.before_xscrollbar = ttk.Scrollbar(
			before_frame, orient="horizontal", command=self.before_list.xview
		)
		self.before_xscrollbar.grid(row=1, column=0, sticky="ew")

		after_frame = ttk.LabelFrame(
			self.frame,
			text="Lines After Clipping",
			padding=5,
		)
		after_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
		after_frame.rowconfigure(0, weight=1)
		after_frame.columnconfigure(0, weight=1)
		after_frame.rowconfigure(1, weight=0)
		self.after_list = tk.Listbox(
			after_frame,
			height=6,
			exportselection=False,
			font=("TkFixedFont", 10),
			background="#ffffff",
			foreground="#202a36",
			selectbackground="#dbe8fb",
			selectforeground="#172a43",
			borderwidth=0,
			highlightthickness=0,
			yscrollcommand=lambda *args: self.after_scrollbar.set(*args),
			xscrollcommand=lambda *args: self.after_xscrollbar.set(*args),
		)
		self.after_list.grid(row=0, column=0, sticky="nsew")
		self.after_scrollbar = ttk.Scrollbar(
			after_frame, orient="vertical", command=self.after_list.yview
		)
		self.after_scrollbar.grid(row=0, column=1, sticky="ns")
		self.after_xscrollbar = ttk.Scrollbar(
			after_frame, orient="horizontal", command=self.after_list.xview
		)
		self.after_xscrollbar.grid(row=1, column=0, sticky="ew")

	def grid(self, **kwargs):
		self.frame.grid(**kwargs)

	def add_before_item(self, text):
		self.before_list.insert(tk.END, text)
		self.before_list.see(tk.END)

	def clear_before(self):
		self.before_list.delete(0, tk.END)

	def add_after_item(self, text):
		self.after_list.insert(tk.END, text)
		self.after_list.see(tk.END)

	def clear_after(self):
		self.after_list.delete(0, tk.END)
