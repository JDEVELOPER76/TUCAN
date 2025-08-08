import customtkinter as ctk
import json
import os
from gestion import main_simple
from historial_ventas import HistorialVentasApp
from asistentes.cuadro_mensaje import ErrorDialog , SuccessDialog , InfoDialog
from asistentes.iconos import iconos
from ingreso_mercaderia import run_ingreso_mercaderia

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
JSON_DIR = os.path.join(BASE_DIR, "JSON")
os.makedirs(JSON_DIR, exist_ok=True)
EMPRESA = os.path.join(JSON_DIR,"empresa.json")
ADMIN = os.path.join(JSON_DIR, "admin.json")
USUARIOS = os.path.join(JSON_DIR, "usuarios.json")

def initialize_admin_panel():
    root = ctk.CTk()
    base_dir_admin = os.path.dirname(__file__)
    employees_file = USUARIOS
    admins_file = ADMIN

    initialize_files(employees_file, admins_file)

    root.title("Administración")
    root._state_before_windows_set_titlebar_color = "zoomed"
    icon_path = os.path.join(base_dir_admin, "imagenes", "logo.ico")
    try:
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        ErrorDialog(None, f"Advertencia: No se pudo cargar el icono: {e}", iconos("imagenes", "error.ico"))
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    main_frame = ctk.CTkFrame(root, fg_color="transparent")
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    header_frame.pack(fill="x", pady=(0, 20))

    title_label = ctk.CTkLabel(
        header_frame,
        text="Panel de Administración",
        font=("Roboto", 24, "bold")
    )
    title_label.pack(side="left", pady=10)

    logout_button = ctk.CTkButton(
        header_frame,
        text="🚪 Cerrar Sesión",
        command=lambda: logout_admin(root),
        width=150,
        height=38,
        fg_color="#e74c3c",
        hover_color="#c0392b",
        font=("Roboto", 13, "bold"),
        corner_radius=8
    )
    logout_button.pack(side="right", pady=10, padx=15)

    main_container = ctk.CTkFrame(main_frame)
    main_container.pack(fill="both", expand=True)
    main_container.grid_columnconfigure(1, weight=1)
    main_container.grid_rowconfigure(0, weight=1)

    sidebar = ctk.CTkFrame(main_container, width=200, corner_radius=0, fg_color="#1a1a2e")
    sidebar.grid(row=0, column=0, sticky="nsew")
    sidebar.grid_propagate(False)

    menu_title = ctk.CTkLabel(
        sidebar,
        text="MENÚ PRINCIPAL",
        font=("Roboto", 16, "bold"),
        text_color="#4CAF50"
    )
    menu_title.pack(pady=(20, 25))

    content_frame = ctk.CTkFrame(main_container)
    content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    personal_frame = ctk.CTkFrame(content_frame)
    inventory_frame = ctk.CTkFrame(content_frame)
    sales_frame = ctk.CTkFrame(content_frame)
    ingreso_frame = ctk.CTkFrame(content_frame)
    empresa_frame = ctk.CTkFrame(content_frame)
    config_frame = ctk.CTkFrame(content_frame)

    frames = {
        "personal": personal_frame,
        "inventory": inventory_frame,
        "sales": sales_frame,
        "ingreso": ingreso_frame,
        "empresa": empresa_frame,
        "config": config_frame
    }

    def show_frame(frame_name):
        for f in frames.values():
            f.pack_forget()
        frames[frame_name].pack(fill="both", expand=True)

    menu_button_style = {
        "corner_radius": 0,
        "height": 40,
        "anchor": "w",
        "fg_color": "transparent",
        "text_color": "white",
        "hover_color": "#2d2d42",
        "font": ("Roboto", 13)
    }

    personal_btn = ctk.CTkButton(sidebar, text=" 👥  Personal", command=lambda: show_frame("personal"), **menu_button_style)
    personal_btn.pack(fill="x", pady=(0, 5))

    inventory_btn = ctk.CTkButton(sidebar, text=" 📦  Inventario", command=lambda: show_frame("inventory"), **menu_button_style)
    inventory_btn.pack(fill="x", pady=5)

    sales_btn = ctk.CTkButton(sidebar, text=" 💰  Ventas", command=lambda: show_frame("sales"), **menu_button_style)
    sales_btn.pack(fill="x", pady=5)

    ingreso_btn = ctk.CTkButton(sidebar, text="📥 Ingreso de mercadería", command=lambda: show_frame("ingreso"), **menu_button_style)
    ingreso_btn.pack(fill="x", pady=5)

    empresa_btn = ctk.CTkButton(sidebar, text="🏢  Empresa", command=lambda: show_frame("empresa"), **menu_button_style)
    empresa_btn.pack(fill="x", pady=5)

    config_btn = ctk.CTkButton(sidebar, text=" ⚙️  Configuración", command=lambda: show_frame("config"), **menu_button_style)
    config_btn.pack(fill="x", pady=5)

    separator = ctk.CTkFrame(sidebar, height=1, fg_color="gray")
    separator.pack(fill="x", pady=15, padx=20)

    version_label = ctk.CTkLabel(sidebar, text="v1.3", font=("Roboto", 15), text_color="gray")
    version_label.pack(pady=(5, 15))

    employees_listbox, admins_listbox = create_personal_tab(personal_frame, employees_file, admins_file)
    create_simplified_tabs(frames)
    create_empresa_tab(frames["empresa"])
    create_ingreso_tab(frames["ingreso"])

    show_frame("personal")
    load_data(employees_file, admins_file, employees_listbox, admins_listbox)

    return root

