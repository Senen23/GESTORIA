import win32com.client as win32
import os
import sys
import tkinter as tk
from tkinter import ttk, PhotoImage
from tkcalendar import DateEntry
from database.search_data import search_data
import pandas as pd


class CheckCargasTab:
    def __init__(self, tab):
        self.tab = tab
        self.create_checkCargas_tab()

    def create_checkCargas_tab(self):
        
        # Cargar la imagen para los botones
        ruta_search = self.resource_path("images/search.png")
        ruta_mail = self.resource_path("images/mail.png")
        self.mail_image = PhotoImage(file=ruta_mail)
        self.search_image = PhotoImage(file=ruta_search)
        
        
        # Frame principal para contener todo (ocupa toda la ventana visible)
        self.main_frame = ttk.Frame(self.tab)
        self.main_frame.pack(fill="both", expand=True)

        # Frame superior fijo (título y botones)
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill="x", padx=10, pady=10)

        # Título
        title_label = ttk.Label(
            self.top_frame,
            text="Gestión de Informes CS2",
            font=("Arial", 16, "bold"),
            background="white",
            foreground="black"  
        )
        title_label.pack(pady=10)

        # Botón para mostrar resultados CS2
        self.show_cs2_button = ttk.Button(self.top_frame, text="Mostrar Informe CS2", image=self.search_image, command=self.mostrar_informe_cs2)
        self.show_cs2_button.pack(side="left", padx=5)

        # Botón para enviar correos
        self.send_mails_button = ttk.Button(self.top_frame, text="Enviar Correos", image=self.mail_image, command=self.enviar_correos, state="disabled")
        self.send_mails_button.pack(side="left", padx=5)

        # Frame inferior con desplazamiento para la tabla
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas para la tabla
        self.canvas = tk.Canvas(self.bottom_frame, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Barras de desplazamiento
        self.scroll_y = ttk.Scrollbar(self.bottom_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x = ttk.Scrollbar(self.bottom_frame, orient="horizontal", command=self.canvas.xview)
        self.scroll_x.pack(side="bottom", fill="x")

        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # Frame interno para la tabla
        self.table_inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.table_inner_frame, anchor="nw")

    def mostrar_informe_cs2(self):
        # Generar el DataFrame y la tabla pivote
        df_cs2 = search_data("cs2", None, None)
        df_or = search_data("or", None, None)

        # Renombrar y combinar datos
        df_or = df_or[['CODIGO', 'ABREVIATURA']].rename(columns={'CODIGO': 'CODIGO_OPERADOR_RED'})
        df_combinado = pd.merge(df_cs2, df_or, on='CODIGO_OPERADOR_RED', how='left')

        # Crear columna de fechas formateadas
        df_combinado['fecha'] = df_combinado['FECHA_APLICACION'].dt.to_period('M')

        # Generar tabla pivote con fechas como columnas y operadores como filas
        tabla_pivote = df_combinado.pivot_table(
            index='CODIGO_OPERADOR_RED',
            columns='fecha',
            values='NIU',
            aggfunc='count',
            fill_value=0
        )

        # Aplicar transformación "Sí" y "No"
        tabla_pivote = tabla_pivote.applymap(lambda x: 'Sí' if x > 0 else 'No')

        # Renombrar filas con nombres de operadores
        operador_map = df_or.set_index('CODIGO_OPERADOR_RED')['ABREVIATURA'].to_dict()
        tabla_pivote.index = [
            f"{operador_map.get(idx, 'Desconocido')} ({idx})" for idx in tabla_pivote.index
        ]

        # Ordenar las columnas (fechas) de forma descendente
        self.tabla_pivote = tabla_pivote[sorted(tabla_pivote.columns, reverse=True)]

        # Mostrar tabla en el Canvas
        self.mostrar_resultado_cs2(self.tabla_pivote)

        # Habilitar el botón de enviar correos
        self.send_mails_button.config(state="normal")

    def mostrar_resultado_cs2(self, tabla_pivote):
        # Limpiar cualquier contenido previo en el canvas
        for widget in self.table_inner_frame.winfo_children():
            widget.destroy()

        # Encabezados y datos
        data = [['Fecha'] + list(tabla_pivote.columns)] + [[str(idx)] + list(row) for idx, row in tabla_pivote.iterrows()]

        # Crear tabla personalizada
        self.create_table(data)

        # Ajustar el tamaño del canvas
        self.table_inner_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_table(self, data):
        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                bg_color = self.get_cell_color(value)
                fg_color = "black"  # Todo texto en negro
                label = tk.Label(
                    self.table_inner_frame,
                    text=value,
                    bg=bg_color,
                    fg=fg_color,
                    borderwidth=1,
                    relief="solid",
                    padx=10,
                    pady=5,
                    width=15
                )
                label.grid(row=row_idx, column=col_idx, sticky="nsew")

        for col_idx in range(len(data[0])):
            self.table_inner_frame.grid_columnconfigure(col_idx, weight=1)

    def get_cell_color(self, value):
        if value == "Sí":
            return "lightgreen"
        elif value == "No":
            return "tomato"
        elif value == "Fecha":
            return "gray"
        return "white"

    def enviar_correos(self):
        """Exporta la tabla pivote a Excel y la envía por correo usando Outlook."""
        try:
            if not hasattr(self, "tabla_pivote") or self.tabla_pivote.empty:
                tk.messagebox.showerror("Error", "No hay informe para enviar.")
                return

            # Guardar tabla como archivo Excel temporal
            temp_file = os.path.join(os.getcwd(), "informe_cs2.xlsx")
            self.tabla_pivote.to_excel(temp_file, index=True)

            # Crear correo en Outlook
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)
            mail.To = "destinatario@correo.com"  # Cambia por el correo real
            mail.Subject = "Informe CS2"
            mail.Body = "Adjunto el informe CS2 generado automáticamente."
            mail.Attachments.Add(temp_file)

            # Enviar el correo
            mail.Send()

            tk.messagebox.showinfo("Correo enviado", "El informe fue enviado con éxito.")

            # Borrar archivo temporal
            os.remove(temp_file)

        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo enviar el correo:\n{e}")

        
    def resource_path(self, relative_path):
        """ Devuelve la ruta absoluta del recurso, ya sea en desarrollo o en el ejecutable """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))  # _MEIPASS es el directorio temporal del ejecutable
        return os.path.join(base_path, relative_path)
