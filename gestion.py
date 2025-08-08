import sqlite3
import customtkinter as ctk
import os
from tkinter import ttk
from asistentes.cuadro_mensaje import ErrorDialog
from asistentes.iconos import iconos

DB_DIR = os.path.join(os.path.dirname(__file__), "BASE DE DATOS")
os.makedirs(DB_DIR, exist_ok=True)
DB_FILE = os.path.join(DB_DIR, "productos.db")
conn = None

entry_nombre = entry_descripcion = entry_stock = entry_precio_1 = entry_precio_2 = entry_precio_3 = None
tree = None
selected_product_id = None
entry_buscar_gestion = None

# ---------- UTILS ----------
def show_messagebox(title, message, icon="info", confirm=False):
    result = {"value": None}
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    width, height = 350, 180
    x = (dialog.winfo_screenwidth() - width) // 2
    y = (dialog.winfo_screenheight() - height) // 2
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.focus_force()

    icon_text = {"info": "ℹ️", "error": "❌", "check": "✅", "warning": "⚠️"}
    ctk.CTkLabel(dialog, text=icon_text.get(icon, "ℹ️"), font=("Arial", 40)).pack(pady=(10, 0))
    ctk.CTkLabel(dialog, text=message, font=("Arial", 14), wraplength=320).pack(pady=(5, 10))

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=5)

    if confirm:
        def set_yes():
            result["value"] = "Sí"
            dialog.destroy()

        def set_no():
            result["value"] = "No"
            dialog.destroy()

        ctk.CTkButton(btn_frame, text="Sí", command=set_yes, fg_color="#2ecc71", width=90).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="No", command=set_no, fg_color="#e74c3c", width=90).pack(side="left", padx=10)
        dialog.wait_window()
        return result["value"]
    else:
        ctk.CTkButton(btn_frame, text="Aceptar", command=dialog.destroy, width=120).pack()
        dialog.wait_window()
        return None

# ---------- DB ----------
def connect_db():
    global conn
    conn = sqlite3.connect(DB_FILE)

def create_table():
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            stock INTEGER DEFAULT 0,
            precio_1 REAL DEFAULT 0,
            precio_2 REAL DEFAULT 0,
            precio_3 REAL DEFAULT 0
        )
    ''')
    conn.commit()

# ---------- CRUD ----------
def add_product():
    nombre = entry_nombre.get().strip()
    descripcion = entry_descripcion.get().strip()
    try:
        stock = int(entry_stock.get().strip())
    except ValueError:
        show_messagebox("Error", "Stock debe ser un número entero", icon="error")
        return
    try:
        precio_1 = float(entry_precio_1.get().strip())
        precio_2 = float(entry_precio_2.get().strip())
        precio_3 = float(entry_precio_3.get().strip())
    except ValueError:
        show_messagebox("Error", "Precios deben ser números válidos", icon="error")
        return
    if not nombre:
        show_messagebox("Error", "El nombre es obligatorio", icon="error")
        return
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO productos (nombre, descripcion, stock, precio_1, precio_2, precio_3)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, descripcion, stock, precio_1, precio_2, precio_3))
    conn.commit()
    show_messagebox("Éxito", f"Producto '{nombre}' agregado", icon="check")
    clear_form()
    load_products()

def update_product():
    global selected_product_id
    if selected_product_id is None:
        show_messagebox("Error", "Seleccione un producto para actualizar", icon="error")
        return
    nombre = entry_nombre.get().strip()
    descripcion = entry_descripcion.get().strip()
    try:
        stock = int(entry_stock.get().strip())
    except ValueError:
        show_messagebox("Error", "Stock debe ser un número entero", icon="error")
        return
    try:
        precio_1 = float(entry_precio_1.get().strip())
        precio_2 = float(entry_precio_2.get().strip())
        precio_3 = float(entry_precio_3.get().strip())
    except ValueError:
        show_messagebox("Error", "Precios deben ser números válidos", icon="error")
        return
    if not nombre:
        show_messagebox("Error", "El nombre es obligatorio", icon="error")
        return
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE productos
        SET nombre = ?, descripcion = ?, stock = ?, precio_1 = ?, precio_2 = ?, precio_3 = ?
        WHERE id = ?
    ''', (nombre, descripcion, stock, precio_1, precio_2, precio_3, selected_product_id))
    conn.commit()
    show_messagebox("Éxito", "Producto actualizado", icon="check")
    clear_form()
    load_products()

def delete_product():
    global selected_product_id
    if selected_product_id is None:
        show_messagebox("Error", "Seleccione un producto para eliminar", icon="error")
        return
    result = show_messagebox("Confirmar", "¿Está seguro de eliminar este producto?", icon="warning", confirm=True)
    if result != "Sí":
        return
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id = ?', (selected_product_id,))
    conn.commit()
    show_messagebox("Éxito", "Producto eliminado", icon="check")
    clear_form()
    load_products()

# ---------- LIST / FILTER ----------
def load_products(filter_text=''):
    global tree
    for item in tree.get_children():
        tree.delete(item)
    cursor = conn.cursor()
    if filter_text == '':
        cursor.execute('SELECT id, nombre, descripcion, precio_1, precio_2, precio_3, stock FROM productos')
    else:
        if filter_text.isdigit():
            cursor.execute('''
                SELECT id, nombre, descripcion, precio_1, precio_2, precio_3, stock
                FROM productos WHERE id = ? OR nombre LIKE ?
            ''', (int(filter_text), f'%{filter_text}%'))
        else:
            cursor.execute('''
                SELECT id, nombre, descripcion, precio_1, precio_2, precio_3, stock
                FROM productos WHERE nombre LIKE ?
            ''', (f'%{filter_text}%',))
    rows = cursor.fetchall()
    for row in rows:
        tree.insert('', 'end', values=row)

