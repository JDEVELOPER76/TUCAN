import customtkinter as ctk
import os

class CustomDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, icono=None, button_text="OK"):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.icono_path = icono
        self.transient(parent)
        self.grab_set()

        self._create_content(message, button_text)

        # Variable para almacenar el ID del after
        self._after_id = None

        if icono and os.path.exists(icono):
            self._after_id = self.after(1, self._force_icon)
            self.icono_timer()

        self.centrar_pantalla(parent)
        try:
            if self.winfo_exists():
                self.focus_set()
        except Exception:
            pass

        # Asegurarse de que al cerrar, se cancele el after
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self._cancel_after()
        self.destroy()

    def _cancel_after(self):
        if hasattr(self, '_after_id') and self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _create_content(self, message, button_text):
        self._frame = ctk.CTkFrame(self)
        self._frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.label = ctk.CTkLabel(
            self._frame,
            text=message,
            wraplength=350,
            font=("Roboto", 12)
        )
        self.label.pack(pady=20, padx=20, fill="both", expand=True)

        self.button = ctk.CTkButton(
            self._frame,
            text=button_text,
            width=120,
            height=35,
            font=("Roboto", 12, "bold"),
            command=self._on_close
        )
        self.button.pack(pady=10)

    def _force_icon(self):
        if not self.winfo_exists():
            return
        if self.icono_path and os.path.exists(self.icono_path):
            try:
                self.iconbitmap(self.icono_path)
                self.wm_iconbitmap(self.icono_path)
                self.tk.call('wm', 'iconbitmap', self._w, self.icono_path)
            except Exception:
                pass

    def icono_timer(self):
        if not self.winfo_exists():
            return
        self._force_icon()
        self._after_id = self.after(100, self.llamado_icono)

    def llamado_icono(self):
        if not self.winfo_exists():
            self._cancel_after()
            return

        if hasattr(self, '_icon_attempts'):
            self._icon_attempts += 1
        else:
            self._icon_attempts = 1

        if self._icon_attempts < 20:
            self._force_icon()
            self._after_id = self.after(100, self.llamado_icono)
        else:
            self._cancel_after()

    def centrar_pantalla(self, parent):
        self.update_idletasks()
        try:
            if parent and parent.winfo_exists():
                parent_x = parent.winfo_x()
                parent_y = parent.winfo_y()
                parent_width = parent.winfo_width()
                parent_height = parent.winfo_height()
                x = parent_x + (parent_width // 2) - (400 // 2)
                y = parent_y + (parent_height // 2) - (200 // 2)
            else:
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                x = (screen_width // 2) - (400 // 2)
                y = (screen_height // 2) - (200 // 2)
            self.geometry(f"400x200+{x}+{y}")
        except Exception:
            self.geometry("400x200+300+200")

    def destroy(self):
        self._cancel_after()
        super().destroy()


# Subclases: ErrorDialog, SuccessDialog, InfoDialog
class ErrorDialog(CustomDialog):
    def __init__(self, parent, message, icono=None):
        super().__init__(parent, "Error", message, icono)
        self.after(0, lambda: self.button.configure(fg_color="#d9534f", hover_color="#c9302c"))


class SuccessDialog(CustomDialog):
    def __init__(self, parent, message, icono=None):
        super().__init__(parent, "Éxito", message, icono, button_text="Aceptar")
        self.after(0, lambda: self.button.configure(fg_color="#5cb85c", hover_color="#4cae4c"))


class InfoDialog(CustomDialog):
    def __init__(self, parent, message, icono=None):
        super().__init__(parent, "Info", message, icono, button_text="Aceptar")
        self.after(0, lambda: self.button.configure(fg_color="#1cad3c", hover_color="#4cae4c"))