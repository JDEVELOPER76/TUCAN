import sqlite3
import customtkinter as ctk
import os
from tkinter import ttk
from cuadro_mensaje import ErrorDialog
# GESTION DE PRODUCTOS
DB_FILE = 'productos.db'
conn = None

entry_nombre = None
entry_descripcion = None
entry_stock = None
entry_precio_1 = None
entry_precio_2 = None
entry_precio_3 = None
tree = None
selected_product_id = None

entry_buscar = None
entry_ingreso = None
tree_mercaderia = None
selected_mercaderia_id = None

entry_buscar_gestion = None

#cuadro de mensaje
def show_messagebox(title, message, icon="info", confirm=False):
    result = {"value": None}
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("350x180")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.focus_force()
    # Icono
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
    load_mercaderia_products()

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
    load_mercaderia_products()

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
    load_mercaderia_products()

def load_products(filter_text=''):
    global tree
    for item in tree.get_children():
        tree.delete(item)
    cursor = conn.cursor()
    if filter_text == '':
        cursor.execute('SELECT id, nombre, descripcion, precio_1, precio_2, precio_3, stock FROM productos')
    else:
        if filter_text.isdigit():
            cursor.execute('SELECT id, nombre, descripcion, precio_1, precio_2, precio_3, stock FROM productos WHERE id = ? OR nombre LIKE ?', 
                         (int(filter_text), f'%{filter_text}%'))
        else:
            cursor.execute('SELECT id, nombre, descripcion, precio_1, precio_2, precio_3, stock FROM productos WHERE nombre LIKE ?', 
                         (f'%{filter_text}%',))
    rows = cursor.fetchall()
    for row in rows:
        tree.insert('', "end", values=row)

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

def load_mercaderia_products():
    global tree_mercaderia
    for item in tree_mercaderia.get_children():
        tree_mercaderia.delete(item)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, descripcion, stock, precio_1, precio_2, precio_3 FROM productos')
    rows = cursor.fetchall()
    for row in rows:
        tree_mercaderia.insert('', "end", values=row)

def buscar_mercaderia():
    search_text = entry_buscar.get().strip()
    for item in tree_mercaderia.get_children():
        tree_mercaderia.delete(item)
    cursor = conn.cursor()
    if search_text == '':
        cursor.execute('SELECT id, nombre, descripcion, stock, precio_1, precio_2, precio_3 FROM productos')
    else:
        if search_text.isdigit():
            cursor.execute('SELECT id, nombre, descripcion, stock, precio_1, precio_2, precio_3 FROM productos WHERE id = ? OR nombre LIKE ?', (int(search_text), f'%{search_text}%'))
        else:
            cursor.execute('SELECT id, nombre, descripcion, stock, precio_1, precio_2, precio_3 FROM productos WHERE nombre LIKE ?', (f'%{search_text}%',))
    rows = cursor.fetchall()
    for row in rows:
        tree_mercaderia.insert('', "end", values=row)

def on_select_mercaderia(event):
    global selected_mercaderia_id
    selected = tree_mercaderia.selection()
    if selected:
        item = tree_mercaderia.item(selected[0])
        data = item['values']
        selected_mercaderia_id = data[0]
    else:
        selected_mercaderia_id = None

def ingresar_mercaderia():
    global selected_mercaderia_id
    if selected_mercaderia_id is None:
        show_messagebox("Error", "Seleccione un producto para ingresar mercadería", icon="error")
        return
    try:
        ingreso = int(entry_ingreso.get().strip())
        if ingreso <= 0:
            show_messagebox("Error", "El ingreso debe ser un número entero positivo", icon="error")
            return
    except ValueError:
        show_messagebox("Error", "El ingreso debe ser un número entero válido", icon="error")
        return
    cursor = conn.cursor()
    cursor.execute('SELECT stock FROM productos WHERE id = ?', (selected_mercaderia_id,))
    current_stock_row = cursor.fetchone()
    if not current_stock_row:
        show_messagebox("Error", "Producto no encontrado en la base de datos", icon="error")
        return
    current_stock = current_stock_row[0] or 0
    nuevo_stock = current_stock + ingreso
    cursor.execute('UPDATE productos SET stock = ? WHERE id = ?', (nuevo_stock, selected_mercaderia_id))
    conn.commit()
    show_messagebox("Éxito", f"Se ingresaron {ingreso} unidades. Nuevo stock: {nuevo_stock}", icon="check")
    entry_ingreso.delete(0, "end")
    load_products(entry_buscar_gestion.get().strip())
    load_mercaderia_products()

def on_key_release_gestion(event):
    filter_text = entry_buscar_gestion.get().strip()
    load_products(filter_text)

def on_key_release_mercaderia(event):
    buscar_mercaderia()