def create_ingreso_tab(parent):
    parent.grid_columnconfigure(0, weight=1)

    title = ctk.CTkLabel(
        parent,
        text="Ingreso de Mercadería",
        font=("Roboto", 22, "bold"),
        text_color="#16a085"
    )
    title.pack(pady=(20, 10))

    form = ctk.CTkFrame(parent, corner_radius=10)
    form.pack(padx=40, pady=20, fill="both", expand=True)

    ctk.CTkLabel(
        form,
        text="Aqui podras sumar el inventario actual de tus productos , sin necesidad de sumar \nSi quieres agregar o quitar productos ve a Inventario",
        font=("Roboto", 15),
        wraplength=500,
        justify="left"
    ).pack(padx=20, pady=(30, 20))

    ctk.CTkButton(
        form,
        text="💾 Abrir Ingreso de Mercaderia",
        command=lambda: run_ingreso_mercaderia(),
        fg_color="#16a085",
        hover_color="#138d75",
        height=40,
        font=("Roboto", 13, "bold"),
    ).pack(pady=30)

def create_empresa_tab(parent):
    parent.grid_columnconfigure(0, weight=1)

    title = ctk.CTkLabel(
        parent,
        text="Datos de la Empresa",
        font=("Roboto", 22, "bold"),
        text_color="#e67e22"
    )
    title.pack(pady=(20, 10))

    form = ctk.CTkFrame(parent, corner_radius=10)
    form.pack(padx=40, pady=20, fill="both", expand=True)

    empresa_path = EMPRESA
    if not os.path.exists(empresa_path):
        with open(empresa_path, "w") as f:
            json.dump(
                {
                    "nombre": "NOMBRE DE LA EMPRESA",
                    "direccion": "Tu dirección aquí",
                    "telefono": "TELEFONO",
                    "email": "sftucan@ejemplo.com"
                },
                f,
                indent=4,
            )

    with open(empresa_path) as f:
        data = json.load(f)

    entries = {}
    labels = ["Nombre", "Dirección", "Teléfono", "Correo"]
    keys = ["nombre", "direccion", "telefono", "email"]

    for label, key in zip(labels, keys):
        ctk.CTkLabel(form, text=f"{label}:", font=("Roboto", 13, "bold")).pack(
            anchor="w", padx=20, pady=(15, 0)
        )
        entry = ctk.CTkEntry(form, height=35, font=("Roboto", 12))
        entry.insert(0, data.get(key, ""))
        entry.pack(fill="x", padx=20)
        entries[key] = entry

    def guardar():
        try:
            new_data = {k: v.get().strip() for k, v in entries.items()}
            with open(empresa_path, "w") as f:
                json.dump(new_data, f, indent=4)
            SuccessDialog(None, "Datos guardados correctamente", iconos("imagenes", "exito.ico"))
        except Exception as e:
            ErrorDialog(None, str(e), iconos("imagenes", "error.ico"))

    ctk.CTkButton(
        form,
        text="💾 Guardar cambios",
        command=guardar,
        fg_color="#2ecc71",
        hover_color="#27ae60",
        height=40,
        font=("Roboto", 13, "bold"),
    ).pack(pady=30)


def initialize_files(employees_file, admins_file):
    if not os.path.exists(employees_file):
        with open(employees_file, 'w') as f:
            json.dump([], f)

    if not os.path.exists(admins_file):
        with open(admins_file, 'w') as f:
            json.dump([], f)


def load_data(employees_file, admins_file, employees_listbox, admins_listbox):
    load_employees(employees_file, employees_listbox)
    load_admins(admins_file, admins_listbox)


