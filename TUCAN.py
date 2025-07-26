import customtkinter as ctk
from PIL import Image
import os
import json
from cuadro_mensaje import ErrorDialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def initialize_login_app():
    root = ctk.CTk()
    root.title("SISTEMA DE FACTURACION TUCAN")
    root._state_before_windows_set_titlebar_color = 'zoomed'

    icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
    try:
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        ErrorDialog(None, f"Advertencia: No se pudo cargar el icono: {e}")

    check_admin_file()
    check_users_file()

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    login_frame = ctk.CTkFrame(root, fg_color="transparent")
    login_frame.grid(row=0, column=0, padx=(100, 50), pady=40, sticky="nsew")

    image_frame = ctk.CTkFrame(root, fg_color="transparent")
    image_frame.grid(row=0, column=1, padx=(50, 100), pady=40, sticky="nsew")

    load_image(image_frame)
    username_entry, password_entry, show_pass_btn = create_login_widgets(login_frame, root)
    show_pass_btn.configure(command=lambda: toggle_password_visibility(password_entry, show_pass_btn))
    login_button = login_frame.grid_slaves(row=5, column=0)[0]
    login_button.configure(command=lambda: handle_login(username_entry, password_entry, login_frame, root))
    return root


def check_admin_file():
    admin_path = os.path.join(os.path.dirname(__file__), "admin.json")
    if not os.path.exists(admin_path):
        default_admin = [{"id": "0", "nombre": "PREDETERMINADO", "usuario": "admin", "contraseña": "admin"}]
        try:
            with open(admin_path, 'w', encoding='utf-8') as f:
                json.dump(default_admin, f, indent=4, ensure_ascii=False)
        except Exception as e:
            ErrorDialog(None, f"Error al crear admin.json: {e}")

def check_users_file():
    users_path = os.path.join(os.path.dirname(__file__), "usuarios.json")
    if not os.path.exists(users_path):
        try:
            with open(users_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4, ensure_ascii=False)
        except Exception as e:
            ErrorDialog(None, f"Error al crear usuarios.json: {e}")

def load_image(image_frame):
    try:
        image_path = os.path.join(os.path.dirname(__file__), "login.jpg")
        if not os.path.exists(image_path):
            raise FileNotFoundError("login.jpg no encontrado")
        pil_image = Image.open(image_path)
        screen_width = image_frame.winfo_screenwidth()
        screen_height = image_frame.winfo_screenheight()
        img_width = min(int(screen_width * 0.3), 500)
        img_height = int(screen_height * 0.5)
        ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(img_width, img_height))
        container = ctk.CTkFrame(image_frame, fg_color="transparent")
        container.pack(expand=True, fill="both", pady=20)
        image_label = ctk.CTkLabel(container, image=ctk_image, text="", fg_color="transparent")
        image_label.pack(pady=(0, 20))
        caption = ctk.CTkLabel(container, text="SF TUCAN", font=ctk.CTkFont(size=40, weight="bold"), text_color="lightblue", justify="center")
        caption.pack()
    except Exception as e:
        ErrorDialog(None, f"Error al cargar imagen: {e}")
        placeholder = ctk.CTkLabel(image_frame, text="Bienvenido al Sistema\nERROR IMAGEN\n© 2023", font=ctk.CTkFont(size=16), justify="center")
        placeholder.pack(expand=True)

