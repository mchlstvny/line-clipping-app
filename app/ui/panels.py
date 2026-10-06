import tkinter as tk


class Panels:
	def __init__(self, parent):
		self.frame = tk.Frame(parent)
		self.frame.columnconfigure(0, weight=1)
		self.frame.rowconfigure(0, weight=1)
		self.frame.rowconfigure(1, weight=1)

		before_frame = tk.LabelFrame(
			self.frame,
			text="Lines Before Clipping",
			padx=5,
			pady=5,
		)
		before_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
		before_frame.rowconfigure(0, weight=1)
		before_frame.columnconfigure(0, weight=1)
		self.before_list = tk.Listbox(before_frame, height=6, exportselection=False)
		self.before_list.grid(row=0, column=0, sticky="nsew")

		after_frame = tk.LabelFrame(
			self.frame,
			text="Lines After Clipping",
			padx=5,
			pady=5,
		)
		after_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
		after_frame.rowconfigure(0, weight=1)
		after_frame.columnconfigure(0, weight=1)
		self.after_list = tk.Listbox(after_frame, height=6, exportselection=False)
		self.after_list.grid(row=0, column=0, sticky="nsew")

	def grid(self, **kwargs):
		self.frame.grid(**kwargs)

	def add_before_item(self, text):
		self.before_list.insert(tk.END, text)

	def clear_before(self):
		self.before_list.delete(0, tk.END)

	def add_after_item(self, text):
		self.after_list.insert(tk.END, text)

	def clear_after(self):
		self.after_list.delete(0, tk.END)
