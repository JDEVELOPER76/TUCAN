import os
import sqlite3
import customtkinter as ctk
from asistentes.cuadro_mensaje import ErrorDialog, SuccessDialog
from asistentes.iconos import iconos

DB_DIR   = os.path.join(os.path.dirname(__file__), "BASE DE DATOS")
os.makedirs(DB_DIR, exist_ok=True)
DB_FILE  = os.path.join(DB_DIR, "productos.db")

class IngresoMercaderiaApp:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
        self.selected_id = None

        self.root = ctk.CTkToplevel()
        self.root.title("Ingreso de Mercadería")
        self.root._state_before_windows_set_titlebar_color = "zoomed"
        self.root.iconbitmap(iconos("imagenes", "logo.ico"))
        self.root.grab_set()

        self.build_ui()
        self.load_products()

    def build_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Título
        title = ctk.CTkLabel(self.root, text="📥 Ingreso de Mercadería", font=("Roboto", 20, "bold"))
        title.pack(pady=10)

        # Frame de búsqueda
        search_frame = ctk.CTkFrame(self.root)
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(search_frame, text="Buscar por Nombre o ID:").pack(side="left", padx=5)
        self.entry_buscar = ctk.CTkEntry(search_frame, width=250)
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind("<KeyRelease>", self.on_key_release)

        # Treeview
        from ventas_user import CTkTreeview
        self.tree = CTkTreeview(self.root, columns=("ID", "Nombre", "Descripción", "Stock"), show="headings", height=15)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        for col in ("ID", "Nombre", "Descripción", "Stock"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col == "Descripción" else 100, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Frame de ingreso
        ingreso_frame = ctk.CTkFrame(self.root)
        ingreso_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(ingreso_frame, text="Producto seleccionado:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.label_producto = ctk.CTkLabel(ingreso_frame, text="Ninguno", font=("Roboto", 14, "bold"))
        self.label_producto.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(ingreso_frame, text="Cantidad a ingresar:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_cantidad = ctk.CTkEntry(ingreso_frame, width=120)
        self.entry_cantidad.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkButton(ingreso_frame, text="Registrar Ingreso", command=self.registrar_ingreso).grid(row=1, column=2, padx=20, pady=5)

    def load_products(self, filter_text=""):
        self.tree.delete(*self.tree.get_children())
        query = "SELECT id, nombre, descripcion, stock FROM productos"
        params = ()
        if filter_text:
            if filter_text.isdigit():
                query += " WHERE id = ? OR nombre LIKE ?"
                params = (int(filter_text), f"%{filter_text}%")
            else:
                query += " WHERE nombre LIKE ?"
                params = (f"%{filter_text}%",)
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def on_key_release(self, event):
        self.load_products(self.entry_buscar.get().strip())

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])["values"]
            self.selected_id = item[0]
            self.label_producto.configure(text=f"{item[1]} (Stock actual: {item[3]})")
        else:
            self.selected_id = None
            self.label_producto.configure(text="Ninguno")

    def registrar_ingreso(self):
        if self.selected_id is None:
            ErrorDialog(self.root, "Por favor seleccione un producto.", iconos("imagenes", "error.ico"))
            return
        try:
            cantidad = int(self.entry_cantidad.get().strip())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            ErrorDialog(self.root, "Cantidad debe ser un número entero positivo.", iconos("imagenes", "error.ico"))
            return

        self.cursor.execute("SELECT stock FROM productos WHERE id = ?", (self.selected_id,))
        stock_actual = self.cursor.fetchone()[0]
        nuevo_stock = stock_actual + cantidad

        self.cursor.execute("UPDATE productos SET stock = ? WHERE id = ?", (nuevo_stock, self.selected_id))
        self.conn.commit()

        SuccessDialog(self.root, f"Ingreso registrado. Nuevo stock: {nuevo_stock}", iconos("imagenes", "exito.ico"))
        self.entry_cantidad.delete(0, "end")
        self.load_products()


def run_ingreso_mercaderia():
    IngresoMercaderiaApp()