def create_simplified_tabs(frames):
    # Frame de Inventario
    inventory_frame = frames["inventory"]

    # Marco de información y descripción
    info_frame = ctk.CTkFrame(inventory_frame)
    info_frame.pack(pady=20, padx=20, fill="x")

    ctk.CTkLabel(
        info_frame,
        text="Gestión de Bodega",
        font=("Roboto", 22, "bold"),
        text_color="#4CAF50"
    ).pack(pady=(10, 5))

    ctk.CTkLabel(
        info_frame,
        text="Aquí puedes gestionar el inventario de productos de la bodega. "
             "Podrás registrar, actualizar, buscar y controlar el stock de todos los productos.",
        font=("Roboto", 16),
        wraplength=600,
        justify="left"
    ).pack(pady=(0, 15))

    # Añadir imagen/icono ilustrativo (simulado con un marco)
    icon_frame = ctk.CTkFrame(inventory_frame, width=100, height=100, fg_color="#4CAF50", corner_radius=50)
    icon_frame.pack(pady=(10, 20))

    ctk.CTkLabel(
        icon_frame,
        text="📦",
        font=("", 40)
    ).place(relx=0.5, rely=0.5, anchor="center")

    # Botón para abrir el gestor de inventario
    btn_frame = ctk.CTkFrame(inventory_frame, fg_color="transparent")
    btn_frame.pack(pady=20)

    ctk.CTkButton(
        btn_frame,
        text="Abrir Gestor de Inventario",
        command=lambda: main_simple(),
        width=250,
        height=50,
        font=("Roboto", 15, "bold"),
        fg_color="#4CAF50",
        hover_color="#388E3C"
    ).pack(pady=10)

    # Frame de Ventas
    sales_frame = frames["sales"]

    sales_header = ctk.CTkFrame(sales_frame, fg_color="transparent")
    sales_header.pack(fill="x", pady=(20, 30))

    ctk.CTkLabel(
        sales_header,
        text="Historial de Ventas",
        font=("Roboto", 22, "bold"),
        text_color="#3498db"
    ).pack(pady=(10, 5))

    # Crear dos columnas para el contenido
    sales_content = ctk.CTkFrame(sales_frame, fg_color="transparent")
    sales_content.pack(fill="both", expand=True, padx=20)
    sales_content.grid_columnconfigure(0, weight=1)
    sales_content.grid_columnconfigure(1, weight=1)

    # Columna izquierda: Descripción
    left_col = ctk.CTkFrame(sales_content, fg_color="#1e272e", corner_radius=10)
    left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    ctk.CTkLabel(
        left_col,
        text="Sistema de Registro",
        font=("Roboto", 18, "bold"),
        text_color="#3498db"
    ).pack(pady=(20, 10))

    ctk.CTkLabel(
        left_col,
        text="• Registro completo de todas las transacciones\n• Información detallada con fechas y horas\n• Filtrado avanzado por período\n• Exportación a formatos diversos",
        font=("Roboto", 14),
        justify="left",
        wraplength=300
    ).pack(pady=15, padx=20)

    # Columna derecha: Botón y estadísticas
    right_col = ctk.CTkFrame(sales_content, fg_color="#1e272e", corner_radius=10)
    right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    ctk.CTkLabel(
        right_col,
        text="💰",
        font=("", 40)
    ).pack(pady=(30, 10))

    ctk.CTkButton(
        right_col,
        text="Ver Historial Completo",
        command=lambda: HistorialVentasApp().mainloop(),
        width=220,
        height=50,
        font=("Roboto", 15, "bold"),
        fg_color="#3498db",
        hover_color="#2980b9"
    ).pack(pady=20)

    # Frame de Configuración
    config_frame = frames["config"]

    config_header = ctk.CTkFrame(config_frame, fg_color="transparent")
    config_header.pack(fill="x", pady=(20, 30))

    ctk.CTkLabel(
        config_header,
        text="Configuración del Sistema",
        font=("Roboto", 22, "bold"),
        text_color="#9b59b6"
    ).pack(pady=(10, 5))

    # Contenedor principal de configuraciones
    config_container = ctk.CTkFrame(config_frame, fg_color="transparent")
    config_container.pack(fill="both", expand=True, padx=20)

    # Crear tarjetas para diferentes configuraciones
    # Tarjeta 1: Apariencia
    appearance_card = ctk.CTkFrame(config_container, fg_color="#1e272e", corner_radius=10)
    appearance_card.pack(fill="x", pady=10, ipady=10)

    ctk.CTkLabel(
        appearance_card,
        text="🎨 Apariencia",
        font=("Roboto", 16, "bold"),
        text_color="#9b59b6"
    ).pack(pady=(10, 5), padx=15, anchor="w")

    theme_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
    theme_frame.pack(fill="x", padx=15)

    ctk.CTkLabel(
        theme_frame,
        text="Tema:",
        font=("Roboto", 12)
    ).pack(side="left", padx=(0, 10))

    theme_var = ctk.StringVar(value="Sistema")
    theme_menu = ctk.CTkOptionMenu(
        theme_frame,
        values=["Sistema"],
        variable=theme_var,
        width=120
    )
    theme_menu.pack(side="left")

    # Tarjeta 2: Sistema
    system_card = ctk.CTkFrame(config_container, fg_color="#1e272e", corner_radius=10)
    system_card.pack(fill="x", pady=10, ipady=10)

    ctk.CTkLabel(
        system_card,
        text="⚙️ Sistema",
        font=("Roboto", 16, "bold"),
        text_color="#9b59b6"
    ).pack(pady=(10, 5), padx=15, anchor="w")

    # Características en desarrollo
    features_frame = ctk.CTkFrame(system_card, fg_color="transparent")
    features_frame.pack(fill="x", padx=15, pady=(5, 10))

    ctk.CTkLabel(
        features_frame,
        text="Próximas actualizaciones:",
        font=("Roboto", 12, "bold")
    ).pack(anchor="w")

    features = [
        "-Proximamente"
    ]

    for feature in features:
        ctk.CTkLabel(
            features_frame,
            text=feature,
            font=("Roboto", 12),
            anchor="w"
        ).pack(anchor="w", padx=(15, 0), pady=2)

    # Tarjeta 3: Información
    info_card = ctk.CTkFrame(config_container, fg_color="#1e272e", corner_radius=10)
    info_card.pack(fill="x", pady=10, ipady=10)

    ctk.CTkLabel(
        info_card,
        text="ℹ️ Acerca del Sistema",
        font=("Roboto", 16, "bold"),
        text_color="#9b59b6"
    ).pack(pady=(10, 5), padx=15, anchor="w")

    ctk.CTkLabel(
        info_card,
        text="Siste libre y gratis\n© 2024 Todos los derechos reservados",
        font=("Roboto", 12),
        justify="left"
    ).pack(padx=15, anchor="w")

