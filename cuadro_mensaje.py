"""Cuadros de dialogos personalizados con CTK(Toplevel)
"""


import customtkinter as ctk

class CustomDialog(ctk.CTkToplevel):
    """Padre de ErrorDialog , SuccesDialog , InfoDialog"""
    def __init__(self, parent, title, message, button_text="OK"):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grab_set()
        self.transient(parent)
        self._frame = ctk.CTkFrame(self)
        self._frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.label = ctk.CTkLabel(self._frame, text=message, wraplength=350, font=("Roboto", 12))
        self.label.pack(pady=20, padx=20, fill="both", expand=True)
        self.button = ctk.CTkButton(self._frame, text=button_text, width=120, height=35,
                                    font=("Roboto", 12, "bold"), command=self.destroy)
        self.button.pack(pady=10)


class ErrorDialog(CustomDialog):
    """
    Cuadro de diálogo personalizado para mostrar mensajes de error.

    Este diálogo se utiliza para alertar al usuario sobre errores en la aplicación,
    con colores específicos para llamar la atención.

    Args:
        parent (ctk.Widget): El widget padre que contiene el diálogo (puede ser None).
        message (str): El mensaje de error que se mostrará.

    Example:
        ErrorDialog(None, "No se pudo cargar la imagen.")
    """
    def __init__(self, parent, message):
        super().__init__(parent, "Error", message)
        self.after(100, lambda: self.button.configure(fg_color="#d9534f", hover_color="#c9302c"))



class SuccessDialog(CustomDialog):
    """
    Cuadro de diálogo personalizado para mostrar mensajes de ok.

    Este diálogo se utiliza para alertar al usuario sobre (ok) en la aplicación,
    con colores específicos para llamar la atención.

    Args:
        parent (ctk.Widget): El widget padre que contiene el diálogo (puede ser None).
        message (str): El mensaje de exito que se mostrara.

    Example:
        SuccessDialog(None, "Exito")
    """
    def __init__(self, parent, message):
        super().__init__(parent, "Éxito", message, "Aceptar")
        self.after(100, lambda: self.button.configure(fg_color="#5cb85c", hover_color="#4cae4c"))

class InfoDialog(CustomDialog):
    """
    Cuadro de diálogo personalizado para mostrar mensajes de informacion.

    Este diálogo se utiliza para alertar al usuario sobre la informacion en la aplicación,
    con colores específicos para llamar la atención.

    Args:
        parent (ctk.Widget): El widget padre que contiene el diálogo (puede ser None).
        message (str): El mensaje de informacion puede ir aqui.

    Example:
        InfoDialog(None, "Los campos no pueden estar vacios")
    """
    def __init__(self, parent, message):
        super().__init__(parent, "Info", message, "Aceptar")
        self.after(100, lambda: self.button.configure(fg_color="#1cad3c", hover_color="#4cae4c"))