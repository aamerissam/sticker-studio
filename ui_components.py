# ui_components.py
import tkinter as tk
from tkinter import ttk


class ScrollableFrame(tk.Frame):
    """A frame with a scrollbar. Pack widgets into .inner"""
    def __init__(self, parent, bg="#12121F", *args, **kwargs):
        super().__init__(parent, bg=bg, *args, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg)
        self._window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_mousewheel()

    def _on_inner_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._window, width=event.width)

    def _bind_mousewheel(self):
        def _on_mousewheel(event):
            if event.delta:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        self.canvas.bind("<Enter>", lambda e: self._activate_scroll(_on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self._deactivate_scroll(_on_mousewheel))

    def _activate_scroll(self, handler):
        self.canvas.bind_all("<MouseWheel>", handler)
        self.canvas.bind_all("<Button-4>", handler)
        self.canvas.bind_all("<Button-5>", handler)

    def _deactivate_scroll(self, handler):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")