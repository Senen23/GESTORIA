import tkinter as tk
import pandas as pd
import os
import sys
from tkinter import messagebox, filedialog, ttk, PhotoImage
from tkcalendar import DateEntry
from datetime import datetime
from dataread.reports import create_file, export_files
from dataread.checks import Checks
from database.search_data import search_data

class CheckTab:
    def __init__(self, tab):
        self.tab = tab
        self.create_check_tab()
        
    def create_check_tab(self):
        self.main_frame = ttk.Frame(self.tab)
        self.main_frame.pack(fill='both', expand=True)

        # Cargar la imagen para los botones
        ruta_search = self.resource_path("images/search.png")
        ruta_excel = self.resource_path("images/excel.png")
        ruta_save = self.resource_path("images/save.png")
        self.save_image = PhotoImage(file=ruta_save)
        self.excel_image = PhotoImage(file=ruta_excel)
        self.search_image = PhotoImage(file=ruta_search)

        # Canvas principal con barra de desplazamiento vertical y horizontal
        self.canvas = tk.Canvas(self.main_frame, bg="white", bd=0, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Deshabilitar que el canvas se redimensione automáticamente
        self.main_frame.pack_propagate(0)

        # Scrollbar vertical
        self.scrollbar_y = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)

        # Scrollbar horizontal
        self.scrollbar_x = tk.Scrollbar(self.main_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.configure(xscrollcommand=self.scrollbar_x.set)

        # Crear el frame principal dentro del canvas
        self.frame = tk.Frame(self.canvas, bg="white")
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # Forzar actualización del scrollregion cuando se redimensiona el frame interno
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Evento que se llama cuando el canvas se redimensiona
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width))

        # Contenido del frame principal
        title_label = ttk.Label(self.frame, background='#ffffff', foreground='#000000', text="Verificar Compensaciones", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        date_label = ttk.Label(self.frame, background='#ffffff', text="Seleccione la fecha de los checkbox o el informe a sacar", font=('Arial', 12))
        date_label.pack(pady=5)

        self.date_entry = DateEntry(self.frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.date_entry.pack(pady=10)

        # Crear un frame para contener los botones
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(pady=10)

        # Botones
        self.search_pendientes_button = ttk.Button(self.button_frame, text="Buscar pendientes", image=self.search_image, command=lambda: self.show_data('pendientes'))
        self.search_pendientes_button.pack(side='left')

        self.search_mes_button = ttk.Button(self.button_frame, text="Buscar por mes", image=self.search_image, command=lambda: self.show_data('mes'))
        self.search_mes_button.pack(side='left')

        self.reports_button = ttk.Button(self.button_frame, text="Exportar reportes Excel", image=self.excel_image, state="disabled")
        self.reports_button.pack(side='left')
        
        self.extract_button = ttk.Button(self.frame, text="Extraer información", state="disabled")
        self.extract_button.pack(side='top', anchor='w')

        # Crear un contenedor para el grid_canvas y sus scrollbars
        self.grid_container = tk.Frame(self.frame)
        self.grid_container.pack(fill='both', expand=True)

        # Canvas y barras de desplazamiento para grid_frame dentro del grid_container
        self.grid_canvas = tk.Canvas(self.grid_container, bg="white", bd=0, highlightthickness=0)
        self.grid_canvas.pack(side="left", fill='both', expand=True)

        # Scrollbar vertical en grid_container
        self.grid_scrollbar_y = tk.Scrollbar(self.grid_container, orient="vertical", command=self.grid_canvas.yview)
        self.grid_scrollbar_y.pack(side="right", fill="y")
        self.grid_canvas.configure(yscrollcommand=self.grid_scrollbar_y.set)

        # Scrollbar horizontal en grid_container
        self.grid_scrollbar_x = tk.Scrollbar(self.grid_container, orient="horizontal", command=self.grid_canvas.xview)
        self.grid_scrollbar_x.pack(side="bottom", fill="x")
        self.grid_canvas.configure(xscrollcommand=self.grid_scrollbar_x.set)

        # Frame dentro del grid_canvas para mostrar los datos
        self.grid_frame = tk.Frame(self.grid_canvas, bg="white")
        self.grid_canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")

        # Forzar la actualización de la región de desplazamiento del grid_canvas
        self.grid_frame.bind("<Configure>", lambda e: self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox("all")))

        # Botón "Guardar cambios" debajo del grid_frame
        self.save_button = ttk.Button(self.frame, text="Guardar cambios", image=self.save_image, command=self.save_decisions)
        self.save_button.pack(pady=10)
        
    def show_data(self, estado):
        # Limpiar el grid_frame si ya existe para evitar duplicación
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Instancia la clase checks
        self.check_instance = Checks()
        if estado == 'pendientes':
            self.check_instance.get_pendientes()
        elif estado == 'mes':
            self.check_instance.get_pendientes_mes(self.date_entry.get_date())

        self.df = self.check_instance.df_operar
        self.df['FECHA'] = self.df['FECHA'].dt.strftime('%d/%m/%Y')
        
        # Etiquetas para las columnas
        for idx, col_name in enumerate(self.df.columns):
            label = ttk.Label(self.grid_frame, text=col_name, font=("Arial", 10, 'bold'), background="#00008b")
            label.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")

        # Crear una lista para almacenar los estados de los checkboxes
        self.check_isagen_vars = []
        self.check_or_vars = []
        self.check_rechazada_vars = []
        self.observation_vars = []

        # Mostrar todas las columnas para cada fila
        for i, row in self.df.iterrows():
            for j, value in enumerate(row):
                if j == len(self.df.columns) - 8:  #poner en formato $dinero 
                    label = tk.Label(self.grid_frame, text= f'$ {value:,.2f}', bg="#f0f0f0")
                    label.grid(row=i + 1, column=j, padx=5, pady=5, sticky="nsew")
                
                elif j == len(self.df.columns) - 6:  # Si es la columna 'PAGADO_ISAGEN', mostrar un checkbox
                    check_var = tk.IntVar(value=int(row['PAGADO_ISAGEN']))  # Asegúrate de convertir el valor a entero
                    self.check_isagen_vars.append(check_var)

                    checkbox = tk.Checkbutton(self.grid_frame, variable=check_var, bg="#f0f0f0")
                    checkbox.grid(row=i + 1, column=j, padx=5, pady=5, sticky="nsew")
                
                elif j == len(self.df.columns) - 5:  
                    check_var = tk.IntVar(value=int(row['PAGADO_OR'])) 
                    self.check_or_vars.append(check_var)

                    checkbox = tk.Checkbutton(self.grid_frame, variable=check_var, bg="#f0f0f0")
                    checkbox.grid(row=i + 1, column=j, padx=5, pady=5, sticky="nsew")
                
                elif j == len(self.df.columns) - 2: 
                    entry = tk.Entry(self.grid_frame, bg="#f0f0f0")
                    entry.insert(0, str(value))  
                    entry.grid(row=i + 1, column=j, padx=10, pady=10, sticky="nsew")
                    self.observation_vars.append(entry)  # Guardar la referencia de cada entrada para luego guardar los cambios
                
                elif j == len(self.df.columns) - 1: 
                    check_var = tk.IntVar(value=int(row['RECHAZADA']))  
                    self.check_rechazada_vars.append(check_var)

                    checkbox = tk.Checkbutton(self.grid_frame, variable=check_var, bg="#f0f0f0")
                    checkbox.grid(row=i + 1, column=j, padx=5, pady=5, sticky="nsew")
                
                else:  # Si es otra columna, mostrar el valor como etiqueta
                    label = tk.Label(self.grid_frame, text=str(value), bg="#f0f0f0")
                    label.grid(row=i + 1, column=j, padx=5, pady=5, sticky="nsew")
     
        self.add_report_summary()
        self.reports_button.config(state='normal', command=lambda: self.export_csv(self.date_entry.get()))
        self.extract_button.config(state='normal', command=self.export_data)

    def add_report_summary(self):
        # Verificar si ya existe el frame del informe y si ya existe, eliminar su contenido
        if hasattr(self, 'report_frame'):
            for widget in self.report_frame.winfo_children():
                widget.destroy()
        else:
            # Si no existe, crear el contenedor del informe
            self.report_frame = tk.Frame(self.frame, bg="lightgrey")
            self.report_frame.pack(fill='x', pady=10)

        # Agrupar por 'OPERADOR_RED' y calcular la cantidad de elementos y suma de 'VF_A_COMP'
        operador_summary = self.df.groupby('OPERADOR_RED').agg(
            total_elementos=('OPERADOR_RED', 'size'),
            suma_vf_a_comp=('VF_A_COMP', 'sum')
        ).reset_index()

        # Calcular los totales de PAGADO_ISAGEN, PAGADO_OR, RECHAZADA por operador
        pagado_isagen_summary = self.df[self.df['PAGADO_ISAGEN'] == 1].groupby('OPERADOR_RED').agg(
            total_pagado_isagen=('PAGADO_ISAGEN', 'size'),
            suma_pagado_isagen=('VF_A_COMP', 'sum')
        ).reset_index()

        pagado_or_summary = self.df[self.df['PAGADO_OR'] == 1].groupby('OPERADOR_RED').agg(
            total_pagado_or=('PAGADO_OR', 'size'),
            suma_pagado_or=('VF_A_COMP', 'sum')
        ).reset_index()

        rechazada_summary = self.df[self.df['RECHAZADA'] == 1].groupby('OPERADOR_RED').agg(
            total_rechazada=('RECHAZADA', 'size'),
            suma_rechazada=('VF_A_COMP', 'sum')
        ).reset_index()

        # Combinar todos los resultados en un solo DataFrame
        operador_summary = operador_summary.merge(pagado_isagen_summary, on='OPERADOR_RED', how='left').merge(
            pagado_or_summary, on='OPERADOR_RED', how='left').merge(
            rechazada_summary, on='OPERADOR_RED', how='left')

        # Reemplazar valores NaN por 0
        operador_summary.fillna(0, inplace=True)

        # Calcular totales generales
        total_elementos_general = operador_summary['total_elementos'].sum()
        total_vf_a_comp_general = operador_summary['suma_vf_a_comp'].sum()
        total_pagado_isagen = operador_summary['suma_pagado_isagen'].sum()
        total_pagado_or = operador_summary['suma_pagado_or'].sum()
        total_rechazada = operador_summary['suma_rechazada'].sum()

        total_count_pagado_isagen = operador_summary['total_pagado_isagen'].sum()
        total_count_pagado_or = operador_summary['total_pagado_or'].sum()
        total_count_rechazada = operador_summary['total_rechazada'].sum()

        self.report_text_widget = tk.Text(self.report_frame, height=15, wrap="none", font=('Courier', 12))
        self.report_text_widget.pack(fill="both", padx=10, pady=10, expand=True)
        
        # Crear un Label para mostrar el resumen en formato tabla
        report_text = "Informe Resumido por Operador:\n\n"
        report_text += f"{'Operador':<20}{'Total Fronteras':<20}{'Suma VF_A_COMP':<20}{'PAGADO_ISAGEN':<20}{'PAGADO_OR':<20}{'RECHAZADA':<20}\n"
        report_text += "-" * 120 + "\n"

        # Añadir filas por cada operador
        for _, row in operador_summary.iterrows():
            report_text += f"{row['OPERADOR_RED']:<20}{int(row['total_elementos']):<20}$ {row['suma_vf_a_comp']:<20,.2f}"
            report_text += f"{int(row['total_pagado_isagen']):<20}{int(row['total_pagado_or']):<20}{int(row['total_rechazada']):<20}\n"

        # Añadir el total general al final de la tabla
        report_text += "-" * 120 + "\n"
        report_text += f"{'Total General':<20}{total_elementos_general:<20}$ {total_vf_a_comp_general:<20,.2f}"
        report_text += f"{int(total_count_pagado_isagen):<20}{int(total_count_pagado_or):<20}{int(total_count_rechazada):<20}\n\n"

        # Añadir el resumen general por estado de pago
        report_text += "Totales por Estado de Pago:\n\n"
        report_text += f"{'Estado':<20}{'Cantidad':<20}{'Suma VF_A_COMP':<20}\n"
        report_text += "-" * 60 + "\n"
        report_text += f"{'PAGADO_ISAGEN':<20}{total_count_pagado_isagen:<20}$ {total_pagado_isagen:<20,.2f}\n"
        report_text += f"{'PAGADO_OR':<20}{total_count_pagado_or:<20}$ {total_pagado_or:<20,.2f}\n"
        report_text += f"{'RECHAZADA':<20}{total_count_rechazada:<20}$ {total_rechazada:<20,.2f}\n\n\n"

        ##REPORTE COMPENASCIONES
        informe = search_data("final", None, None)
        
        # Agregar una columna de "mes" para agrupar por mes
        informe['mes'] = informe['FACTURACION_ISAGEN'].dt.to_period('M').dt.to_timestamp()
        
        tabla_pivot = pd.pivot_table(
            informe, 
            values='VF_A_COMP', 
            index='OPERADOR_RED', 
            columns='mes', 
            aggfunc='sum', 
            fill_value=0
        )
        
        tabla_pivot = tabla_pivot.sort_index(axis=1, ascending=False)
        
        # Calcular el total por fecha y añadirlo como fila
        tabla_pivot.loc['Total'] = tabla_pivot.sum(axis=0)
        
        # Calcular el total por fecha y añadirlo como fila
        tabla_pivot_formateada = tabla_pivot.applymap(lambda valor: f"${valor:,.0f}")
        tabla_pivot_formateada.loc['Total'] = tabla_pivot.loc['Total'].apply(lambda valor: f"${valor:,.0f}")
        
        tabla_pivot_formateada = tabla_pivot_formateada.iloc[:, :7]
        
        report_text += f'Reporte de Fronteras Aprovadas\n{tabla_pivot_formateada}'
        
        # Insertar el texto en el widget Text
        self.report_text_widget.insert(tk.END, report_text)
        self.report_text_widget.config(state="normal")
    
    def save_decisions(self):
        # Obtener la fecha actual
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        
        # Guardar el estado anterior de 'PAGADO_ISAGEN'
        pagado_isagen_anterior = self.df['PAGADO_ISAGEN'].copy()
        pagado_or_anterior = self.df['PAGADO_OR'].copy()
        
        # Actualizar la columnas del DataFrame con los valores de los checkboxes
        self.df['RECHAZADA'] = [var.get() for var in self.check_rechazada_vars]
        self.df['PAGADO_ISAGEN'] = [var.get() for var in self.check_isagen_vars]
        self.df['PAGADO_OR'] = [var.get() for var in self.check_or_vars]
        
        # Actualizar la columna 'OBSERVACIONES' del DataFrame con los valores de las entradas de texto
        self.df['OBSERVACIONES'] = [entry.get() for entry in self.observation_vars]
        
        # Actualizar columna facturación con fecha actual
        self.df['FACTURACION_ISAGEN'] = pd.to_datetime(self.df['FACTURACION_ISAGEN'], errors='coerce').dt.strftime('%d/%m/%Y')
        self.df['FACTURACION_ISAGEN'] = self.df.apply(
            lambda row: fecha_actual if pagado_isagen_anterior[row.name] == 0 and row['PAGADO_ISAGEN'] == 1
                        else None if pagado_isagen_anterior[row.name] == 1 and row['PAGADO_ISAGEN'] == 0
                        else row['FACTURACION_ISAGEN'], axis=1
        )
        self.df['FACTURACION_ISAGEN'] = self.df['FACTURACION_ISAGEN'].apply(lambda x: None if pd.isna(x) else x)
             
        self.df['FACTURACION_OR'] = pd.to_datetime(self.df['FACTURACION_OR'], errors='coerce').dt.strftime('%d/%m/%Y')
        self.df['FACTURACION_OR'] = self.df.apply(
            lambda row: fecha_actual if pagado_or_anterior[row.name] == 0 and row['PAGADO_OR'] == 1
                        else None if pagado_or_anterior[row.name] == 1 and row['PAGADO_OR'] == 0
                        else row['FACTURACION_OR'], axis=1
        )
        self.df['FACTURACION_OR'] = self.df['FACTURACION_OR'].apply(lambda x: None if pd.isna(x) else x)

        self.check_instance.send_data()
        count = self.check_instance.send_data()
        if count:
            messagebox.showinfo("Éxito", f"{count} Datos Actualizados con éxito")
        else:
            messagebox.showinfo("Error", f"No se pudo agregar datos")

    def export_data(self):
        df = self.check_instance.df_actualizaciones
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                    filetypes=[("Archivos Excel", "*.xlsx")],
                                                    title="Guardar archivo Excel")
        if file_path:
            try:
                df.to_excel(file_path, index=False)
                tk.messagebox.showinfo("Éxito", "Los resultados se han exportado a Excel exitosamente.")
            except Exception as e:
                tk.messagebox.showerror("Error", f"No se pudo guardar el archivo Excel. Error: {e}")

    def export_csv(self, date):
        total_dfs = create_file(date)
        verificar = export_files(total_dfs)
        if verificar:
            messagebox.showinfo("Éxito", f"Archivos guardados en: {verificar}")
        else:
            messagebox.showerror("Error", "No se guardaron archivos porque no se seleccionó una carpeta.")

    def resource_path(self, relative_path):
        """ Devuelve la ruta absoluta del recurso, ya sea en desarrollo o en el ejecutable """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))  # _MEIPASS es el directorio temporal del ejecutable
        return os.path.join(base_path, relative_path)
    