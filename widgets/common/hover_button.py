import tkinter as tk

class HoverButton(tk.Button):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.default_bg = self['bg']  # Guardar el color de fondo original
        self.default_bd = self['bd']  # Guardar el borde original
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        # Cambiar el color de fondo y borde al pasar el cursor
        self.config(bg="#9CDCFE", relief="raised")

    def on_leave(self, event):
        # Restaurar el color de fondo y borde originales al salir el cursor
        self.config(bg=self.default_bg, bd=self.default_bd, relief="flat")