def main_simple():
    global entry_nombre, entry_descripcion, entry_stock, entry_precio_1, entry_precio_2, entry_precio_3, tree
    global entry_buscar, entry_ingreso, tree_mercaderia
    global entry_buscar_gestion

    connect_db()
    create_table()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTkToplevel()
    root.title("Gestion de Productos")
    icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
    try:
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        ErrorDialog(None,f"Advertencia: No se pudo cargar el icono: {e}")
    root.state("zoomed")
    root.grab_set()

    # Estilo para encabezados en negro y fondo blanco
    style = ttk.Style(root)
    style.theme_use('default')
    style.configure("Treeview.Heading", foreground="black", background="white")

    # --- Sección de Gestión de Productos ---
    label_gestion = ctk.CTkLabel(root, text="Gestion de Productos", font=ctk.CTkFont(size=16, weight="bold"))
    label_gestion.pack(pady=(10,0))

    # caja de busqueda para los productos
    search_frame = ctk.CTkFrame(root)
    search_frame.pack(fill="x", padx=10, pady=(0,5))
    ctk.CTkLabel(search_frame, text="Buscar por Nombre o ID:").pack(side="left")
    entry_buscar_gestion = ctk.CTkEntry(search_frame, width=300)
    entry_buscar_gestion.pack(side="left", padx=(5,0))
    entry_buscar_gestion.bind('<KeyRelease>', on_key_release_gestion)

    # frame
    form_frame = ctk.CTkFrame(root)
    form_frame.pack(fill="x", padx=10)

    # Nombre
    ctk.CTkLabel(form_frame, text="Nombre:").grid(row=0, column=0, sticky="w", pady=2)
    entry_nombre = ctk.CTkEntry(form_frame)
    entry_nombre.grid(row=0, column=1, sticky="ew", pady=2)

    # Descripcion
    ctk.CTkLabel(form_frame, text="Descripción:").grid(row=1, column=0, sticky="w", pady=2)
    entry_descripcion = ctk.CTkEntry(form_frame)
    entry_descripcion.grid(row=1, column=1, sticky="ew", pady=2)

    # Stock
    ctk.CTkLabel(form_frame, text="Stock:").grid(row=2, column=0, sticky="w", pady=2)
    entry_stock = ctk.CTkEntry(form_frame)
    entry_stock.grid(row=2, column=1, sticky="ew", pady=2)

    # Precio 1
    ctk.CTkLabel(form_frame, text="Precio 1:").grid(row=0, column=2, sticky="w", padx=10 ,pady=2)
    entry_precio_1 = ctk.CTkEntry(form_frame)
    entry_precio_1.grid(row=0, column=3, sticky="ew", pady=2)

    # Precio 2
    ctk.CTkLabel(form_frame, text="Precio 2:").grid(row=1, column=2, sticky="w", padx=10, pady=2)
    entry_precio_2 = ctk.CTkEntry(form_frame)
    entry_precio_2.grid(row=1, column=3, sticky="ew", pady=2)

    # Precio 3
    ctk.CTkLabel(form_frame, text="Precio 3:").grid(row=2, column=2, sticky="w", padx=10, pady=2)
    entry_precio_3 = ctk.CTkEntry(form_frame)
    entry_precio_3.grid(row=2, column=3, sticky="ew", pady=2)

    for col in range(4):
        form_frame.grid_columnconfigure(col, weight=1)

    # Buttons frame
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(fill="x", padx=10, pady=10)

    ctk.CTkButton(button_frame, text="Agregar Producto", command=add_product).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Actualizar Producto", command=update_product).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Eliminar Producto", command=delete_product).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Limpiar Formulario", command=clear_form).pack(side="left", padx=5)

    # Treeview desde ventas user , supongo que da igual 
    from ventas_user import CTkTreeview
    tree_frame = ctk.CTkFrame(root)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

    columns = ('ID', 'Nombre', 'Descripción', 'Precio 1', 'Precio 2', 'Precio 3' , 'Stock')
    tree = CTkTreeview(tree_frame, columns=columns, show='headings', height=10)

    for col in columns:
        tree.heading(col, text=col)
        if col == 'Descripción':
            tree.column(col, width=200)
        else:
            tree.column(col, width=100, anchor="center")
    tree.pack(fill="both", expand=True)
    tree.bind('<<TreeviewSelect>>', on_product_select)

    # --- Sección de Ingreso de Mercaderia ---
    sep = ctk.CTkFrame(root, height=2)
    sep.pack(fill="x", pady=10, padx=10)

    label_mercaderia = ctk.CTkLabel(root, text="Ingreso de Mercadería", font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
    label_mercaderia.pack(pady=(0, 10))

    merca_frame = ctk.CTkFrame(root)
    merca_frame.pack(fill="both", expand=True, padx=10)

    # Buscar producto (por ID o nombre)
    ctk.CTkLabel(merca_frame, text="Buscar por Nombre o ID:", text_color="white").grid(row=0, column=0, sticky="w", pady=2)
    entry_buscar = ctk.CTkEntry(merca_frame, width=200)
    entry_buscar.grid(row=0, column=1, sticky="w", pady=2, padx=5)
    entry_buscar.bind('<KeyRelease>', lambda e: buscar_mercaderia())

    # Treeview para productos para ingreso mercaderia
    columns_mercaderia = ('ID', 'Nombre', 'Descripción', 'Stock', 'Precio 1', 'Precio 2', 'Precio 3')
    tree_mercaderia = CTkTreeview(merca_frame, columns=columns_mercaderia, show='headings', height=7)

    for col in columns_mercaderia:
        tree_mercaderia.heading(col, text=col)
        if col == 'Descripción':
            tree_mercaderia.column(col, width=200)
        else:
            tree_mercaderia.column(col, width=100, anchor="center")
    tree_mercaderia.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=5)

    tree_mercaderia.bind('<<TreeviewSelect>>', on_select_mercaderia)

    merca_frame.grid_rowconfigure(1, weight=1)
    merca_frame.grid_columnconfigure(1, weight=1)

    # Ingreso de cantidad
    ctk.CTkLabel(merca_frame, text="Cantidad a ingresar:", text_color="white").grid(row=2, column=0, sticky="w", pady=2)
    entry_ingreso = ctk.CTkEntry(merca_frame, width=100)
    entry_ingreso.grid(row=2, column=1, sticky="w", pady=2, padx=5)

    ctk.CTkButton(merca_frame, text="Registrar Ingreso", command=ingresar_mercaderia).grid(row=2, column=2, sticky="w", pady=2)
    # Inicializar datos
    load_products()
    load_mercaderia_products()
    root.mainloop()




