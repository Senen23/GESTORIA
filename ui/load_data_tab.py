from datetime import datetime
import tkinter as tk
import pandas as pd
import os
import sys
from tkinter import ttk, PhotoImage
from tkinter import messagebox
from database.delete_data import delete_data
from database.count_data import count_data
from database.search_data import search_data
from dataread.data_manager import actualizar_info, manage_type
from database.insert_data import insert_data
from dataread.data_read import *
from tkcalendar import DateEntry

class LoadDataTab:
    def __init__(self, tab):
        self.tab = tab
        self.df_retornar = pd.DataFrame()
        self.button_folder = None
        self.button_file = None
        self.create_add_tab()

    def create_add_tab(self):
        style =  ttk.Style()
        style.configure("add.TFrame", background="#F1F0FE")
        
        self.tab.grid_columnconfigure(0, weight=1)  
        self.tab.grid_columnconfigure(1, weight=1)    
        
        add_label = ttk.Label(self.tab, background='#ffffff', foreground='#000000', text="Carga de Información", font=('Arial', 16, 'bold'))
        add_label.grid(row=0, column=0, pady=10, sticky='ewns') 
        
        delete_label = ttk.Label(self.tab, background='#ffffff', foreground='#000000', text="Eliminar Informacíon", font=('Arial', 16, 'bold'))
        delete_label.grid(row=0, column=1, pady=10, sticky='ewns')
        
        # Cargar la imagen para los botones
        ruta_delete = self.resource_path("images/delete.png")
        ruta_save2 = self.resource_path("images/save.2.png")
        ruta_save = self.resource_path("images/save.1.png")
        ruta_folder = self.resource_path("images/folder.png")
        ruta_file = self.resource_path("images/file.png")
        self.delete_image = PhotoImage(file=ruta_delete)
        self.save2_image = PhotoImage(file=ruta_save2)
        self.save_image = PhotoImage(file=ruta_save)
        self.folder_image = PhotoImage(file=ruta_folder)
        self.file_image = PhotoImage(file=ruta_file)
        
        # Definir los tipos de archivo y el texto de los botones
        self.file_types = {
            "tc1": "Formato TC1",
            "cs2": "Formato CS2",
            "zref": "Liquidacion ZREF",
            "dt": "Cargo Dt",
            "instalaciones": "Instalaciones",
            "diug_fiug": "Metas DIUG_FIUG",
            "%t": "porcentaje(%)t",
            "or": "Crear OPERADOR RED"
        }

        # Crear un marco para los botones
        self.buttons_frame = ttk.Frame(self.tab, style="add.TFrame", padding=20)
        self.buttons_frame.grid(row=1, column=0, columnspan=1, padx=10, pady=10, sticky='w')

        # Crear botones para cada tipo de archivo y organizarlos en una cuadrícula
        self.buttons = {}
        row = 0
        column = 0
        self.esp = "     "
        esp = "                                   "
        self.button_width = 25 
        
        for file_type, text in self.file_types.items():
            if row < 5:
                # Crear botón con texto e imagen
                button = ttk.Button(self.buttons_frame, text=self.esp + text + esp, image=self.save_image, compound='left', command=lambda ft=file_type: self.handle_button_click(ft))

                # Configurar tamaño uniforme para todos los botones
                button.config(width=self.button_width)
                button.grid(row=row, column=column, padx=10, pady=5, sticky='nsw') 

                # Añadir el botón al diccionario
                self.buttons[file_type] = button
            else:
                # Crear botón con texto e imagen
                button = ttk.Button(self.buttons_frame, text=self.esp + text + esp, image=self.save2_image, compound='left', command=lambda ft=file_type: self.handle_button_click(ft))

                # Configurar tamaño uniforme para todos los botones
                button.config(width=self.button_width)
                button.grid(row=row, column=column, padx=10, pady=5, sticky='nsw') 

                # Añadir el botón al diccionario
                self.buttons[file_type] = button
            row += 1     
            
            
        # Crear botones para cargar carpeta o archivo
        self.button_folder = ttk.Button(self.buttons_frame, text=self.esp+"Carga Masiva"+self.esp, image=self.folder_image)
        self.button_file = ttk.Button(self.buttons_frame, text=self.esp+"Carga por Archivo"+self.esp, image=self.file_image)
        
        self.button_folder.config(width=self.button_width, state='disabled')
        self.button_file.config(width=self.button_width, state='disabled')
        self.button_folder.grid(row=0, column=1, padx=5, pady=5, sticky='wn')  # Colocar en la primera columna de la nueva fila
        self.button_file.grid(row=1, column=1, padx=5, pady=5, sticky='wn')
        
        # Expansión horizontal para las columnas
        self.buttons_frame.grid_columnconfigure(0, weight=1)  # Asegurar que los botones se expandan horizontalmente

        self.create_delete_tab()
        
    def handle_button_click(self, file_type):
        self.set_buttons_state(False)
        self.add_data(file_type)
        self.set_buttons_state(True)

    def set_buttons_state(self, state):
        for button in self.buttons.values():
            button.config(state=tk.NORMAL if state else tk.DISABLED)

    def add_data(self, file_type):
        try:
            df = self.load_data(file_type)
            if df is None:
                messagebox.showerror("Error", "Ocurrió un problema, vuelva a seleccionar una opción")
                return

            if file_type in ["tc1", "cs2", "instalaciones"]:
                fecha = self.ask_for_date()
                if fecha:
                    df['fecha'] = fecha
                    if file_type == "cs2":
                        column_names = ["DIU", "DIUM", "FIU", "FIUM", "fecha", "OPERADOR_RED", "NIU", "ID Mercado", "ID_CAUSAL", "CANT_CAUSAL", "DURACION_CAUSAL"]
                        df = df[column_names]
                        df = df.rename(columns={"OPERADOR_RED": "CODIGO_OPERADOR_RED"})
                else:
                    return
            
            df = actualizar_info(df, file_type)
            
            df = manage_type(df, file_type)
            
            numfilas = insert_data(df, file_type)
            
            self.mostrar_informe(file_type)
            
            if numfilas:
                messagebox.showinfo("Éxito", f"{numfilas} Datos cargados con éxito")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")

    def load_data(self, file_type):
        self.button_folder.config(state='normal', command=lambda ft=file_type: self.confirm_folder(ft))
        self.button_file.config(state='normal', command=lambda ft=file_type: self.confirm_file(ft))
        
        #mostrar informe        
        self.mostrar_informe(file_type)
        
        # Lógica adicional para gestionar las ventanas ocultas (si es necesario)
        if file_type in ["tc1", "cs2", "dt"]:
            self.hidden_window = tk.Toplevel()
            self.hidden_window.withdraw()

            self.hidden_window.wait_window()
            self.button_folder.config(state='disabled')
            self.button_file.config(state='disabled')

            return self.df_retornar

        elif file_type in ["zref", "instalaciones"]:
            self.button_folder.config(state='disabled')
            self.button_file.config(state='disabled')
            return leer_archivo(file_type)

        elif file_type in ["%t", "or", "diug_fiug"]:
            self.button_folder.config(state='disabled')
            self.button_file.config(state='disabled')
            return self.mostrar_formulario(file_type)

        else:
            raise ValueError("Tipo de archivo no reconocido")

    def mostrar_informe(self, file_type):
        if not hasattr(self, 'text_widget'):
            # Si no existe, crear el Text widget
            self.text_widget = tk.Text(self.buttons_frame, wrap="word", height=20, width=60)
            self.text_widget.grid(row=2, column=1, rowspan=6, padx=5, pady=5, sticky='wn')
        
        # Limpiar el Text widget antes de insertar el nuevo texto
        self.text_widget.config(state='normal')  # Habilitar edición temporalmente para actualizar el contenido
        self.text_widget.delete("1.0", tk.END)  # Limpiar el contenido actual

        # Crear el nuevo informe
        datos = count_data()
        #datos['FECHA'] = pd.to_datetime(datos['FECHA'], format='%m/%Y')
        
        datos = datos[['FECHA','tc1','cs2','zref','dt','instalaciones']].reset_index(drop=True)
        datos['FECHA'] = pd.to_datetime(datos['FECHA'], format='%m/%Y', errors='coerce')
        datos = datos.sort_values(by='FECHA', ascending=False)
        datos['FECHA'] = datos['FECHA'].dt.strftime('%m/%Y').fillna('Total')
        
        text = f'Estás agregando información en {file_type}\n\n'
        text += f'Resumen de registros cargados:\n\n{datos.to_string(index=False)}'

        # Insertar el nuevo contenido en el Text widget
        self.text_widget.insert("1.0", text)
        self.text_widget.configure(state='disabled')  # Deshabilitar la edición de nuevo

    def confirm_file(self, file_type):
        self.df_retornar = leer_archivo(file_type)
        self.hidden_window.destroy()

    def confirm_folder(self, file_type):
        self.df_retornar = leer_carpeta(file_type)
        self.hidden_window.destroy()
    
    def mostrar_formulario(self, file_type):
        form_window = tk.Toplevel(self.tab)
        form_window.title("Formulario de Datos")

        datos = {}
        entry_widgets = {}

        def enviar_datos():
            try:
                if file_type == "%t":
                    anio = int(entry_widgets['anio'].get())
                    if anio < 2000 or anio > 2100:
                        raise ValueError("El año debe estar entre 2000 y 2100.")
                    valor = float(entry_widgets['valor'].get())
                    datos["Año"] = [anio]
                    datos["Valor"] = [valor]

                elif file_type == "or":
                    datos["Código"] = [int(entry_widgets['codigo'].get())]
                    datos["Código_v1"] = [entry_widgets['codigo_v1'].get()]
                    datos["Código_v2"] = [entry_widgets['codigo_v2'].get()]
                    datos["Abreviatura"] = [entry_widgets['abreviatura'].get()]
                    datos["Operador_red"] = [entry_widgets['operador_red'].get()]

                elif file_type == "diug_fiug":
                    datos["AÑO"] = [entry_widgets['anio'].get()]
                    datos["CODIGO_OPERADOR_RED"] = [int(entry_widgets['codigo_operador_red'].get())]
                    datos["NIVEL_TENSION"] = [int(entry_widgets['nivel_tension'].get())]
                    datos["GRUPO_CALIDAD"] = [int(entry_widgets['grupo_calidad'].get())]
                    datos["DIUG"] = [float(entry_widgets['diug'].get())]
                    datos["FIUG"] = [float(entry_widgets['fiug'].get())]

                form_window.destroy()

            except ValueError as e:
                messagebox.showerror("Error", f"Formato inválido: {e}")
                return

        if file_type == "%t":
            self.create_form_fields(form_window, {
                'anio': "Año (YYYY):",
                'valor': "Valor (float):"
            }, entry_widgets)
        elif file_type == "or":
            self.create_form_fields(form_window, {
                'codigo': "Código (int):",
                'codigo_v1': "Código_v1 (string):",
                'codigo_v2': "Código_v2 (string):",
                'abreviatura': "Abreviatura (string):",
                'operador_red': "Operador_red (string):"
            }, entry_widgets)
        elif file_type == "diug_fiug":
            self.create_form_fields(form_window, {
                'anio': "AÑO (VARCHAR2(20 BYTE)):",
                'codigo_operador_red': "CODIGO_OPERADOR_RED (NUMBER):",
                'nivel_tension': "NIVEL_TENSION (NUMBER):",
                'grupo_calidad': "GRUPO_CALIDAD (NUMBER):",
                'diug': "DIUG (NUMBER):",
                'fiug': "FIUG (NUMBER):"
            }, entry_widgets)

        btn_enviar = ttk.Button(form_window, text="Enviar Datos", command=enviar_datos)
        btn_enviar.grid(row=len(entry_widgets), column=1, pady=10)

        form_window.wait_window()
        return pd.DataFrame(datos)

    def create_form_fields(self, form_window, fields, entry_widgets):
        for i, (field, label_text) in enumerate(fields.items()):
            label = ttk.Label(form_window, text=label_text, foreground='black')
            label.grid(row=i, column=0, padx=5, pady=5, sticky='w')

            entry = ttk.Entry(form_window)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            entry_widgets[field] = entry

    def resource_path(self, relative_path):
        """ Devuelve la ruta absoluta del recurso, ya sea en desarrollo o en el ejecutable """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))  # _MEIPASS es el directorio temporal del ejecutable
        return os.path.join(base_path, relative_path)

    def ask_for_date(self):
        # Crear una nueva ventana emergente para seleccionar la fecha
        date_window = tk.Toplevel(self.tab)
        date_window.title("Seleccionar Fecha")
        
        # Label para instruir al usuario
        label = ttk.Label(date_window, text="Seleccione la fecha:", foreground='#000000', font=('Arial', 12))
        label.grid(row=0, column=0, padx=10, pady=10)
        
        # Calendar DateEntry para elegir la fecha
        date_entry = DateEntry(date_window, width=12, background='darkblue',
                            foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        date_entry.grid(row=1, column=0, padx=10, pady=10)
        
        selected_date = [None]  # Usamos una lista mutable para almacenar la fecha seleccionada
        
        def submit_date():
            selected_date[0] = date_entry.get_date()  # Obtener la fecha seleccionada
            date_window.destroy()  # Cerrar la ventana emergente

        # Botón para confirmar la selección de la fecha
        submit_button = ttk.Button(date_window, text="Confirmar", command=submit_date)
        submit_button.grid(row=2, column=0, padx=10, pady=10)
        
        # Esperar a que la ventana de fecha se cierre
        date_window.wait_window()
        
        return selected_date[0]
    
    def create_delete_tab(self):
        # Definir los tipos de archivo y el texto de los botones
        self.delete_file_types = {
            "tc1": "Formato TC1",
            "cs2": "Formato CS2",
            "zref": "Liquidacion ZREF",
            "dt": "Cargo Dt",
            "instalaciones": "Instalaciones",
            "diug_fiug": "Metas DIUG_FIUG",
            "%t": "porcentaje(%)t",
            "or": "Eliminar OPERADOR RED"
        }

        # Crear un marco para los botones
        self.delete_buttons_frame = ttk.Frame(self.tab, style="add.TFrame", padding=20)
        self.delete_buttons_frame.grid(row=1, column=1, columnspan=1, padx=10, pady=10, sticky='w')
        
        self.delete_buttons = {}
        row = 0
        column = 0
        esp = "                                   "
        for file_type, text in self.delete_file_types.items():
            # Crear botón con texto e imagen
            button = ttk.Button(self.delete_buttons_frame, text=self.esp + text + esp, image=self.delete_image, compound='left', command=lambda ft=file_type: self.show_delete_options(ft))

            # Configurar tamaño uniforme para todos los botones
            button.config(width=self.button_width)
            button.grid(row=row, column=column, padx=10, pady=5, sticky='nsw') 

            # Añadir el botón al diccionario
            self.delete_buttons[file_type] = button
            row += 1  
            
        self.delete_options_frame = ttk.Frame(self.delete_buttons_frame, style="add.TFrame", padding=20)
        self.delete_options_frame.grid(row=0, column=1, rowspan=8, padx=10, pady=10, sticky='w')
        
    def show_delete_options(self, file_type):
        # Limpiar el contenido actual del marco de filtros
        for widget in self.delete_options_frame.winfo_children():
            widget.destroy()

        label = ttk.Label(self.delete_options_frame, text= f"{file_type}", foreground='#000000')
        label.grid(row=0, column=0, sticky='s')
        
        operator_combobox = None
        date_entry = None
        
        if file_type in ["cs2", "dt", "diug_fiug"]:
             # Selector de fecha
            date_label = ttk.Label(self.delete_options_frame, text="Selecciona la Fecha:", foreground='#030303')
            date_label.grid(row=1, column=0, sticky='s')

            date_entry = DateEntry(self.delete_options_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
            date_entry.grid(row=2, column=0, padx=10, pady=5)

            # Menú desplegable para operadores
            operator_label = ttk.Label(self.delete_options_frame, text="Selecciona el Operador:", foreground='#030303')
            operator_label.grid(row=3, column=0, sticky='s')

            df = search_data("or", None, None)
            operators = df["CODIGO"].tolist()

            operator_combobox = ttk.Combobox(self.delete_options_frame, values=operators, state="readonly")
            operator_combobox.grid(row=4, column=0, padx=10, pady=5)

            llenar = ttk.Label(self.delete_options_frame, text="\n\n\n\n\n\n\n\n\n")
            llenar.grid(row=5, rowspan=4)
            
        if file_type == "or":
            # Menú desplegable para operadores
            operator_label = ttk.Label(self.delete_options_frame, text="Selecciona el Operador:", foreground='#030303')
            operator_label.grid(row=1, column=0, sticky='s')

            df = search_data("or", None, None)
            operators = df["CODIGO"].tolist()

            operator_combobox = ttk.Combobox(self.delete_options_frame, values=operators, state="readonly")
            operator_combobox.grid(row=2, column=0, padx=10, pady=5)
            
            llenar = ttk.Label(self.delete_options_frame, text="\n\n\n\n\n\n\n\n\n")
            llenar.grid(row=5, rowspan=4)
        
        else:
            date_label = ttk.Label(self.delete_options_frame, text="Selecciona la Fecha:", foreground='#030303')
            date_label.grid(row=1, column=0, sticky='s')

            date_entry = DateEntry(self.delete_options_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
            date_entry.grid(row=2, column=0, padx=10, pady=5)
            
            llenar = ttk.Label(self.delete_options_frame, text="\n\n\n\n\n\n\n\n\n")
            llenar.grid(row=5, rowspan=4)

        delete_button = ttk.Button(self.delete_options_frame, text="Eliminar", 
                           command=lambda: self.delete_info(
                               int(operator_combobox.get()) if operator_combobox else None, 
                               date_entry.get_date() if date_entry else None,
                               file_type
                           ))
        delete_button.grid(row=5, column=0, padx=10, pady=10)
        
    def delete_info(self, op, date, file_type):
        
        fecha = date.strftime("%d/%m/%Y") if date else None
        
        if file_type in ["%t", "diug_fiug"]:
            fecha = date.year
        
        # Crear el mensaje de confirmación dinámico
        confirmation_message = f"Estás seguro que quieres eliminar datos de {file_type}?"
        if fecha:
            confirmation_message += f"\nFecha seleccionada: {fecha}"
        if op:
            confirmation_message += f"\nOperador seleccionado: {op}"
        
        confirm = messagebox.askyesno("Confirmar eliminación", confirmation_message)

        # Si el usuario confirma, proceder con la eliminación
        if confirm:
            # Llamar a la función que realmente elimina los datos
            count = delete_data(file_type, op, fecha)

            # Mostrar mensajes dependiendo de si se eliminó algo o no
            if count:
                messagebox.showinfo("Éxito", f"Se eliminaron {count} registros de {file_type}.")
            else:
                messagebox.showwarning("Advertencia", "No se eliminaron registros.")
        else:
            messagebox.showinfo("Cancelado", "La operación de eliminación ha sido cancelada.")
            
        self.mostrar_informe(file_type)
        