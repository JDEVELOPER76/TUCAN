import sqlite3
import customtkinter as ctk
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors  
from reportlab.lib.units import inch
from tkinter import ttk



class CustomDialog(ctk.CTkToplevel):
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
    def __init__(self, parent, message):
        super().__init__(parent, "Error", message)
        self.after(100, lambda: self.button.configure(fg_color="#d9534f", hover_color="#c9302c"))


class SuccessDialog(CustomDialog):
    def __init__(self, parent, message):
        super().__init__(parent, "Éxito", message, "Aceptar")
        
        self.after(100, lambda: self.button.configure(fg_color="#5cb85c", hover_color="#4cae4c"))


class SaleDetailsDialog(ctk.CTkToplevel):
    def __init__(self, parent, sale_data):
        super().__init__(parent)
        self.title(f"Detalles de Venta ID: {sale_data['id']}")
        self.geometry("600x400")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._frame = ctk.CTkFrame(self)
        self._frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self._frame.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self._frame, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(header_frame, text=f"Venta ID: {sale_data['id']}", font=("Roboto", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(header_frame, text=f"Fecha: {sale_data['date']}").pack(pady=2)
        ctk.CTkLabel(header_frame, text=f"Tipo: {sale_data['price_type']}", font=("Roboto", 12)).pack(pady=2)
        ctk.CTkLabel(header_frame, text=f"Total: ${float(sale_data['total']):.2f}",
                     text_color="#4fc3f7", font=("Roboto", 14, "bold")).pack(pady=10)

        products_frame = ctk.CTkFrame(self._frame)
        products_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        products_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(products_frame, text="Productos:", font=("Roboto", 12, "bold")).grid(row=0, column=0, sticky="w", pady=5)

        self.products_text = ctk.CTkTextbox(products_frame, wrap="word", height=150, activate_scrollbars=True)
        self.products_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        formatted_products = sale_data['products'].replace('\\n', '\n').replace('|', '\n')
        self.products_text.insert("1.0", formatted_products.strip())
        self.products_text.configure(state="disabled")

        close_btn = ctk.CTkButton(self._frame, text="Cerrar", command=self.destroy)
        close_btn.grid(row=2, column=0, pady=10)


class HistorialVentasApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._setup_app()
        self._setup_db()
        #self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.selected_report_type = "Ventas del día"
        self._create_ui()
        self._load_sales_today()

    def _setup_app(self):
        self.title("Sistema de Historial de Ventas")
        self._state_before_windows_set_titlebar_color='zoomed'
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
        self.iconbitmap(icon_path)

    def _setup_db(self):
        try:
            self.conn = sqlite3.connect('ventas.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    total REAL NOT NULL,
                    productos TEXT NOT NULL,
                    tipo_precio TEXT NOT NULL
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            ErrorDialog(self, f"Error de base de datos:\n{str(e)}")
            self.destroy()

    def _create_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header_frame, text="Buscar:").grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        self.date_entry = ctk.CTkEntry(header_frame, placeholder_text="Seleccione fecha...", width=120)
        self.date_entry.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        self.today_button = ctk.CTkButton(header_frame, text="Hoy", width=60, command=self._load_sales_today)
        self.today_button.grid(row=0, column=2, padx=5, pady=10)

        self.search_btn = ctk.CTkButton(header_frame, text="Buscar", width=80, command=self._search_sales)
        self.search_btn.grid(row=0, column=3, padx=5, pady=10)

        ctk.CTkLabel(header_frame, text="Tipo de Vista/Reporte:").grid(row=0, column=4, padx=(20, 5), pady=10, sticky="e")

        self.export_menu = ctk.CTkOptionMenu(
            header_frame,
            values=["Ventas del día", "Ventas mensuales", "Ventas anuales", "Ventas generales"],
            command=self._update_view_and_set_report_type
        )
        self.export_menu.grid(row=0, column=5, padx=(5, 10), pady=10, sticky="e")

        export_button = ctk.CTkButton(header_frame, text="Exportar PDF", command=self._execute_export, width=120)
        export_button.grid(row=0, column=6, padx=(5, 10), pady=10, sticky="e")

        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.sales_table = ttk.Treeview(
            content_frame,
            columns=('id', 'fecha', 'total', 'productos', 'tipo_precio'),
            show='headings',
            selectmode='browse',
            style="Custom.Treeview"
        )

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview",
                        font=('Segoe UI', 10),
                        rowheight=25,
                        background=self._apply_appearance_mode_color("bg_color"),
                        fieldbackground=self._apply_appearance_mode_color("field_bg_color"),
                        foreground=self._apply_appearance_mode_color("text_color"))
        style.map("Custom.Treeview", background=[('selected', self._apply_appearance_mode_color("selected_bg_color"))])
        style.configure("Custom.Treeview.Heading",
                        font=('Segoe UI', 10, 'bold'),
                        background=self._apply_appearance_mode_color("header_bg_color"),
                        foreground=self._apply_appearance_mode_color("header_text_color"))
        style.map("Custom.Treeview.Heading", background=[('active', self._apply_appearance_mode_color("header_hover_color"))])

        columns = {
            'id': {'text': 'ID', 'width': 50, 'anchor': 'center'},
            'fecha': {'text': 'Fecha y Hora', 'width': 150, 'anchor': 'center'},
            'total': {'text': 'Total', 'width': 100, 'anchor': 'center'},
            'productos': {'text': 'Productos', 'width': 400, 'anchor': 'center'},
            'tipo_precio': {'text': 'Tipo Venta', 'width': 120, 'anchor': 'center'}
        }
        for col, config in columns.items():
            self.sales_table.heading(col, text=config['text'])
            self.sales_table.column(col, width=config.get('width', 100), anchor=config.get('anchor', 'w'))

        vsb = ttk.Scrollbar(content_frame, orient="vertical", command=self.sales_table.yview)
        hsb = ttk.Scrollbar(content_frame, orient="horizontal", command=self.sales_table.xview)
        self.sales_table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.sales_table.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        # ---  Single click now opens the details window  ---
        self.sales_table.bind("<Double-1>", self._show_sale_details_window)

    def _apply_appearance_mode_color(self, element):
        colors_map = {
            "dark": {
                "bg_color": "#2b2b2b",
                "field_bg_color": "#2b2b2b",
                "text_color": "#ffffff",
                "selected_bg_color": "#3b8ed0",
                "header_bg_color": "#3a3a3a",
                "header_text_color": "#ffffff",
                "header_hover_color": "#4a4a4a"
            },
            "light": {
                "bg_color": "#ffffff",
                "field_bg_color": "#ffffff",
                "text_color": "#000000",
                "selected_bg_color": "#3b8ed0",
                "header_bg_color": "#e0e0e0",
                "header_text_color": "#000000",
                "header_hover_color": "#d0d0d0"
            }
        }
        mode = ctk.get_appearance_mode().lower()
        return colors_map.get(mode, colors_map["dark"]).get(element)



    def _update_view_and_set_report_type(self, choice):
        self.selected_report_type = choice
        self.export_menu.set(choice)
        self.date_entry.delete(0, ctk.END)

        if choice == "Ventas del día":
            self.date_entry.configure(placeholder_text="YYYY-MM-DD", state="normal")
            self.today_button.configure(state="normal")
            self.search_btn.configure(text="Buscar", command=self._search_sales, state="normal")
            self._load_sales_today()
        elif choice == "Ventas mensuales":
            self.date_entry.configure(placeholder_text="YYYY-MM", state="normal")
            self.today_button.configure(state="disabled")
            self.search_btn.configure(text="Buscar Mes", command=lambda: self._search_sales(mode="month"), state="normal")
            self.sales_table.delete(*self.sales_table.get_children())
        elif choice == "Ventas anuales":
            self.date_entry.configure(placeholder_text="YYYY", state="normal")
            self.today_button.configure(state="disabled")
            self.search_btn.configure(text="Buscar Año", command=lambda: self._search_sales(mode="year"), state="normal")
            self.sales_table.delete(*self.sales_table.get_children())
        elif choice == "Ventas generales":
            self.date_entry.configure(placeholder_text="", state="disabled")
            self.today_button.configure(state="disabled")
            self.search_btn.configure(text="Buscar", state="disabled")
            self._show_general_sales()

    def _execute_export(self):
        choice = self.selected_report_type
        if choice == "Ventas del día":
            self._export_daily_pdf()
        elif choice == "Ventas generales":
            self._export_general_sales_pdf()
        elif choice == "Ventas mensuales":
            self._export_monthly_pdf()
        elif choice == "Ventas anuales":
            self._export_yearly_pdf()

    def _load_sales_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_entry.delete(0, ctk.END)
        self.date_entry.insert(0, today)
        self._search_sales()

    def _search_sales(self, mode="day"):
        date_str = self.date_entry.get().strip()

        if mode == "day":
            if not date_str:
                ErrorDialog(self, "Por favor, seleccione una fecha (YYYY-MM-DD).")
                return
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                query = """
                    SELECT id, fecha, total, productos, tipo_precio
                    FROM ventas
                    WHERE date(fecha) = ?
                    ORDER BY fecha DESC
                """
                self.cursor.execute(query, (date_str,))
                sales = self.cursor.fetchall()
                self._display_sales(sales)
            except ValueError:
                ErrorDialog(self, "Formato de fecha inválido.\nUse YYYY-MM-DD")
            except Exception as e:
                ErrorDialog(self, f"Error al buscar ventas diarias:\n{str(e)}")

        elif mode == "month":
            if not date_str:
                ErrorDialog(self, "Por favor, seleccione un mes (YYYY-MM).")
                return
            try:
                datetime.strptime(date_str, "%Y-%m")
                query = """
                    SELECT id, fecha, total, productos, tipo_precio
                    FROM ventas
                    WHERE strftime('%Y-%m', fecha) = ?
                    ORDER BY fecha DESC
                """
                self.cursor.execute(query, (date_str,))
                sales = self.cursor.fetchall()
                self._display_sales(sales)
            except ValueError:
                ErrorDialog(self, "Formato de mes inválido.\nUse YYYY-MM")
            except Exception as e:
                ErrorDialog(self, f"Error al buscar ventas mensuales:\n{str(e)}")

        elif mode == "year":
            if not date_str:
                ErrorDialog(self, "Por favor, seleccione un año (YYYY).")
                return
            try:
                datetime.strptime(date_str, "%Y")
                query = """
                    SELECT id, fecha, total, productos, tipo_precio
                    FROM ventas
                    WHERE strftime('%Y', fecha) = ?
                    ORDER BY fecha DESC
                """
                self.cursor.execute(query, (date_str,))
                sales = self.cursor.fetchall()
                self._display_sales(sales)
            except ValueError:
                ErrorDialog(self, "Formato de año inválido.\nUse YYYY")
            except Exception as e:
                ErrorDialog(self, f"Error al buscar ventas anuales:\n{str(e)}")

    def _display_sales(self, sales):
        self.sales_table.delete(*self.sales_table.get_children())
        if not sales and self.selected_report_type != "Ventas generales":
            CustomDialog(self, "Información", "No se encontraron ventas para el criterio seleccionado.")
            return

        for sale in sales:
            sale_id, date, total, products, price_type = sale
            formatted_date = date[:19] if len(date) > 19 else date
            self.sales_table.insert('', 'end', values=(
                sale_id,
                formatted_date,
                f"${float(total):.2f}",
                "Ver más…",  # <- Placeholder shown in the table
                self._get_readable_price_type(price_type)
            ))

    def _get_readable_price_type(self, price_type):
        price_types = {
            "Venta 1": "Venta 1",
            "Venta 2": "Venta 2",
            "Venta 3": "Venta 3"
        }
        return price_types.get(price_type, price_type)

    def _show_sale_details_window(self, event):
        # Ignore clicks on the header separator
        if self.sales_table.identify_region(event.x, event.y) == "heading":
            return

        selected_item = self.sales_table.identify_row(event.y)
        if not selected_item:
            return
        try:
            sale_id = self.sales_table.item(selected_item, 'values')[0]
            self.cursor.execute("""
                SELECT fecha, total, tipo_precio, productos
                FROM ventas
                WHERE id = ?
            """, (sale_id,))
            sale = self.cursor.fetchone()
            if not sale:
                return
            date, total, price_type, products = sale
            sale_data = {
                'id': sale_id,
                'date': date,
                'total': total,
                'price_type': self._get_readable_price_type(price_type),
                'products': products
            }
            SaleDetailsDialog(self, sale_data)
        except Exception as e:
            ErrorDialog(self, f"Error al mostrar detalles:\n{str(e)}")

    def _generate_pdf_report(self, filename_prefix, title, query, params=None, mode="daily"):
        try:
            os.makedirs("ventas", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ventas/{filename_prefix}_{timestamp}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter,
                                    rightMargin=40, leftMargin=40,
                                    topMargin=40, bottomMargin=40)

            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name="ReportTitle", fontSize=16, alignment=1, spaceAfter=20,
                fontName="Helvetica-Bold", textColor=colors.HexColor("#2c3e50")
            ))
            styles.add(ParagraphStyle(
                name="SectionHeader", fontSize=12, fontName="Helvetica-Bold",
                textColor=colors.HexColor("#3498db"), spaceAfter=10
            ))
            styles.add(ParagraphStyle(
                name="Highlight", fontSize=12, alignment=1, fontName="Helvetica-Bold",
                textColor=colors.HexColor("#e74c3c"), spaceBefore=10, spaceAfter=10
            ))

            meses_espanol = {
                'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
            }

            elements = [Paragraph(title, styles["ReportTitle"])]

            self.cursor.execute(query, params if params else ())
            sales_data = self.cursor.fetchall()

            if not sales_data:
                ErrorDialog(self, "No hay datos para generar el reporte.")
                return

            elif mode == "daily":
                from collections import defaultdict

                ventas = defaultdict(lambda: defaultdict(lambda: {'unidades': 0, 'total': 0}))
                total_general = 0

                for sale in sales_data:
                    _, fecha, total_venta, productos, tipo_venta = sale
                    tipo = self._get_readable_price_type(tipo_venta)

                    for chunk in productos.replace('\\n', '\n').split('|'):
                        chunk = chunk.strip()
                        if not chunk:
                            continue

                        try:
                            name_part, rest_part = chunk.split('(', 1)
                            nombre = name_part.strip()

                            rest_part = rest_part.rstrip(')')
                            unidades_str, _, subtotal_str = rest_part.partition(' x ')
                            subtotal_str = subtotal_str.split('=')[1].split('-')[0]
                            unidades = int(unidades_str.strip())
                            subtotal = float(subtotal_str.replace('$', '').strip())
                        except Exception:
                            continue

                        ventas[tipo][nombre]['unidades'] += unidades
                        ventas[tipo][nombre]['total'] += subtotal
                        total_general += subtotal

                product_style = ParagraphStyle('ProductStyle', fontSize=9, leading=10, alignment=TA_LEFT)

                table_data = [["Producto", "Unidades", "Tipo de Venta", "Total"]]
                for tipo, productos in ventas.items():
                    for prod, datos in productos.items():
                        table_data.append([
                            Paragraph(prod, product_style),
                            str(datos['unidades']),
                            tipo,
                            f"${datos['total']:.2f}"
                        ])

                table = Table(table_data, colWidths=[2.2*inch, 0.7*inch, 1.2*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498db")),
                    ('TEXTCOLOR',  (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN',      (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN',      (1, 1), (1, -1), 'CENTER'),
                    ('ALIGN',      (3, 1), (3, -1), 'RIGHT'),
                    ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE',   (0, 0), (-1, 0), 9),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID',       (0, 0), (-1, -1), 1, colors.lightgrey),
                    ('VALIGN',     (0, 0), (-1, -1), 'TOP')
                ]))

                elements.append(Paragraph("Resumen del día", styles["SectionHeader"]))
                elements.append(table)
                elements.append(Spacer(1, 15))
                elements.append(Paragraph(f"TOTAL GENERAL DEL DÍA: ${total_general:.2f}", styles["Highlight"]))

            elif mode == "monthly":
                mes_param = params[0]
                anio, mes = mes_param.split('-')[:2]

                query_dias = """
                    SELECT date(fecha) as dia,
                           SUM(total) as total_dia
                    FROM ventas
                    WHERE strftime('%Y-%m', fecha) = ?
                    GROUP BY dia
                    ORDER BY dia
                """
                self.cursor.execute(query_dias, (mes_param,))
                dias_data = self.cursor.fetchall()

                try:
                    fecha_mes = datetime(int(anio), int(mes), 1)
                    nombre_mes = meses_espanol[fecha_mes.strftime("%B")]
                except Exception:
                    nombre_mes = mes_param

                table_data = [['Día', 'Total']]
                total_mes = 0

                for row in dias_data:
                    dia_str = row[0]
                    total_dia = row[1]
                    table_data.append([dia_str, f"${float(total_dia):.2f}"])
                    total_mes += float(total_dia)

                table = Table(table_data, colWidths=[3*inch, 3*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498db")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
                ]))

                elements.append(Paragraph(f"VENTAS DE {nombre_mes.upper()} {anio}", styles["SectionHeader"]))
                elements.append(table)
                elements.append(Spacer(1, 15))
                elements.append(Paragraph(f"TOTAL MENSUAL: ${total_mes:.2f}", styles["Highlight"]))

            elif mode == "yearly":
                anio = params[0]

                query_meses = """
                    SELECT strftime('%m', fecha) as mes,
                           SUM(total) as total_mes
                    FROM ventas
                    WHERE strftime('%Y', fecha) = ?
                    GROUP BY mes
                    ORDER BY mes
                """
                self.cursor.execute(query_meses, (anio,))
                meses_data = self.cursor.fetchall()

                table_data = [['Mes', 'Total']]
                total_anual = 0

                for mes_num, total in meses_data:
                    nombre_mes = meses_espanol[datetime.strptime(mes_num, "%m").strftime("%B")]
                    table_data.append([nombre_mes, f"${float(total):.2f}"])
                    total_anual += float(total)

                table = Table(table_data, colWidths=[3*inch, 3*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498db")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
                ]))

                elements.append(Paragraph(f"VENTAS DEL AÑO {anio}", styles["SectionHeader"]))
                elements.append(table)
                elements.append(Spacer(1, 15))
                elements.append(Paragraph(f"TOTAL ANUAL: ${total_anual:.2f}", styles["Highlight"]))

            doc.build(elements)
            SuccessDialog(self, f"Reporte generado exitosamente:\n{filename}")

        except Exception as e:
            ErrorDialog(self, f"Error al generar PDF:\n{str(e)}")

    def _export_daily_pdf(self):
        date_str = self.date_entry.get().strip()
        if not date_str:
            ErrorDialog(self, "Por favor, seleccione una fecha para el reporte diario.")
            return
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            query = """
                SELECT id, fecha, total, productos, tipo_precio
                FROM ventas
                WHERE date(fecha) = ?
                ORDER BY fecha DESC
            """
            title = f"REPORTE DE VENTAS DEL DÍA - {date_str}"
            self._generate_pdf_report("reporte_ventas_dia", title, query, (date_str,), mode="daily")
        except ValueError:
            ErrorDialog(self, "Formato de fecha inválido para el reporte diario.\nUse YYYY-MM-DD")

    def _export_monthly_pdf(self):
        date_str = self.date_entry.get().strip()
        if not date_str:
            ErrorDialog(self, "Por favor, seleccione un mes para el reporte mensual (YYYY-MM).")
            return
        try:
            datetime.strptime(date_str, "%Y-%m")
            query = """
                SELECT id, fecha, total, productos, tipo_precio
                FROM ventas
                WHERE strftime('%Y-%m', fecha) = ?
                ORDER BY fecha DESC
            """
            title = f"REPORTE DE VENTAS MENSUALES - {date_str}"
            self._generate_pdf_report("reporte_ventas_mensual", title, query, (date_str,), mode="monthly")
        except ValueError:
            ErrorDialog(self, "Formato de mes inválido para el reporte mensual.\nUse YYYY-MM")

    def _export_yearly_pdf(self):
        date_str = self.date_entry.get().strip()
        if not date_str:
            ErrorDialog(self, "Por favor, seleccione un año para el reporte anual (YYYY).")
            return
        try:
            datetime.strptime(date_str, "%Y")
            query = """
                SELECT id, fecha, total, productos, tipo_precio
                FROM ventas
                WHERE strftime('%Y', fecha) = ?
                ORDER BY fecha DESC
            """
            title = f"REPORTE DE VENTAS ANUALES - {date_str}"
            self._generate_pdf_report("reporte_ventas_anual", title, query, (date_str,), mode="yearly")
        except ValueError:
            ErrorDialog(self, "Formato de año inválido para el reporte anual.\nUse YYYY")

    def _show_general_sales(self):
        try:
            self.cursor.execute("SELECT id, fecha, total, productos, tipo_precio FROM ventas ORDER BY fecha DESC")
            sales = self.cursor.fetchall()
            self._display_sales(sales)
            if not sales:
                CustomDialog(self, "Información", "No hay ventas registradas en el historial.")
        except Exception as e:
            ErrorDialog(self, f"Error al cargar ventas generales:\n{str(e)}")

    def _export_general_sales_pdf(self):
        query = """
            SELECT date(fecha) as day,
                   SUM(total) as total_day,
                   COUNT(*) as sales_count
            FROM ventas
            GROUP BY day
            ORDER BY day DESC
        """
        title = "REPORTE GENERAL DE VENTAS POR DÍA"
        self._generate_pdf_report("reporte_general", title, query, mode="general_summary")

    def _on_closing(self):
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception:
            ErrorDialog(self,"Error al cerrar la base de datos")
        finally:
            self.quit()
            self.destroy()