def create_login_widgets(login_frame,root):
    login_frame.grid_columnconfigure(0, weight=1)
    title_label = ctk.CTkLabel(login_frame, text="Inicio de Sesión", font=ctk.CTkFont(size=28, weight="bold"))
    title_label.grid(row=0, column=0, pady=(20, 40), sticky="ew")

    ctk.CTkLabel(login_frame, text="Usuario:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=40, pady=(0, 5), sticky="w")
    username_entry = ctk.CTkEntry(login_frame, placeholder_text="Ingrese su usuario", font=ctk.CTkFont(size=14), height=40)
    username_entry.grid(row=2, column=0, padx=40, pady=(0, 15), sticky="ew")

    password_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
    password_frame.grid(row=3, column=0, padx=40, pady=(0, 5), sticky="ew")
    password_frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(password_frame, text="Contraseña:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, sticky="w")
    show_pass_btn = ctk.CTkButton(password_frame, text="👁️", width=30, height=30, fg_color="transparent", hover_color="#333333")
    show_pass_btn.grid(row=0, column=1, padx=(10, 0))
    password_entry = ctk.CTkEntry(login_frame, placeholder_text="Ingrese su contraseña", show="*", font=ctk.CTkFont(size=14), height=40)
    password_entry.grid(row=4, column=0, padx=40, pady=(0, 15), sticky="ew")

    login_button = ctk.CTkButton(login_frame, text="Acceder", font=ctk.CTkFont(size=14, weight="bold"), height=40)
    login_button.grid(row=5, column=0, padx=40, pady=(0, 20), sticky="ew")

    version_label = ctk.CTkLabel(login_frame, text="Versión : 1.2", font=ctk.CTkFont(size=12), text_color="gray")
    version_label.grid(row=6, column=0, pady=(20, 0), sticky="se")
    return username_entry, password_entry, show_pass_btn

def toggle_password_visibility(password_entry, show_pass_btn):
    if password_entry.cget("show") == "":
        password_entry.configure(show="*")
        show_pass_btn.configure(text="👁️")
    else:
        password_entry.configure(show="")
        show_pass_btn.configure(text="🔒")

def handle_login(username_entry, password_entry, login_frame, root):
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        show_error_message("¡Usuario y contraseña son requeridos!", login_frame, root)
        return
    if verify_admin_credentials(username, password):
        show_success_message("✓ Acceso Admin concedido", login_frame, root)
        root.after(1000, lambda: open_admin_panel(root))
    elif verify_sales_credentials(username, password):
        show_success_message("✓ Acceso Ventas concedido", login_frame, root)
        root.after(1000, lambda: open_sales_system(root))
    else:
        show_error_message("✗ Credenciales incorrectas", login_frame, root)

def verify_admin_credentials(username, password):
    admin_path = os.path.join(os.path.dirname(__file__), "admin.json")
    try:
        with open(admin_path, 'r', encoding='utf-8') as f:
            admins = json.load(f)
        return any(a["usuario"] == username and a["contraseña"] == password for a in admins)
    except Exception as e:
        ErrorDialog(None, f"Error al leer admin.json: {e}")
        return False

def verify_sales_credentials(username, password):
    users_path = os.path.join(os.path.dirname(__file__), "usuarios.json")
    try:
        if not os.path.exists(users_path):
            return False
        with open(users_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
        return any(u["usuario"] == username and u["contraseña"] == password for u in users)
    except Exception as e:
        ErrorDialog(None, f"Error al leer usuarios.json: {e}")
        return False

def open_admin_panel(root):
    root.destroy()
    from winADMIN import initialize_admin_panel
    app = initialize_admin_panel()
    app.mainloop()

def open_sales_system(root):
    root.destroy()
    from ventas_user import crear_sistema_ventas_tucan
    sales_app = crear_sistema_ventas_tucan()
    sales_app.mainloop()

def show_error_message(message, login_frame, root):
    for w in login_frame.grid_slaves(row=7, column=0):
        w.grid_forget()
    error_label = ctk.CTkLabel(login_frame, text=message, text_color="red", font=ctk.CTkFont(size=12, weight="bold"))
    error_label.grid(row=7, column=0, pady=(10, 0))
    root.after(3000, error_label.grid_forget)
    
def show_success_message(message, login_frame,root):
    for w in login_frame.grid_slaves(row=7, column=0):
        w.grid_forget()
    success_label = ctk.CTkLabel(login_frame, text=message, text_color="green", font=ctk.CTkFont(size=12, weight="bold"))
    success_label.grid(row=7, column=0, pady=(10, 0))
    root.after(1000, success_label.grid_forget)

def run_login_app():
    app = initialize_login_app()
    app.mainloop()

if __name__ == "__main__":
    run_login_app()