def clear_form():
    global selected_product_id
    selected_product_id = None
    entry_nombre.delete(0, "end")
    entry_descripcion.delete(0, "end")
    entry_stock.delete(0, "end")
    entry_precio_1.delete(0, "end")
    entry_precio_2.delete(0, "end")
    entry_precio_3.delete(0, "end")
    tree.selection_remove(tree.selection())
    entry_buscar_gestion.delete(0, "end")
    load_products()

def on_product_select(event):
    global selected_product_id
    selected = tree.selection()
    if selected:
        item = tree.item(selected[0])
        data = item['values']
        selected_product_id = data[0]
        entry_nombre.delete(0, "end")
        entry_nombre.insert(0, data[1])
        entry_descripcion.delete(0, "end")
        entry_descripcion.insert(0, data[2])
        entry_stock.delete(0, "end")
        entry_stock.insert(0, data[6])
        entry_precio_1.delete(0, "end")
        entry_precio_1.insert(0, f"{float(data[3]):.2f}")
        entry_precio_2.delete(0, "end")
        entry_precio_2.insert(0, f"{float(data[4]):.2f}")
        entry_precio_3.delete(0, "end")
        entry_precio_3.insert(0, f"{float(data[5]):.2f}")

def on_key_release_gestion(event):
    filter_text = entry_buscar_gestion.get().strip()
    load_products(filter_text)

# ---------- MAIN WINDOW ----------
def main_simple():
    global entry_nombre, entry_descripcion, entry_stock, entry_precio_1, entry_precio_2, entry_precio_3, tree, entry_buscar_gestion

    connect_db()
    create_table()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTkToplevel()
    root.title("Gestión de Productos")
    icon_path = iconos("imagenes", "logo.ico")
    try:
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        ErrorDialog(None, f"Advertencia: No se pudo cargar el icono: {e}", iconos("imagenes", "error.ico"))
    root.state("zoomed")
    root.grab_set()

    style = ttk.Style(root)
    style.theme_use('default')
    style.configure("Treeview.Heading", foreground="black", background="white")

    label_gestion = ctk.CTkLabel(root, text="Gestión de Productos", font=ctk.CTkFont(size=16, weight="bold"))
    label_gestion.pack(pady=(10, 0))

    search_frame = ctk.CTkFrame(root)
    search_frame.pack(fill="x", padx=10, pady=(0, 5))
    ctk.CTkLabel(search_frame, text="Buscar por Nombre o ID:").pack(side="left")
    entry_buscar_gestion = ctk.CTkEntry(search_frame, width=300)
    entry_buscar_gestion.pack(side="left", padx=(5, 0))
    entry_buscar_gestion.bind('<KeyRelease>', on_key_release_gestion)

    form_frame = ctk.CTkFrame(root)
    form_frame.pack(fill="x", padx=10)

    ctk.CTkLabel(form_frame, text="Nombre:").grid(row=0, column=0, sticky="w", pady=2)
    entry_nombre = ctk.CTkEntry(form_frame)
    entry_nombre.grid(row=0, column=1, sticky="ew", pady=2)

    ctk.CTkLabel(form_frame, text="Descripción:").grid(row=1, column=0, sticky="w", pady=2)
    entry_descripcion = ctk.CTkEntry(form_frame)
    entry_descripcion.grid(row=1, column=1, sticky="ew", pady=2)

    ctk.CTkLabel(form_frame, text="Stock:").grid(row=2, column=0, sticky="w", pady=2)
    entry_stock = ctk.CTkEntry(form_frame)
    entry_stock.grid(row=2, column=1, sticky="ew", pady=2)

    ctk.CTkLabel(form_frame, text="Precio 1:").grid(row=0, column=2, sticky="w", padx=10, pady=2)
    entry_precio_1 = ctk.CTkEntry(form_frame)
    entry_precio_1.grid(row=0, column=3, sticky="ew", pady=2)

    ctk.CTkLabel(form_frame, text="Precio 2:").grid(row=1, column=2, sticky="w", padx=10, pady=2)
    entry_precio_2 = ctk.CTkEntry(form_frame)
    entry_precio_2.grid(row=1, column=3, sticky="ew", pady=2)

    ctk.CTkLabel(form_frame, text="Precio 3:").grid(row=2, column=2, sticky="w", padx=10, pady=2)
    entry_precio_3 = ctk.CTkEntry(form_frame)
    entry_precio_3.grid(row=2, column=3, sticky="ew", pady=2)

    for col in range(4):
        form_frame.grid_columnconfigure(col, weight=1)

    button_frame = ctk.CTkFrame(root)
    button_frame.pack(fill="x", padx=10, pady=10)

    ctk.CTkButton(button_frame, text="Agregar Producto", command=add_product).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Actualizar Producto", command=update_product).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Eliminar Producto", command=delete_product).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Limpiar Formulario", command=clear_form).pack(side="left", padx=5)

    from ventas_user import CTkTreeview
    tree_frame = ctk.CTkFrame(root)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    columns = ('ID', 'Nombre', 'Descripción', 'Precio 1', 'Precio 2', 'Precio 3', 'Stock')
    tree = CTkTreeview(tree_frame, columns=columns, show='headings', height=10)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=90, anchor="center")
    tree.column('Descripción', width=200)
    tree.pack(fill="both", expand=True)
    tree.bind('<<TreeviewSelect>>', on_product_select)

    load_products()
    root.mainloop()



