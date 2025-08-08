import sqlite3
import customtkinter as ctk
from datetime import datetime
import os
import json
from tkinter import ttk
from reportlab.platypus import SimpleDocTemplate,Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from asistentes.cuadro_mensaje import ErrorDialog

DB_DIR   = os.path.join(os.path.dirname(__file__), "BASE DE DATOS")
os.makedirs(DB_DIR, exist_ok=True)
DB_PRODUCTOS = os.path.join(DB_DIR, "productos.db")
DB_VENTAS    = os.path.join(DB_DIR, "ventas.db")

#------------------------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
JSON_DIR = os.path.join(BASE_DIR, "JSON")
os.makedirs(JSON_DIR, exist_ok=True)
COUNTER_FILE = os.path.join(JSON_DIR, "factura_counter.json")
EMPRESA = os.path.join(JSON_DIR,"empresa.json")


def siguiente_numero_factura():
    if not os.path.exists(COUNTER_FILE):
        cont = 1
    else:
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            cont = json.load(f).get("ultimo", 0) + 1

    with open(COUNTER_FILE, "w", encoding="utf-8") as f:
        json.dump({"ultimo": cont}, f)

    return f"{cont:010d}"


class CTkTreeview(ttk.Treeview):
    def __init__(self, master=None, **kwargs):
        self.style = ttk.Style()
        self.style.configure("CTk.Treeview",
                             background="white",
                             foreground="black",
                             fieldbackground="white",
                             borderwidth=0)
        self.style.map('CTk.Treeview',
                       background=[('selected', '#1f538d')],
                       foreground=[('selected', 'white')])
        self.style.configure("CTk.Treeview.Heading",
                             background="#2fcf2f",
                             foreground="black",
                             relief="flat")
        self.style.map("CTk.Treeview.Heading",
                       background=[('active', "#209CF5")],
                       foreground=[('active', 'black')])
        kwargs["style"] = "CTk.Treeview"
        super().__init__(master, **kwargs)


