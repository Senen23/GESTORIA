import tkinter as tk
import pandas as pd
import os
import sys
from tkinter import ttk, filedialog, messagebox, PhotoImage
from tkcalendar import DateEntry
from database.update_data import update_data
from database.search_data import search_data 
from database.count_data import count_data
from pandastable import Table, TableModel
from dataread.data_manager import manage_type

class SearchTab:
    def __init__(self, tab):
        self.tab = tab
        self.file_type = None
        self.full_results_df = None  # Almacena el DataFrame completo
        self.filtered_df = None
        self.filter_widgets = []  # Almacena los filtros dinámicos
        self.create_load_tab()

    def create_load_tab(self):
        # Configurar el tab para que se expanda en ambas direcciones
        self.tab.grid_rowconfigure(0, weight=1)
        self.tab.grid_columnconfigure(0, weight=1)
        
        # Crear un Canvas que contendrá el main_frame y la barra de desplazamiento
        self.canvas = tk.Canvas(self.tab, bg="white", bd=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas.grid_rowconfigure(0, weight=1)
        self.canvas.grid_columnconfigure(0, weight=1)
        
        # Barra de desplazamiento vertical
        self.scrollbar = ttk.Scrollbar(self.tab, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame dentro del canvas
        self.main_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Vincular el redimensionamiento del canvas
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Cargar las imágenes 
        ruta_search = self.resource_path("images/search.png")
        ruta_excel = self.resource_path("images/excel.png")
        ruta_save = self.resource_path("images/save.png")
        ruta_filter = self.resource_path("images/filter.png")
        ruta_plus = self.resource_path("images/plus.png")

        self.filter_image = PhotoImage(file=ruta_filter)
        self.plus_image = PhotoImage(file=ruta_plus)
        self.save_image = PhotoImage(file=ruta_save)
        self.excel_image = PhotoImage(file=ruta_excel)
        self.search_image = PhotoImage(file=ruta_search)

        # Frame de botones
        button_frame = ttk.Frame(self.main_frame, style="add.TFrame", padding=20)
        button_frame.grid(row=0, column=0, rowspan=10, sticky="ns", padx=10, pady=10)

        search_label = ttk.Label(button_frame, text="Buscar Información", background='#ffffff',  foreground='#000000', font=('Arial', 16, 'bold'))
        search_label.grid(row=0, column=0, pady=10, sticky='w')

        # Opciones para seleccionar el tipo de archivo
        file_types = {
            "tc1": "Buscar en TC1",
            "cs2": "Buscar en CS2",
            "zref": "Buscar en ZREF",
            "diug_fiug": "Buscar en DIUG_FIUG",
            "dt": "Buscar en DT",
            "%t": "Buscar en %T",
            "or": "Buscar en OPERADOR RED",
            "instalaciones": "Buscar en INSTALACIONES",
            "final": "Buscar Informe Compensaciones",
            "contar_datos": "Buscar cantidad de datos por tabla",
        }

        self.file_type_var = tk.StringVar()
        self.file_type_var.set("tc1")  # Valor predeterminado

        # Usar grid para organizar los RadioButtons
        row = 1
        column = 0
        for file_type, text in file_types.items():
            radio = ttk.Radiobutton(button_frame, text=text, variable=self.file_type_var, value=file_type)
            radio.grid(row=row, column=column, sticky='w', padx=5, pady=5)
            row += 1

        search_button = ttk.Button(button_frame, text="Buscar", width=20, image=self.search_image, command=self.perform_search)
        search_button.grid(row=1, column=1, columnspan=2, pady=5, sticky="ew")

        self.add_filter_button = ttk.Button(button_frame, text="Agregar filtro", image=self.plus_image, command=self.add_filter, state='disable')
        self.add_filter_button.grid(row=2, column=1, columnspan=2, pady=5, sticky="ew")

        self.apply_filter_button = ttk.Button(button_frame, text="Filtrar", image=self.filter_image, command=self.apply_filters, state='disable')
        self.apply_filter_button.grid(row=3, column=1, columnspan=2, pady=5, sticky="ew")

        self.export_button = ttk.Button(button_frame, text="Exportar", image=self.excel_image, command=self.export_to_excel, state='disable')
        self.export_button.grid(row=4, column=1, columnspan=2, pady=5, sticky="ew")

        self.update_button = ttk.Button(button_frame, text="Guardar Cambios", image=self.save_image, command=self.update_data, state='disable')
        self.update_button.grid(row=5, column=1, columnspan=2, pady=5, sticky="ew")

        # Marco para filtros dinámicos
        self.dynamic_options_frame = ttk.Frame(button_frame)
        self.dynamic_options_frame.grid(column=0, columnspan=2, pady=10, sticky="nsew")
        
        #frame vacio para organizar espacio
        self.void_frame = ttk.Frame(self.main_frame)
        self.void_frame.grid(column=1)
        
        # Frame para la tabla
        self.table_frame = ttk.Frame(self.main_frame, style="add.TFrame", padding=20)
        self.table_frame.grid(row=0, column=2, rowspan=14, columnspan=5, pady=10, sticky="nsew")
        
    def perform_search(self):
        self.clear_dynamic_widgets()

        try:
            # Realiza la búsqueda de datos
            file_type = self.file_type_var.get()
            if file_type == 'contar_datos':
                full_results_df = count_data()
            else:    
                full_results_df = search_data(file_type, None, None)

            if full_results_df.empty:
                tk.messagebox.showinfo("Sin Resultados", "No se encontraron datos.")
            else:
                # Almacenar y mostrar el DataFrame
                self.full_results_df = full_results_df
                visible_results_df = self.full_results_df.head(200)
                self.show_table(visible_results_df)

                # Habilitar botones después de una búsqueda exitosa
                self.apply_filter_button.config(state='normal')
                self.export_button.config(state='normal')
                self.add_filter_button.config(state='normal')
                self.update_button.config(state='normal')

        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo realizar la búsqueda. Error: {e}")

    def show_table(self, df):
        # Usa una referencia persistente para la tabla
        if hasattr(self, 'pt'):
            # Si la tabla ya existe, actualiza su dataframe usando TableModel
            self.pt.updateModel(TableModel(df))
            self.pt.redraw()
        else:
            # Si la tabla no existe, créala        
            self.pt = Table(self.table_frame, dataframe=df, width=700)
            self.pt.show()
            self.pt.grid(sticky="nsew")
            
    def clear_dynamic_widgets(self):
        for widget in self.dynamic_options_frame.winfo_children():
            widget.destroy()

    def add_filter(self):
        # Crear un marco para un nuevo filtro
        filter_row = ttk.Frame(self.dynamic_options_frame)
        filter_row.grid(sticky="ew", pady=5)

        # Crear un StringVar para la columna seleccionada
        selected_column = tk.StringVar(value=self.full_results_df.columns[0])
        column_menu = ttk.OptionMenu(filter_row, selected_column, *self.full_results_df.columns)
        column_menu.grid(row=0, column=0, padx=5)

        filter_value = ttk.Entry(filter_row)
        filter_value.grid(row=0, column=1, padx=5)
        filter_value.insert(0, "Ingresa valor")

        # Botón para eliminar filtro
        remove_button = ttk.Button(filter_row, text="Eliminar", command=lambda: self.remove_filter(filter_row))
        remove_button.grid(row=0, column=2, padx=5)

        # Almacenar los widgets
        self.filter_widgets.append((selected_column, filter_value, filter_row))

    def remove_filter(self, filter_row):
        # Eliminar la fila de widgets de la interfaz y de la lista
        for i, (col, val, row) in enumerate(self.filter_widgets):
            if row == filter_row:
                self.filter_widgets.pop(i)
                row.destroy()
                break

    def apply_filters(self):
        # Aplicar los filtros acumulativamente
        filtered_df = self.full_results_df.copy()

        for selected_column, filter_value, _ in self.filter_widgets:
            col = selected_column.get()
            val = filter_value.get()
            filtered_df = self.apply_filter(filtered_df, col, val)
    
        # Guardar el DataFrame filtrado
        self.filtered_df = filtered_df.reset_index(drop=True)

        # Actualizar la tabla con el DataFrame filtrado
        self.show_table(filtered_df.head(200))

    def apply_filter(self, df, col, val):
        # Si la columna es de tipo fecha, convertirla a datetime para permitir el filtrado
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col], dayfirst=True)

        # Aplicar el filtro dinámico basado en el tipo de la columna
        if pd.api.types.is_numeric_dtype(df[col]):
            # Si la columna es numérica, buscar si el valor ingresado es numérico
            try:
                val = float(val)
                df = df[df[col] == val]
            except ValueError:
                pass
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            # Si la columna es de tipo fecha, convertir el valor ingresado y filtrar
            try:
                val = pd.to_datetime(val, dayfirst=True)
                df = df[df[col] == val]
            except ValueError:
                pass
        else:
            # Filtrar texto u otras columnas no numéricas
            df = df[df[col].astype(str).str.contains(val, na=False)]
        
        return df

    def export_to_excel(self):
        # Exportar el DataFrame completo 
        if self.filtered_df is None:
            self.filtered_df = self.full_results_df
        
        if self.filtered_df is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                    filetypes=[("Archivos Excel", "*.xlsx")],
                                                    title="Guardar archivo Excel")
            if file_path:
                try:
                    self.filtered_df.to_excel(file_path, index=False)
                    tk.messagebox.showinfo("Éxito", "Los resultados se han exportado a Excel exitosamente.")
                except Exception as e:
                    tk.messagebox.showerror("Error", f"No se pudo guardar el archivo Excel. Error: {e}")
        else:
            tk.messagebox.showwarning("Sin Datos", "No hay datos para exportar.")

    def update_data(self):
        try:
            # Captura el DataFrame modificado desde la tabla pandastable
            updated_df = self.pt.model.df
            
            updated_df = updated_df.reset_index(drop=True)
            
            updated_df =  manage_type(updated_df, self.file_type_var.get())
            
            # Verifica si el DataFrame actualizado no está vacío
            if updated_df is not None and not updated_df.empty:
                count = update_data(updated_df, self.file_type_var.get())  # Envía el DataFrame actualizado a la función update_data
                messagebox.showinfo("Éxito", f"{count} Datos Actualizados con éxito")
            else:
                messagebox.showwarning("Sin Datos", "No hay datos para actualizar.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar los datos: {e}")

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def resource_path(self, relative_path):
        """ Devuelve la ruta absoluta del recurso, ya sea en desarrollo o en el ejecutable """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))  # _MEIPASS es el directorio temporal del ejecutable
        return os.path.join(base_path, relative_path)