#crea los .json
def initialize_files(employees_file, admins_file):
    if not os.path.exists(employees_file):
        with open(employees_file, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(admins_file):
        with open(admins_file, 'w') as f:
            json.dump([], f)
#Cargar datos de empleados y administradores
def load_data(employees_file, admins_file, employees_listbox, admins_listbox):

    load_employees(employees_file, employees_listbox)
    load_admins(admins_file, admins_listbox)

#Crea la interfaz de gestión de personal
def create_personal_tab(tab, employees_file, admins_file):
    header = ctk.CTkFrame(tab, fg_color="transparent")
    header.pack(fill="x", pady=(10, 25))
    
    ctk.CTkLabel(
        header, 
        text="Gestión de Personal",
        font=("Roboto", 22, "bold"),
        text_color="#ff9800"  # Color naranja para personal
    ).pack(side="left")
    
    # Contenedor principal con grid para las dos columnas
    main_content = ctk.CTkFrame(tab, fg_color="transparent")
    main_content.pack(fill="both", expand=True)
    main_content.grid_columnconfigure(0, weight=1)
    main_content.grid_columnconfigure(1, weight=1)
    main_content.grid_rowconfigure(0, weight=1)
    
    # Panel de empleados con diseño mejorado
    emp_frame = ctk.CTkFrame(main_content, corner_radius=10, fg_color="#1e272e")
    emp_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    emp_header = ctk.CTkFrame(emp_frame, fg_color="transparent")
    emp_header.pack(fill="x", pady=(15, 10), padx=15)
    
    ctk.CTkLabel(
        emp_header, 
        text="👥 Empleados",
        font=("Roboto", 18, "bold"),
        text_color="#ff9800"
    ).pack(side="left")
    
    # Panel de botones de empleados con diseño mejorado
    emp_buttons_frame = ctk.CTkFrame(emp_frame, fg_color="transparent")
    emp_buttons_frame.pack(fill="x", padx=15, pady=(15,10))

    add_emp_btn = ctk.CTkButton(
        emp_buttons_frame,
        text="➕ Nuevo Empleado",
        command=lambda: add_employee_dialog(employees_file, tab.winfo_toplevel(), employees_listbox),
        fg_color="#2ecc71",
        hover_color="#27ae60",
        font=("Roboto", 13, "bold"),
        corner_radius=8,
        height=40,
        width=160
    )
    add_emp_btn.pack(side="left", padx=5)

    remove_emp_btn = ctk.CTkButton(
        emp_buttons_frame,
        text="🗑️ Eliminar Empleado",
        command=lambda: remove_employee_dialog(employees_file, tab.winfo_toplevel(), employees_listbox),
        fg_color="#e74c3c",
        hover_color="#c0392b",
        font=("Roboto", 13, "bold"),
        corner_radius=8,
        height=40,
        width=160
    )
    remove_emp_btn.pack(side="left", padx=5)
    
    # Lista de empleados con marco mejorado
    list_container = ctk.CTkFrame(emp_frame, fg_color="#2c3e50", corner_radius=5)
    list_container.pack(pady=10, padx=15, fill="both", expand=True)
    
    list_header = ctk.CTkFrame(list_container, fg_color="transparent")
    list_header.pack(fill="x", padx=10, pady=(10, 0))
    
    ctk.CTkLabel(
        list_header,
        text="Lista de Empleados Registrados",
        font=("Roboto", 14, "bold"),
        text_color="#ff9800"
    ).pack(side="left")
    
    employees_listbox = ctk.CTkTextbox(
        list_container,
        height=250,
        corner_radius=0,
        fg_color="#2c3e50",
        text_color="#ecf0f1",
        font=("Roboto", 12),
        border_width=0,
        state="disabled"
    )
    employees_listbox.pack(pady=10, padx=10, fill="both", expand=True)
    
    # Panel de administradores con diseño mejorado
    admin_frame = ctk.CTkFrame(main_content, corner_radius=10, fg_color="#1e272e")
    admin_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    admin_header = ctk.CTkFrame(admin_frame, fg_color="transparent")
    admin_header.pack(fill="x", pady=(15, 10), padx=15)
    
    ctk.CTkLabel(
        admin_header, 
        text="👑 Administradores",
        font=("Roboto", 18, "bold"),
        text_color="#ff9800"
    ).pack(side="left")
    
    # Panel de botones de administradores con diseño mejorado
    admin_buttons_frame = ctk.CTkFrame(admin_frame, fg_color="transparent")
    admin_buttons_frame.pack(fill="x", padx=15, pady=(15,10))

    add_admin_btn = ctk.CTkButton(
        admin_buttons_frame,
        text="👑 Nuevo Admin",
        command=lambda: add_admin_dialog(admins_file, tab.winfo_toplevel(), admins_listbox),
        fg_color="#3498db",
        hover_color="#2980b9",
        font=("Roboto", 13, "bold"),
        corner_radius=8,
        height=40,
        width=160
    )
    add_admin_btn.pack(side="left", padx=5)

    remove_admin_btn = ctk.CTkButton(
        admin_buttons_frame,
        text="🗑️ Eliminar Admin",
        command=lambda: remove_admin_dialog(admins_file, tab.winfo_toplevel(), admins_listbox),
        fg_color="#e74c3c",
        hover_color="#c0392b",
        font=("Roboto", 13, "bold"),
        corner_radius=8,
        height=40,
        width=160
    )
    remove_admin_btn.pack(side="left", padx=5)
    
    # Lista de administradores con marco mejorado
    admin_list_container = ctk.CTkFrame(admin_frame, fg_color="#2c3e50", corner_radius=5)
    admin_list_container.pack(pady=10, padx=15, fill="both", expand=True)
    
    admin_list_header = ctk.CTkFrame(admin_list_container, fg_color="transparent")
    admin_list_header.pack(fill="x", padx=10, pady=(10, 0))
    
    ctk.CTkLabel(
        admin_list_header,
        text="Lista de Administradores",
        font=("Roboto", 14, "bold"),
        text_color="#ff9800"
    ).pack(side="left")
    
    admins_listbox = ctk.CTkTextbox(
        admin_list_container,
        height=250,
        corner_radius=0,
        fg_color="#2c3e50",
        text_color="#ecf0f1",
        font=("Roboto", 12),
        border_width=0,
        state="disabled"
    )
    admins_listbox.pack(pady=10, padx=10, fill="both", expand=True)
    
    # Información adicional
    info_bar = ctk.CTkFrame(tab, height=40, fg_color="#ff9800", corner_radius=5)
    info_bar.pack(fill="x", padx=10, pady=(15, 10))
    
    ctk.CTkLabel(
        info_bar,
        text="Consejo: Cree un nuevo administrador y elimine al admin (0), admin(0) dejara de funcionar si crea 1 nuevo",
        font=("Roboto", 12),
        text_color="white"
    ).place(relx=0.5, rely=0.5, anchor="center")
    
    return employees_listbox, admins_listbox

def load_employees(employees_file, employees_listbox):
    try:
        with open(employees_file, 'r') as f:
            employees = json.load(f)
        
        employees_listbox.configure(state="normal")
        employees_listbox.delete("1.0", "end")
        
        if not employees:
            employees_listbox.insert("end", "No hay empleados registrados")
        else:
            for emp in employees:
                employees_listbox.insert(
                    "end", 
                    f"ID: {emp.get('id', 'N/A')}\n"
                    f"Nombre: {emp.get('nombre', 'N/A')}\n"
                    f"Usuario: {emp.get('usuario', 'N/A')}\n"
                    f"Contraseña: {emp.get('contraseña', 'N/A')}\n"
                    f"{'-'*30}\n"
                )
        
        employees_listbox.configure(state="disabled")
    except Exception as e:
        ErrorDialog(None, f"No se pudieron cargar los empleados: {str(e)}",iconos("imagenes","error.ico"))

def load_admins(admins_file, admins_listbox):
    try:
        with open(admins_file, 'r') as f:
            admins = json.load(f)
        
        admins_listbox.configure(state="normal")
        admins_listbox.delete("1.0", "end")
        
        if not admins:
            admins_listbox.insert("end", "No hay administradores registrados")
        else:
            for admin in admins:
                admins_listbox.insert(
                    "end", 
                    f"ID: {admin.get('id', 'N/A')}\n"
                    f"Nombre: {admin.get('nombre', 'N/A')}\n"
                    f"Usuario: {admin.get('usuario', 'N/A')}\n"
                    f"Contraseña: {admin.get('contraseña', 'N/A')}\n"
                    f"{'-'*30}\n"
                )
        
        admins_listbox.configure(state="disabled")
    except Exception as e:
        ErrorDialog(None, f"No se pudieron cargar los administradores: {str(e)}",iconos("imagenes","error.ico"))

#añadir empleados
def add_employee_dialog(employees_file, parent_window, employees_listbox):
    dialog = ctk.CTkToplevel(parent_window)
    dialog.title("Agregar Empleado")
    dialog.geometry("450x570")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.configure(fg_color="#1a2a6d")
    
    # Encabezado
    header = ctk.CTkFrame(dialog, fg_color="#ff9800", corner_radius=0, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    ctk.CTkLabel(
        header, 
        text="Nuevo Empleado", 
        font=("Roboto", 18, "bold"),
        text_color="white"
    ).place(relx=0.5, rely=0.5, anchor="center")
    
    # Contenedor principal
    main_form = ctk.CTkFrame(dialog, fg_color="#1e272e", corner_radius=10)
    main_form.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Campos del formulario con iconos
    fields = [
        {"name": "id", "icon": "🆔", "placeholder": "Identificador único"},
        {"name": "nombre", "icon": "👤", "placeholder": "Nombre completo"},
        {"name": "usuario", "icon": "📝", "placeholder": "Nombre de usuario"},
        {"name": "contraseña", "icon": "🔒", "placeholder": "Contraseña segura", "show": "●"}
    ]
    entries = {}
    
    form_container = ctk.CTkFrame(main_form, fg_color="transparent")
    form_container.pack(padx=20, pady=20, fill="both", expand=True)
    
    for field in fields:
        # Marco del campo
        field_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)
        
        # Etiqueta con icono
        label_frame = ctk.CTkFrame(field_frame, fg_color="transparent")
        label_frame.pack(side="top", fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            label_frame,
            text=f"{field['icon']} {field['name'].capitalize()}:",
            font=("Roboto", 12, "bold"),
            text_color="#ff9800"
        ).pack(side="left")
        
        # Campo de entrada
        entry_kwargs = {
            "placeholder_text": field["placeholder"],
            "border_width": 1,
            "corner_radius": 5,
            "height": 35,
            "font": ("Roboto", 12)
        }
        
        if "show" in field:
            entry_kwargs["show"] = field["show"]
            
        entry = ctk.CTkEntry(field_frame, **entry_kwargs)
        entry.pack(fill="x")
        entries[field["name"]] = entry
    
    # Botones - Mejorado con contenedores separados para cada botón
    btn_container = ctk.CTkFrame(main_form, fg_color="#1a1a2e", corner_radius=5)
    btn_container.pack(fill="x", pady=(15, 5), padx=20)
    
    # Contenedor de botones con espaciado
    btn_layout = ctk.CTkFrame(btn_container, fg_color="transparent")
    btn_layout.pack(fill="x", pady=10, padx=10)
    btn_layout.grid_columnconfigure(0, weight=1)
    btn_layout.grid_columnconfigure(1, weight=1)
    
    # Botón Guardar
    save_btn = ctk.CTkButton(
        btn_layout,
        text="💾 Guardar",
        command=lambda: save_employee(entries, dialog, employees_file, employees_listbox),
        fg_color="#2ecc71",
        hover_color="#27ae60",
        font=("Roboto", 13, "bold"),
        corner_radius=8,
        height=42,
        width=150
    )
    save_btn.grid(row=0, column=0, padx=10, pady=5)
    # ✅ Centrar
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
    y = (dialog.winfo_screenheight() // 2) - (570 // 2)
    dialog.geometry(f"450x570+{x}+{y}")
    # Función de cierre robusta
    def close_add_employee_dialog():
        for child in dialog.winfo_children():
            try:
                if hasattr(child, 'winfo_class') and child.winfo_class() == 'CTkEntry':
                    try:
                        child.configure(state='disabled')
                    except Exception:
                        pass
                child.destroy()
            except Exception:
                pass
        dialog.destroy()
    # Botón Cancelar
    cancel_btn = ctk.CTkButton(
        btn_layout,
        text="❌ Cancelar",
        command=close_add_employee_dialog,
        fg_color="#e74c3c",
        hover_color="#c0392b",
        font=("Roboto", 13, "bold"),
        corner_radius=8,
        height=42,
        width=150
    )
    cancel_btn.grid(row=0, column=1, padx=10, pady=5)

def save_employee(entries, dialog, employees_file, employees_listbox):
    try:
        employee_data = {
            "id": entries["id"].get(),
            "nombre": entries["nombre"].get(),
            "usuario": entries["usuario"].get(),
            "contraseña": entries["contraseña"].get()
        }
        
        # Validar campos vacíos
        for key, value in employee_data.items():
            if not value.strip():
                InfoDialog(None, f"El campo {key} no puede estar vacío",iconos("imagenes","info.ico"))
                return
        
        # Leer empleados existentes
        with open(employees_file, 'r') as f:
            employees = json.load(f)
        
        # Verificar si el ID ya existe
        if any(emp["id"] == employee_data["id"] for emp in employees):
            InfoDialog(None, "Ya existe un empleado con este ID",iconos("imagenes","info.ico"))
            return
        
        # Añadir nuevo empleado
        employees.append(employee_data)
        
        # Guardar en el archivo
        with open(employees_file, 'w') as f:
            json.dump(employees, f, indent=4)
        
        InfoDialog(None, "Empleado agregado correctamente",iconos("imagenes","info.ico"))
        
        # Actualizar la lista de empleados
        load_employees(employees_file, employees_listbox)
        dialog.destroy()
        
    except Exception as e:
        ErrorDialog(None, f"No se pudo guardar el empleado: {str(e)}",iconos("imagenes","error.ico"))

def remove_employee_dialog(employees_file, parent_window, employees_listbox):
    dialog = ctk.CTkToplevel(parent_window)
    dialog.title("Eliminar Empleado")
    dialog.geometry("400x350")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.configure(fg_color="#1a2a6d")
    
    # Encabezado con advertencia
    header = ctk.CTkFrame(dialog, fg_color="#e74c3c", corner_radius=0, height=50)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    ctk.CTkLabel(
        header, 
        text="⚠️ Eliminar Empleado", 
        font=("Roboto", 16, "bold"),
        text_color="white"
    ).place(relx=0.5, rely=0.5, anchor="center")
    
    # Contenedor principal
    main_form = ctk.CTkFrame(dialog, fg_color="#1e272e", corner_radius=10)
    main_form.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Mensaje de advertencia
    ctk.CTkLabel(
        main_form,
        text="Esta acción no se puede deshacer.",
        font=("Roboto", 12),
        text_color="#e74c3c"
    ).pack(pady=(15, 10))
    
    # Campo de entrada para ID
    input_frame = ctk.CTkFrame(main_form, fg_color="transparent")
    input_frame.pack(fill="x", padx=20)
    
    ctk.CTkLabel(
        input_frame,
        text="🆔 ID del Empleado:",
        font=("Roboto", 12, "bold"),
        text_color="#ff9800"
    ).pack(anchor="w", pady=(0, 5))
    
    id_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="Ingrese el ID exacto del empleado",
        border_width=1,
        corner_radius=5,
        height=35,
        font=("Roboto", 12)
    )
    id_entry.pack(fill="x")
    
    # Botones - Mejorado con contenedores separados para cada botón
    btn_container = ctk.CTkFrame(main_form, fg_color="#1a1a2e", corner_radius=5)
    btn_container.pack(fill="x", pady=(20, 5), padx=10)
    
    # Contenedor de botones con espaciado
    btn_layout = ctk.CTkFrame(btn_container, fg_color="transparent")
    btn_layout.pack(fill="x", pady=10, padx=10)
    btn_layout.grid_columnconfigure(0, weight=1)
    btn_layout.grid_columnconfigure(1, weight=1)
    
    # Función de cierre robusta
    def close_remove_employee_dialog():
        for child in dialog.winfo_children():
            try:
                if hasattr(child, 'winfo_class') and child.winfo_class() == 'CTkEntry':
                    try:
                        child.configure(state='disabled')
                    except Exception:
                        pass
                child.destroy()
            except Exception:
                pass
        dialog.destroy()
    # Botón Cancelar
    cancel_btn = ctk.CTkButton(
        btn_layout,
        text="❌ Cancelar",
        command=close_remove_employee_dialog,
        fg_color="#14cf33",
        hover_color="#26c018",
        font=("Roboto", 13, "bold"),
        corner_radius=8,
        height=42,
        width=150
    )
    cancel_btn.grid(row=0, column=0, padx=10, pady=5)
    
    # Botón Eliminar
    delete_btn = ctk.CTkButton(
        btn_layout,
        text="🗑️ Eliminar",
        command=lambda: remove_employee(id_entry.get(), dialog, employees_file, employees_listbox),
        fg_color="#e74c3c",
        hover_color="#c0392b",
        font=("Roboto", 13, "bold"),
        corner_radius=8,
        height=42,
        width=150
    )
    delete_btn.grid(row=0, column=1, padx=10, pady=5)
    # ✅ Centrar
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
    y = (dialog.winfo_screenheight() // 2) - (570 // 2)
    dialog.geometry(f"450x570+{x}+{y}")

#Eliminar empleado por ID
def remove_employee(emp_id, dialog, employees_file, employees_listbox):
    try:
        if not emp_id.strip():
            InfoDialog(None, "Debe ingresar un ID",iconos("imagenes","info.ico"))
            return
        
        with open(employees_file, 'r') as f:
            employees = json.load(f)
        
        # Filtrar empleados, excluyendo el que coincide con el ID
        new_employees = [emp for emp in employees if emp["id"] != emp_id]
        
        if len(new_employees) == len(employees):
            InfoDialog(None, "No se encontró un empleado con ese ID",iconos("imagenes","info.ico"))
            return
        
        # Guardar los cambios
        with open(employees_file, 'w') as f:
            json.dump(new_employees, f, indent=4)
        
        InfoDialog(None, "Empleado eliminado correctamente",iconos("imagenes","info.ico"))
        
        # Actualizar la lista de empleados
        load_employees(employees_file, employees_listbox)
        dialog.destroy()
        
    except Exception as e:
        InfoDialog(None, f"No se pudo eliminar el empleado: {str(e)}",iconos("imagenes","info.ico"))

def add_admin_dialog(admins_file, parent_window, admins_listbox):
    dialog = ctk.CTkToplevel(parent_window)
    dialog.title("Agregar Administrador")
    dialog.geometry("450x480")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.configure(fg_color="#1a2a6d")
    
    # Contenedor principal
    main_form = ctk.CTkFrame(dialog, fg_color="#1e272e")
    main_form.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Campos del formulario
    entries = {}
    fields = [
        {"name": "id", "icon": "🆔", "placeholder": "ID único"},
        {"name": "nombre", "icon": "👤", "placeholder": "Nombre completo"},
        {"name": "usuario", "icon": "📝", "placeholder": "Nombre de usuario"},
        {"name": "contraseña", "icon": "🔒", "placeholder": "Contraseña", "show": "*"}
    ]
    
    for field in fields:
        frame = ctk.CTkFrame(main_form, fg_color="transparent")
        frame.pack(fill="x", pady=5, padx=20)
        
        ctk.CTkLabel(
            frame,
            text=f"{field['icon']} {field['name'].title()}:",
            font=("Roboto", 12, "bold")
        ).pack(anchor="w")
        
        entry = ctk.CTkEntry(
            frame,
            placeholder_text=field["placeholder"],
            show=field.get("show", ""),
            height=35
        )
        entry.pack(fill="x", pady=(5, 0))
        entries[field["name"]] = entry
    
    # Frame para botones
    button_frame = ctk.CTkFrame(main_form, fg_color="transparent")
    button_frame.pack(fill="x", pady=20, padx=20)
    
    # Botones
    def close_add_admin_dialog():
        for child in dialog.winfo_children():
            try:
                if hasattr(child, 'winfo_class') and child.winfo_class() == 'CTkEntry':
                    try:
                        child.configure(state='disabled')
                    except Exception:
                        pass
                child.destroy()
            except Exception:
                pass
        dialog.destroy()
    ctk.CTkButton(
        button_frame,
        text="Cancelar",
        command=close_add_admin_dialog,
        fg_color="#e74c3c",
        width=120,
        height=35
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        button_frame,
        text="Guardar",
        command=lambda: save_admin(entries, dialog, admins_file, admins_listbox),
        fg_color="#2ecc71",
        width=120,
        height=35
    ).pack(side="right", padx=5)
    # ✅ Centrar
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
    y = (dialog.winfo_screenheight() // 2) - (570 // 2)
    dialog.geometry(f"450x570+{x}+{y}")

def save_admin(entries, dialog, admins_file, admins_listbox):
    try:
        admin_data = {
            "id": entries["id"].get(),
            "nombre": entries["nombre"].get(),
            "usuario": entries["usuario"].get(),
            "contraseña": entries["contraseña"].get()
        }
        
        # Validar campos vacíos
        for key, value in admin_data.items():
            if not value.strip():
                InfoDialog(None, f"El campo {key} no puede estar vacío",iconos("imagenes","info.ico"))
                return
        
        # Leer administradores existentes
        with open(admins_file, 'r') as f:
            admins = json.load(f)
        
        # Verificar si el ID ya existe
        if any(admin["id"] == admin_data["id"] for admin in admins):
            InfoDialog(None, "Ya existe un administrador con este ID",iconos("imagenes","info.ico"))
            return
        
        # Añadir nuevo administrador
        admins.append(admin_data)
        
        # Guardar en el archivo
        with open(admins_file, 'w') as f:
            json.dump(admins, f, indent=4)
        
        InfoDialog(None, "Administrador agregado correctamente",iconos("imagenes","info.ico"))
        
        # Actualizar la lista de administradores
        load_admins(admins_file, admins_listbox)
        dialog.destroy()
        
    except Exception as e:
        InfoDialog(None, f"No se pudo guardar el administrador: {str(e)}",iconos("imagenes","info.ico"))

def remove_admin_dialog(admins_file, parent_window, admins_listbox):
    dialog = ctk.CTkToplevel(parent_window)
    dialog.title("Eliminar Administrador")
    dialog.geometry("400x350")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.configure(fg_color="#1a2a6d")
    
    # Contenedor principal
    main_form = ctk.CTkFrame(dialog, fg_color="#1e272e")
    main_form.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Advertencia
    ctk.CTkLabel(
        main_form,
        text="⚠️ ADVERTENCIA",
        font=("Roboto", 16, "bold"),
        text_color="#e74c3c"
    ).pack(pady=10)
    
    ctk.CTkLabel(
        main_form,
        text="Esta acción no se puede deshacer",
        font=("Roboto", 12),
        text_color="#95a5a6"
    ).pack()
    
    # Campo ID
    id_frame = ctk.CTkFrame(main_form, fg_color="transparent")
    id_frame.pack(fill="x", pady=20, padx=20)
    
    ctk.CTkLabel(
        id_frame,
        text="🆔 ID del Administrador:",
        font=("Roboto", 12, "bold")
    ).pack(anchor="w")
    
    id_entry = ctk.CTkEntry(
        id_frame,
        placeholder_text="Ingrese el ID",
        height=35
    )
    id_entry.pack(fill="x", pady=(5, 0))
    
    # Frame para botones
    button_frame = ctk.CTkFrame(main_form, fg_color="transparent")
    button_frame.pack(fill="x", pady=20, padx=20)
    
    # Botones
    def close_remove_admin_dialog():
        for child in dialog.winfo_children():
            try:
                if hasattr(child, 'winfo_class') and child.winfo_class() == 'CTkEntry':
                    try:
                        child.configure(state='disabled')
                    except Exception:
                        pass
                child.destroy()
            except Exception:
                pass
        dialog.destroy()
    ctk.CTkButton(
        button_frame,
        text="Cancelar",
        command=close_remove_admin_dialog,
        fg_color="#95a5a6",
        width=120,
        height=35
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        button_frame,
        text="Eliminar",
        command=lambda: remove_admin(id_entry.get(), dialog, admins_file, admins_listbox),
        fg_color="#e74c3c",
        width=120,
        height=35
    ).pack(side="right", padx=5)
    # ✅ Centrar
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
    y = (dialog.winfo_screenheight() // 2) - (570 // 2)
    dialog.geometry(f"450x570+{x}+{y}")

def remove_admin(admin_id, dialog, admins_file, admins_listbox):
    try:
        if not admin_id.strip():
            InfoDialog(None, "Debe ingresar un ID",iconos("imagenes","info.ico"))
            return
        
        with open(admins_file, 'r') as f:
            admins = json.load(f)
        
        # Filtrar administradores, excluyendo el que coincide con el ID
        new_admins = [admin for admin in admins if admin["id"] != admin_id]
        
        if len(new_admins) == len(admins):
            InfoDialog(None, "No se encontró un administrador con ese ID",iconos("imagenes","info.ico"))
            return

        # Verificar si se intenta eliminar el último administrador
        if len(admins) == 1 and admin_id == admins[0]["id"]:
            InfoDialog(None, "No se puede eliminar el último administrador del sistema.",iconos("imagenes","info.ico"))
            return

        # Guardar los cambios
        with open(admins_file, 'w') as f:
            json.dump(new_admins, f, indent=4)
        
        InfoDialog(None, "Administrador eliminado correctamente",iconos("imagenes","info.ico"))
        
        # Actualizar la lista de administradores
        load_admins(admins_file, admins_listbox)
        dialog.destroy()
        
    except Exception as e:
        InfoDialog(None, f"No se pudo eliminar el administrador: {str(e)}",iconos("imagenes","info.ico"))

def logout_admin(root):
    confirm_dialog = ctk.CTkToplevel(root)
    confirm_dialog.title("Confirmar cierre de sesión")
    confirm_dialog.geometry("380x230")
    confirm_dialog.resizable(False, False)
    confirm_dialog.grab_set()
    confirm_dialog.configure(fg_color="#1a2a6d")
    
    # Centrar el diálogo en la pantalla
    window_width = 380
    window_height = 230
    screen_width = confirm_dialog.winfo_screenwidth()
    screen_height = confirm_dialog.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    confirm_dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Contenedor principal
    main_content = ctk.CTkFrame(confirm_dialog, fg_color="#1e272e", corner_radius=10)
    main_content.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Icono y mensaje
    ctk.CTkLabel(
        main_content,
        text="🚪",
        font=("Roboto", 48)
    ).pack(pady=(20, 10))
    
    ctk.CTkLabel(
        main_content,
        text="¿Está seguro que desea cerrar sesión?",
        font=("Roboto", 14, "bold")
    ).pack(pady=5)
    
    # Frame para los botones
    button_frame = ctk.CTkFrame(main_content, fg_color="transparent")
    button_frame.pack(fill="x", pady=(20, 10), padx=20)
    
    # Función de cierre robusta
    def close_logout_dialog():
        for child in confirm_dialog.winfo_children():
            try:
                if hasattr(child, 'winfo_class') and child.winfo_class() == 'CTkEntry':
                    try:
                        child.configure(state='disabled')
                    except Exception:
                        pass
                child.destroy()
            except Exception:
                pass
        confirm_dialog.destroy()
    # Botón Cancelar
    ctk.CTkButton(
        button_frame,
        text="Cancelar",
        command=close_logout_dialog,
        fg_color="#95a5a6",
        hover_color="#7f8c8d",
        font=("Roboto", 13, "bold"),
        corner_radius=8,
        height=40,
        width=130
    ).pack(side="left", padx=10)
    
    # Botón Cerrar Sesión
    ctk.CTkButton(
        button_frame,
        text="Cerrar Sesión",
        command=lambda: confirmar_logout(root, confirm_dialog),
        fg_color="#e74c3c",
        hover_color="#c0392b",
        font=("Roboto", 13, "bold"),
        corner_radius=8,
        height=40,
        width=130
    ).pack(side="right", padx=10)
    
    def confirmar_logout(root, dialog):
        # ✅ Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (570 // 2)
        dialog.geometry(f"450x570+{x}+{y}")
        dialog.destroy()
        root.destroy()
        from TUCAN import run_login_app
        run_login_app()