def crear_sistema_ventas_tucan():
    class SistemaVentasTucan(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("SISTEMA DE FACTURACION TUCAN")
            self._state_before_windows_set_titlebar_color = 'zoomed'
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")

            self.total_venta = 0.0
            self.productos_venta = {}
            self.tipo_precio_seleccionado = ctk.StringVar(value="precio_1")
            self.tipo_precio_seleccionado.trace_add("write", self.actualizar_precios_venta)

            self.conectar_bases_datos()
            self.crear_interfaz_principal()
            self.cargar_productos()

        def logout(self):
            confirm_dialog = ctk.CTkToplevel(self)
            confirm_dialog.title("Confirmar cierre de sesión")
            width, height = 300, 150
            screen_width = confirm_dialog.winfo_screenwidth()
            screen_height = confirm_dialog.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            confirm_dialog.geometry(f"{width}x{height}+{x}+{y}")
            confirm_dialog.resizable(False, False)
            confirm_dialog.grab_set()
            ctk.CTkLabel(confirm_dialog, text="¿Está seguro que desea cerrar sesión?", font=("Roboto", 14)).pack(pady=(20, 15))
            btn_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
            btn_frame.pack(pady=10)
            ctk.CTkButton(btn_frame, text="Sí", command=lambda: self.confirmar_logout(confirm_dialog), fg_color="#2ecc71").pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="No", command=confirm_dialog.destroy, fg_color="#e74c3c").pack(side="left", padx=10)

        def confirmar_logout(self, dialog):
            dialog.destroy()
            self.destroy()
            from TUCAN import run_login_app
            run_login_app()

        def conectar_bases_datos(self):
            try:
                self.conn_productos = sqlite3.connect(DB_PRODUCTOS)
                self.cursor_productos = self.conn_productos.cursor()
                self.cursor_productos.execute('''CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    precio_1 REAL NOT NULL,
                    precio_2 REAL NOT NULL,
                    precio_3 REAL NOT NULL,
                    stock INTEGER NOT NULL)''')
                self.conn_productos.commit()

                self.conn_ventas = sqlite3.connect(DB_VENTAS)
                self.cursor_ventas = self.conn_ventas.cursor()
                self.cursor_ventas.execute('''CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    total REAL NOT NULL,
                    productos TEXT NOT NULL,
                    tipo_precio TEXT NOT NULL)''')
                self.conn_ventas.commit()
            except sqlite3.Error as e:
                self.mostrar_mensaje_error("Error", f"Error al conectar a la base de datos: {e}")
                self.destroy()

        def mostrar_mensaje_error(self, titulo, mensaje):
            dialog = ctk.CTkToplevel(self)
            dialog.title(titulo)
            width, height = 350, 200
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            dialog.resizable(False, False)
            dialog.grab_set()
            ctk.CTkLabel(dialog, text="❌", font=("Arial", 48)).pack(pady=(20, 10))
            ctk.CTkLabel(dialog, text=mensaje, font=("Arial", 14), wraplength=300).pack(pady=10)
            ctk.CTkButton(dialog, text="Aceptar", command=dialog.destroy, width=100).pack(pady=10)

        def mostrar_mensaje_advertencia(self, titulo, mensaje):
            dialog = ctk.CTkToplevel(self)
            dialog.title(titulo)
            width, height = 350, 200
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            dialog.resizable(False, False)
            dialog.grab_set()
            ctk.CTkLabel(dialog, text="⚠️", font=("Arial", 48)).pack(pady=(20, 10))
            ctk.CTkLabel(dialog, text=mensaje, font=("Arial", 14), wraplength=300).pack(pady=10)
            ctk.CTkButton(dialog, text="Aceptar", command=dialog.destroy, width=100).pack(pady=10)

        def mostrar_mensaje_info(self, titulo, mensaje):
            dialog = ctk.CTkToplevel(self)
            dialog.title(titulo)
            width, height = 350, 200
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            dialog.resizable(False, False)
            dialog.grab_set()
            ctk.CTkLabel(dialog, text="ℹ️", font=("Arial", 48)).pack(pady=(20, 10))
            ctk.CTkLabel(dialog, text=mensaje, font=("Arial", 14), wraplength=300).pack(pady=10)
            ctk.CTkButton(dialog, text="Aceptar", command=dialog.destroy, width=100).pack(pady=10)

        def crear_interfaz_principal(self):
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)
            self.crear_panel_productos()
            self.crear_panel_venta()
            self.crear_panel_controles()

        def crear_panel_productos(self):
            panel_productos = ctk.CTkFrame(self, width=350)
            panel_productos.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            frame_busqueda = ctk.CTkFrame(panel_productos)
            frame_busqueda.pack(fill="x", pady=5)
            ctk.CTkLabel(frame_busqueda, text="BUSCAR PRODUCTOS", font=("Arial", 14, "bold")).pack(pady=5)
            self.entry_busqueda = ctk.CTkEntry(frame_busqueda, placeholder_text="Nombre o descripción...")
            self.entry_busqueda.pack(fill="x", padx=5, pady=5)
            self.entry_busqueda.bind("<KeyRelease>", self.buscar_productos_en_tiempo_real)
            ctk.CTkButton(frame_busqueda, text="Buscar", command=self.buscar_productos).pack(pady=5)

            frame_tipo_precio = ctk.CTkFrame(panel_productos)
            frame_tipo_precio.pack(fill="x", pady=5)
            ctk.CTkLabel(frame_tipo_precio, text="TIPO DE VENTA:").pack(side="left", padx=5)
            ctk.CTkRadioButton(frame_tipo_precio, text="Venta 1", variable=self.tipo_precio_seleccionado, value="precio_1", command=self.actualizar_precios_venta).pack(side="left", padx=5)
            ctk.CTkRadioButton(frame_tipo_precio, text="Venta 2", variable=self.tipo_precio_seleccionado, value="precio_2", command=self.actualizar_precios_venta).pack(side="left", padx=5)
            ctk.CTkRadioButton(frame_tipo_precio, text="Venta 3", variable=self.tipo_precio_seleccionado, value="precio_3", command=self.actualizar_precios_venta).pack(side="left", padx=5)

            frame_lista = ctk.CTkFrame(panel_productos)
            frame_lista.pack(fill="both", expand=True, pady=10)
            self.tree_productos = CTkTreeview(frame_lista, columns=('nombre', 'precio_1', 'precio_2', 'precio_3', 'stock'), show='headings')
            self.tree_productos.heading('nombre', text='PRODUCTO')
            self.tree_productos.heading('precio_1', text='VENTA 1')
            self.tree_productos.heading('precio_2', text='VENTA 2')
            self.tree_productos.heading('precio_3', text='VENTA 3')
            self.tree_productos.heading('stock', text='STOCK')
            self.tree_productos.column('nombre', width=150)
            self.tree_productos.column('precio_1', width=80, anchor='e')
            self.tree_productos.column('precio_2', width=80, anchor='e')
            self.tree_productos.column('precio_3', width=80, anchor='e')
            self.tree_productos.column('stock', width=70, anchor='center')
            scrollbar = ctk.CTkScrollbar(frame_lista, command=self.tree_productos.yview)
            self.tree_productos.configure(yscrollcommand=scrollbar.set)
            self.tree_productos.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            self.tree_productos.bind("<Double-1>", self.agregar_a_venta)
            self.tree_productos.bind("<Return>", self.agregar_a_venta)

        def crear_panel_venta(self):
            panel_venta = ctk.CTkFrame(self)
            panel_venta.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
            panel_venta.grid_columnconfigure(0, weight=1)
            panel_venta.grid_rowconfigure(1, weight=1)
            ctk.CTkLabel(panel_venta, text="VENTA ACTUAL", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=10)
            self.lbl_tipo_precio = ctk.CTkLabel(panel_venta, text=f"Tipo de venta: Venta 1", font=("Arial", 12))
            self.lbl_tipo_precio.grid(row=0, column=0, sticky="e", padx=10)

            self.tree_venta = CTkTreeview(panel_venta, columns=('producto', 'precio', 'cantidad', 'subtotal', 'tipo_precio'), show='headings')
            self.tree_venta.heading('producto', text='PRODUCTO')
            self.tree_venta.heading('precio', text='PRECIO UNIT.')
            self.tree_venta.heading('cantidad', text='CANTIDAD')
            self.tree_venta.heading('subtotal', text='SUBTOTAL')
            self.tree_venta.heading('tipo_precio', text='TIPO VENTA')
            self.tree_venta.column('producto', width=200)
            self.tree_venta.column('precio', width=100, anchor='e')
            self.tree_venta.column('cantidad', width=80, anchor='center')
            self.tree_venta.column('subtotal', width=120, anchor='e')
            self.tree_venta.column('tipo_precio', width=100, anchor='center')
            scrollbar = ctk.CTkScrollbar(panel_venta, command=self.tree_venta.yview)
            self.tree_venta.configure(yscrollcommand=scrollbar.set)
            self.tree_venta.grid(row=1, column=0, sticky="nsew")
            scrollbar.grid(row=1, column=1, sticky="ns")

            self.lbl_total = ctk.CTkLabel(panel_venta, text="TOTAL: $0.00", font=("Arial", 14, "bold"))
            self.lbl_total.grid(row=2, column=0, pady=10, sticky="e")

        def crear_panel_controles(self):
            panel_controles = ctk.CTkFrame(self)
            panel_controles.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
            ctk.CTkButton(panel_controles, text="Eliminar Producto", command=self.eliminar_producto_venta, fg_color="#d9534f").pack(side="left", padx=5)
            ctk.CTkButton(panel_controles, text="Limpiar Venta", command=self.limpiar_venta).pack(side="left", padx=5)
            ctk.CTkButton(panel_controles, text="Cerrar Sesión", command=self.logout, fg_color="#e74c3c").pack(side="left", padx=5)
            ctk.CTkButton(panel_controles, text="Finalizar Venta", command=self.finalizar_venta, fg_color="#5cb85c").pack(side="right", padx=5)
        
        def buscar_productos_en_tiempo_real(self, event=None):
            texto = self.entry_busqueda.get().strip()
            self.cargar_productos(filtro=texto if texto else None)

        def cargar_productos(self, filtro=None):
            self.tree_productos.delete(*self.tree_productos.get_children())
            try:
                if filtro:
                    self.cursor_productos.execute("""SELECT id, nombre, precio_1, precio_2, precio_3, stock
                                                     FROM productos
                                                     WHERE nombre LIKE ? OR descripcion LIKE ?
                                                     ORDER BY nombre""", (f'%{filtro}%', f'%{filtro}%'))
                else:
                    self.cursor_productos.execute("SELECT id, nombre, precio_1, precio_2, precio_3, stock FROM productos ORDER BY nombre")
                for producto in self.cursor_productos.fetchall():
                    self.tree_productos.insert('', 'end', values=(
                        producto[1],
                        f"${round(producto[2], 2):.2f}",
                        f"${round(producto[3], 2):.2f}",
                        f"${round(producto[4], 2):.2f}",
                        producto[5]
                    ), iid=producto[0])
            except sqlite3.Error as e:
                self.mostrar_mensaje_error("Error", f"Error al cargar productos: {e}")

        def buscar_productos(self):
            filtro = self.entry_busqueda.get().strip()
            self.cargar_productos(filtro if filtro else None)

        def agregar_a_venta(self, event=None):
            item = self.tree_productos.focus()
            if not item:
                return
            valores = self.tree_productos.item(item, 'values')
            nombre = valores[0]
            tipo_precio = self.tipo_precio_seleccionado.get()
            if tipo_precio == "precio_1":
                        precio = round(float(valores[1].replace('$', '')), 2)
            elif tipo_precio == "precio_2":
                precio = round(float(valores[2].replace('$', '')), 2)
            else:
                precio = round(float(valores[3].replace('$', '')), 2)

            stock = int(valores[4])
            if stock <= 0:
                self.mostrar_mensaje_advertencia("Stock", "No hay stock disponible")
                return

            for item_venta in self.tree_venta.get_children():
                valores_venta = self.tree_venta.item(item_venta, 'values')
                if valores_venta[0] == nombre and valores_venta[4] == tipo_precio.replace('precio_', 'Venta '):
                    nueva_cantidad = int(valores_venta[2]) + 1
                    if nueva_cantidad >= stock:
                        self.mostrar_mensaje_advertencia("Stock", "No hay suficiente stock")
                        return
                    nuevo_subtotal = round(nueva_cantidad * precio, 2)
                    self.tree_venta.item(item_venta, values=(
                        nombre, f"${precio:.2f}", nueva_cantidad, f"${nuevo_subtotal:.2f}",
                        tipo_precio.replace('precio_', 'Venta ')))
                    self.total_venta += precio
                    self.actualizar_total()
                    return

            subtotal = round(precio, 2)
            self.tree_venta.insert('', 'end', values=(
                nombre, f"${precio:.2f}", 1, f"${subtotal:.2f}",
                tipo_precio.replace('precio_', 'Venta ')), tags=(item,))
            self.total_venta += precio
            self.actualizar_total()
            self.lbl_tipo_precio.configure(text=f"Tipo de venta: {tipo_precio.replace('precio_', 'Venta ')}")

        def actualizar_precios_venta(self, *args):
            tipo_precio = self.tipo_precio_seleccionado.get()
            self.lbl_tipo_precio.configure(text=f"Tipo de venta: {tipo_precio.replace('precio_', 'Venta ')}")
            if not self.tree_venta.get_children():
                return
            self.total_venta = 0.0
            for item in self.tree_venta.get_children():
                id_producto = self.tree_venta.item(item, 'tags')[0]
                producto = self.tree_productos.item(id_producto)
                if not producto:
                    continue
                valores_producto = producto['values']
                nombre = valores_producto[0]
                cantidad = int(self.tree_venta.item(item, 'values')[2])
                if tipo_precio == "precio_1":
                    nuevo_precio = round(float(valores_producto[1].replace('$', '')), 2)
                elif tipo_precio == "precio_2":
                    nuevo_precio = round(float(valores_producto[2].replace('$', '')), 2)
                else:
                    nuevo_precio = round(float(valores_producto[3].replace('$', '')), 2)
                nuevo_subtotal = round(cantidad * nuevo_precio, 2)
                self.tree_venta.item(item, values=(
                    nombre, f"${nuevo_precio:.2f}", cantidad, f"${nuevo_subtotal:.2f}",
                    tipo_precio.replace('precio_', 'Venta ')))
                self.total_venta += nuevo_subtotal
            self.actualizar_total()

        def eliminar_producto_venta(self):
            item = self.tree_venta.focus()
            if not item:
                return
            valores = self.tree_venta.item(item, 'values')
            subtotal = float(valores[3].replace('$', ''))
            self.tree_venta.delete(item)
            self.total_venta -= subtotal
            self.actualizar_total()

        def limpiar_venta(self):
            self.tree_venta.delete(*self.tree_venta.get_children())
            self.total_venta = 0.0
            self.actualizar_total()

        def finalizar_venta(self):
            if not self.tree_venta.get_children():
                self.mostrar_mensaje_advertencia("Venta vacía", "No hay productos en la venta")
                return
            self.ventana_pago()

        def ventana_pago(self):
            try:
                self.dialog = ctk.CTkToplevel(self)
                self.dialog.title("Finalizar Venta")
                width, height = 350, 300
                screen_width = self.dialog.winfo_screenwidth()
                screen_height = self.dialog.winfo_screenheight()
                x = (screen_width // 2) - (width // 2)
                y = (screen_height // 2) - (height // 2)
                self.dialog.geometry(f"{width}x{height}+{x}+{y}")
                self.dialog.grab_set()
                self.dialog.focus()
                self.monto_recibido = self.total_venta
                ctk.CTkLabel(self.dialog, text=f"Total a cobrar: ${self.total_venta:.2f}", font=("Arial", 14, "bold")).pack(pady=10)
                frame_monto = ctk.CTkFrame(self.dialog)
                frame_monto.pack(pady=5, padx=10, fill="x")
                ctk.CTkLabel(frame_monto, text="Monto recibido:").pack(anchor="w")
                self.entry_monto_recibido = ctk.CTkEntry(frame_monto)
                self.entry_monto_recibido.pack(fill="x")
                self.entry_monto_recibido.focus()
                self.entry_monto_recibido.bind("<KeyRelease>", self.actualizar_cambio)
                frame_cambio = ctk.CTkFrame(self.dialog)
                frame_cambio.pack(pady=5, padx=10, fill="x")
                ctk.CTkLabel(frame_cambio, text="Cambio:").pack(anchor="w")
                self.entry_cambio = ctk.CTkEntry(frame_cambio, state="readonly")
                self.entry_cambio.pack(fill="x")
                ctk.CTkButton(self.dialog, text="Confirmar Cobro", command=self.confirmar_pago).pack(pady=15)
            except Exception as e:
                self.mostrar_mensaje_error("Error", f"No se pudo abrir la ventana de pago: {e}")

        def actualizar_cambio(self, event=None):
            try:
                valor = self.entry_monto_recibido.get()
                recibido = float(valor) if valor else self.total_venta
                cambio = round(recibido - self.total_venta, 2)
                self.entry_cambio.configure(state="normal")
                self.entry_cambio.delete(0, "end")
                self.entry_cambio.insert(0, f"${cambio:.2f}" if cambio >= 0 else "")
                self.entry_cambio.configure(state="readonly")
            except ValueError:
                self.entry_cambio.configure(state="normal")
                self.entry_cambio.delete(0, "end")
                self.entry_cambio.configure(state="readonly")
            except Exception:
                pass

        def confirmar_pago(self):
            try:
                recibido = float(self.entry_monto_recibido.get())
                if recibido < self.total_venta:
                    self.mostrar_mensaje_advertencia("Monto insuficiente", "El monto recibido es menor al total.")
                    return
            except ValueError:
                self.mostrar_mensaje_advertencia("Entrada inválida", "Ingrese un monto válido.")
                return
            cambio = round(recibido - self.total_venta, 2)
            self.monto_recibido = recibido
            self.cambio_venta = cambio
            self.dialog.destroy()
            self.preguntar_factura(recibido, cambio)
        def preguntar_factura(self, recibido, cambio):
            dialog_factura = ctk.CTkToplevel(self)
            dialog_factura.title("Factura")
            width, height = 300, 150
            screen_width = dialog_factura.winfo_screenwidth()
            screen_height = dialog_factura.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            dialog_factura.geometry(f"{width}x{height}+{x}+{y}")
            dialog_factura.grab_set()
            ctk.CTkLabel(dialog_factura, text="¿Desea generar factura?", font=("Arial", 14)).pack(pady=(20, 15))
            btn_frame = ctk.CTkFrame(dialog_factura, fg_color="transparent")
            btn_frame.pack(pady=10)

            def procesar_con_factura():
                try:
                    productos = []
                    for item in self.tree_venta.get_children():
                        valores = self.tree_venta.item(item)['values']
                        productos.append({
                            'nombre': str(valores[0]),
                            'precio': round(float(valores[1].replace('$', '')), 2),
                            'cantidad': int(valores[2]),
                            'subtotal': round(float(valores[3].replace('$', '')), 2),
                            'tipo_precio': str(valores[4])
                        })
                    total = self.total_venta
                    numero_factura = f"TF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    dialog_factura.destroy()
                    self.pedir_datos_factura(productos, total, recibido, cambio, numero_factura)
                except Exception as e:
                    self.mostrar_mensaje_error("Error", f"Error al procesar factura: {e}")
                    self.registrar_venta(con_factura=False)

            def procesar_sin_factura():
                dialog_factura.destroy()
                self.registrar_venta(con_factura=False)

            ctk.CTkButton(btn_frame, text="Sí", command=procesar_con_factura, fg_color="#2ecc71", width=100).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="No", command=procesar_sin_factura, fg_color="#e74c3c", width=100).pack(side="left", padx=10)
                
        def pedir_datos_factura(self, productos, total, recibido, cambio, numero_factura):
            dialog_datos = ctk.CTkToplevel(self)
            dialog_datos.title("Datos de Factura")
            width, height = 400, 300
            screen_width = dialog_datos.winfo_screenwidth()
            screen_height = dialog_datos.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            dialog_datos.geometry(f"{width}x{height}+{x}+{y}")
            dialog_datos.resizable(False, False)
            dialog_datos.grab_set()
            cliente_tipo = ctk.StringVar(value="final")

            def toggle_inputs():
                state = "disabled" if cliente_tipo.get() == "final" else "normal"
                entry_ruc.configure(state=state)
                entry_nombre.configure(state=state)

            ctk.CTkLabel(dialog_datos, text="¿A quién se factura?", font=("Arial", 14, "bold")).pack(pady=10)
            ctk.CTkRadioButton(dialog_datos, text="Consumidor Final", variable=cliente_tipo, value="final", command=toggle_inputs).pack(anchor="w", padx=20)
            ctk.CTkRadioButton(dialog_datos, text="Con RUC/Cédula", variable=cliente_tipo, value="ruc", command=toggle_inputs).pack(anchor="w", padx=20)

            frame_inputs = ctk.CTkFrame(dialog_datos)
            frame_inputs.pack(pady=10, padx=20, fill="x")
            ctk.CTkLabel(frame_inputs, text="RUC / Cédula:").pack(anchor="w")
            entry_ruc = ctk.CTkEntry(frame_inputs, state="disabled")
            entry_ruc.pack(fill="x")
            ctk.CTkLabel(frame_inputs, text="Nombre del Cliente:").pack(anchor="w")
            entry_nombre = ctk.CTkEntry(frame_inputs, state="disabled")
            entry_nombre.pack(fill="x")
            toggle_inputs()

            def confirmar_datos():
                if cliente_tipo.get() == "ruc":
                    ruc = entry_ruc.get().strip()
                    nombre = entry_nombre.get().strip()
                    if not ruc or not nombre:
                        self.mostrar_mensaje_advertencia("Datos incompletos", "Debe ingresar RUC y nombre del cliente.")
                        return
                else:
                    ruc = None
                    nombre = "Consumidor Final"
                dialog_datos.destroy()
                pdf_path = self.generar_factura_pdf(productos, total, recibido, cambio, numero_factura, cliente_ruc=ruc, cliente_nombre=nombre)
                if pdf_path:
                    try:
                        import webbrowser
                        webbrowser.open(os.path.abspath(pdf_path))
                    except Exception:
                        pass
                self.registrar_venta(con_factura=True)

            btn_frame = ctk.CTkFrame(dialog_datos, fg_color="transparent")
            btn_frame.pack(pady=20)
            ctk.CTkButton(btn_frame, text="Cancelar", command=dialog_datos.destroy, fg_color="#e74c3c").pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="OK", command=confirmar_datos, fg_color="#2ecc71").pack(side="left", padx=10)

        def generar_factura_pdf(self, productos, total, recibido, cambio, numero_factura, cliente_ruc=None, cliente_nombre=None):
            try:
                # Obtener el escritorio del usuario de forma multiplataforma
                from pathlib import Path
                desktop = str(Path.home() / "Desktop")
                facturas_dir = os.path.join(desktop, "facturas")
                os.makedirs(facturas_dir, exist_ok=True)
                fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(facturas_dir, f"factura_{numero_factura}_{fecha_hora}.pdf")
                doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
                styles = getSampleStyleSheet()
                story = []
                # --- Leer datos de la empresa ---
                empresa_path = EMPRESA
                try:
                    with open(empresa_path) as f:
                        emp = json.load(f)
                except Exception:
                    emp = {
                        "nombre": "NOMBRE DE LA EMPRESA",
                        "direccion": "Tu dirección aquí",
                        "telefono": "TELEFONO",
                        "email": "sftucan@ejemplo.com"
                    }
                num_fact = siguiente_numero_factura()
                story.append(Paragraph(f"<b>{emp['nombre']}</b>", styles["Title"]))
                story.append(Paragraph(f"Direccion: {emp['direccion']}", styles["Normal"]))
                story.append(Paragraph(f"Tel: {emp['telefono']}", styles["Normal"]))
                story.append(Paragraph(f"Email: {emp['email']}", styles["Normal"]))
                story.append(Spacer(1, 12))

                story.append(Paragraph(f"<b>Factura #{num_fact}</b>", styles["Heading2"]))
                story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles["Normal"]))
                story.append(Paragraph(f"Tipo de Venta: {self.tipo_precio_seleccionado.get().replace('precio_','Venta ')}", styles["Normal"]))
                if cliente_ruc:
                    story.append(Paragraph(f"Cliente: {cliente_nombre}", styles["Normal"]))
                    story.append(Paragraph(f"RUC/Cédula: {cliente_ruc}", styles["Normal"]))
                else:
                    story.append(Paragraph("Cliente: Consumidor Final", styles["Normal"]))
                story.append(Spacer(1, 12))

                story.append(Paragraph("<b>DETALLE DE PRODUCTOS:</b>", styles["Heading3"]))
                # Elimina la columna de IVA y Precio IVA
                data = [["Producto", "Cantidad", "Precio Unit.", "Subtotal"]]
                for p in productos:
                    subtotal = float(p['subtotal'])
                    data.append([
                        p['nombre'], str(p['cantidad']), f"${p['precio']:.2f}", f"${subtotal:.2f}"
                    ])

                from reportlab.platypus import Table, TableStyle
                table = Table(data, colWidths=[160, 50, 70, 80])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                story.append(table)
                story.append(Spacer(1, 12))

                total_style = ParagraphStyle('TotalStyle', parent=styles['Normal'], fontSize=12, alignment=2, spaceAfter=6)
                story.append(Paragraph(f"<b>TOTAL: ${total:.2f}</b>", total_style))
                story.append(Paragraph(f"<b>RECIBIDO: ${recibido:.2f}</b>", total_style))
                story.append(Paragraph(f"<b>CAMBIO: ${cambio:.2f}</b>", total_style))

                story.append(Spacer(1, 24))
                story.append(Paragraph("Gracias por su compra", styles["Italic"]))
                story.append(Paragraph("Este documento sirve como comprobante de pago", styles["Italic"]))

                doc.build(story)
                return filename
            except Exception as e:
                ErrorDialog(None,f"Error al generar PDF: {e}")
                return None

        def registrar_venta(self, con_factura=False):
            try:
                productos = []
                for item in self.tree_venta.get_children():
                    valores = self.tree_venta.item(item, 'values')
                    productos.append({
                        'nombre': valores[0],
                        'cantidad': int(valores[2]),
                        'precio': round(float(valores[1].replace('$', '')), 2),
                        'subtotal': round(float(valores[3].replace('$', '')), 2)
                    })
                for producto in productos:
                    self.cursor_productos.execute("UPDATE productos SET stock = stock - ? WHERE nombre = ?", (producto['cantidad'], producto['nombre']))
                productos_str = "|".join([f"{p['nombre']} ({p['cantidad']} x ${p['precio']:.2f} = ${p['subtotal']:.2f})" for p in productos])
                fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tipo_precio = self.tipo_precio_seleccionado.get().replace('precio_', 'Venta ')
                self.cursor_ventas.execute("INSERT INTO ventas (fecha, total, productos, tipo_precio) VALUES (?, ?, ?, ?)",
                                           (fecha_hora_actual, self.total_venta, productos_str, tipo_precio))
                self.conn_productos.commit()
                self.conn_ventas.commit()
                mensaje = "Venta registrada correctamente"
                if con_factura:
                    num_factura = siguiente_numero_factura()
                    mensaje += f"\nFactura generada con número: {num_factura}"
                self.mostrar_mensaje_info("Éxito", mensaje)
                self.limpiar_venta()
                self.cargar_productos()
            except sqlite3.Error as e:
                self.mostrar_mensaje_error("Error", f"No se pudo registrar la venta: {e}")
                self.conn_productos.rollback()
                self.conn_ventas.rollback()

        def actualizar_total(self):
            self.lbl_total.configure(text=f"TOTAL: ${self.total_venta:.2f}")

    return SistemaVentasTucan()

