import win32com.client as win32
import os
import tkinter as tk
import time
import pywintypes
import pandas as pd
import sys
from tkinter import messagebox, filedialog, ttk, PhotoImage, simpledialog
from tkcalendar import DateEntry
from database.search_data import search_data
from dataread.mail_manager import mail_manager
from datacalculation.statistics import statistics
from dataread.data_manager import manage_type
from database.update_data import update_data
from datacalculation.do_calculations import DoMath
from pandastable import Table

class MathTab:
    def __init__(self, tab):
        self.tab = tab
        self.create_math_tab()

    def create_math_tab(self):
        self.main_frame = ttk.Frame(self.tab)
        self.main_frame.pack(fill='both', expand=True)

        # Cargar la imagen para los botones
        ruta_calculadora = self.resource_path("images/calculadora.png")
        ruta_mail = self.resource_path("images/mail.png")
        self.mail_image = PhotoImage(file=ruta_mail)
        self.calculadora_image = PhotoImage(file=ruta_calculadora)

        # Crear un canvas con fondo blanco y sin borde
        self.canvas = tk.Canvas(self.main_frame, bg="white", bd=0, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Crear una scrollbar vertical y asociarla al self.canvas
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Crear un frame dentro del self.canvas
        self.frame = tk.Frame(self.canvas, bg="white")

        # Añadir el frame al self.canvas
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # Configurar el self.canvas para que se ajuste al tamaño del frame
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("all", width=e.width))

        # Vincular el evento de la rueda del ratón
        self.frame.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Contenido del Frame
        title_label = ttk.Label(self.frame, background='#ffffff', foreground='#000000', text="Realizar cálculos", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        self.date_entry = DateEntry(self.frame, width=12, background='darkblue', 
                                    foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.date_entry.pack(pady=10)

        # Crear un frame para contener ambos botones #
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(pady=10)
        
        # Botón "buscar"
        self.confirm_button = ttk.Button(self.button_frame, text="Calcular compensaciones", image=self.calculadora_image,
                                         command=self.start)
        self.confirm_button.pack(side='left')
        
        self.export_button = ttk.Button(self.button_frame, text="Enviar correos a ORs", image=self.mail_image,
                                      state="disabled")
        self.export_button.pack(side='left')
        self.export_button.config(command=lambda: self.send_mails(), state="normal")
        
        self.confirm_button2= ttk.Button(self.button_frame, text="Calcular compensaciones por or", image=self.calculadora_image,
                                 command=self.startOp)
        self.confirm_button2.pack(side='left')
        
        # Agregar cuadro de texto debajo de los botones (inicialmente invisible)
        self.text_box = tk.Entry(self.frame, state="disabled", 
                                 borderwidth=0, highlightthickness=0, foreground='#000000',
                                 font=("Helvetica", 14))
        self.text_box.pack(anchor='center', fill='x')
        
        # Subtítulo de la Tabla
        table_title_label = ttk.Label(self.frame, background='#ffffff', text="Fronteras a Compensar:", font=('Arial', 12, 'bold'))
        table_title_label.pack(pady=5, fill='x', expand=True)

        # Frame para mostrar el DataFrame
        self.table_frame = ttk.Frame(self.frame)
        self.table_frame.pack(side='left', pady=10, fill='both', expand=True)

        # Frame para los cálculos matemáticos
        self.stats_frame = ttk.Frame(self.frame)
        self.stats_frame.pack(side='right', pady=10, fill='both', expand=True)

    def start(self):
        date = self.date_entry.get_date()
        formatted_date = date.strftime("%m/%Y")

        self.load_and_show_data(formatted_date, None)
        
    def startOp(self):
        # Obtener la fecha seleccionada en el DateEntry
        date = self.date_entry.get_date()
        formatted_date = date.strftime("%m/%Y")

        # Mostrar un cuadro de diálogo para ingresar el código del operador
        operador = simpledialog.askstring(
            "Agregar Código del Operador", 
            "Agrega el código del operador.\nSi no lo conoces, consúltalo en la pestaña 'Buscar Datos',\nseleccionando la opción de 'Operador Red'."
        )

        if operador:
            # Llamar a la función `load` pasando el código del operador y la fecha
            self.load_and_show_data(formatted_date, operador)
        else:
            messagebox.showwarning("Advertencia", "No se ingresó ningún código de operador. Por favor, inténtalo nuevamente.")
    
    def load_and_show_data(self, formatted_date, operador):
        try:
            math_instance = DoMath()
            df = math_instance.extract_data(formatted_date)
            
            if operador:
                operador = float(operador) 
                df = df[df['operador_red'] == operador]
            
            df = manage_type(df, "final")
            
            # Mostrar el DataFrame
            self.show_table(df[df['vf_a_comp'] > 0])

            #mostrar estadísticas
            self.show_statistics(df)
            
            self.load_data(df)
            
            #Exportar a excel
            if not df.empty:
                save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")], title="Guardar informe Completo")
                if save_path:
                    df.to_excel(save_path, index=False)
                    messagebox.showinfo("Guardado", f"Archivo guardado exitosamente en {save_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los datos: {str(e)}")

    def load_data(self, df):
        try:
            if not df.empty:
                # Mostrar el aviso de confirmación
                respuesta = messagebox.askyesno(
                    "Aviso de Sobreescritura", 
                    "Si ya realizaste cálculos anteriormente, estos serán sobrescritos.\n"
                    "Si ya hiciste chequeo de compensaciones, se te van a poner de nuevo en 0.\n"
                    "¿Quieres continuar?"
                )
                if not respuesta:
                    return  # Salir si el usuario selecciona 'No'                
        
                numfilas = update_data(df, "final")
                df.columns = df.columns.str.lower()
                if numfilas:
                    messagebox.showinfo("Éxito", f"{numfilas} Datos cargados con éxito")
            else:
                messagebox.showerror("Error", "No hay datos a enviar")   
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_table(self, df):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.table = Table(self.table_frame, dataframe=df)
        self.table.show()

    def show_statistics(self, df):
        # Limpiar las estadísticas anteriores
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # Calcular estadísticas
        data = statistics(df)

        # Crear un Text widget para mostrar las estadísticas y permitir la copia
        text_widget = tk.Text(self.stats_frame, wrap="word", height=20, width=60)
        text_widget.insert("1.0", data)
        text_widget.configure(state='disabled')  # Deshabilitar edición
        text_widget.pack(padx=10)
        
    def send_mails(self):
        
        data = search_data("final", None, None)
        data = data[(data['VF_A_COMP'] > 0) & (data['PAGADO_ISAGEN'] == 0) & (data['RECHAZADA'] != 1)].reset_index(drop=True)
        data = data = data.sort_values(by='FECHA', ascending=False).reset_index(drop=True)
        
        dic_compensaciones = mail_manager(data)
        correos = search_data("correo", None, None)
        
        self.text_box.config(state="normal")  # Habilitar el cuadro de texto
        self.text_box.insert(0, f"Ejecutando...")
        self.text_box.update()
        
        # Diccionario de traducción de meses
        meses_espanol = {
            'January': 'enero', 'February': 'febrero', 'March': 'marzo', 'April': 'abril',
            'May': 'mayo', 'June': 'junio', 'July': 'julio', 'August': 'agosto',
            'September': 'septiembre', 'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
        }

        for operador, data in dic_compensaciones.items():
            total = data['VF_A_COMP'].replace({'\$': '', ',': ''}, regex=True).astype(float).sum()
            total =  "$   {:,.0f}".format(total)
            
            # Crea el archivo excel temporal
            attachment_path = os.path.join(os.getcwd(), f'{operador}.xlsx')
            data.to_excel(attachment_path, index=False)
            
            #saca la fecha
            fecha = data['FECHA'].unique()
            fecha = pd.to_datetime(fecha[0])
            mes = meses_espanol[fecha.strftime('%B')]
            # Crear la lista con el mes y el año
            resultado = [mes, fecha.year]
            
            #saca los correos
            correos_op = correos[correos['ABREVIACION'].isin(data['OPERADOR_RED'].unique())]
            correos_list = ';'.join(correos_op['CORREO'].tolist()) if not correos_op.empty else ''
            
            # Muestra la ventana del mail
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)
            mail.To = correos_list
            mail.Subject = f'XX: XXXXX-XXXXXX - Compensaciones CREG 015 - {operador} - {resultado[0]} {resultado[1]}'
            mail.HTMLBody = f"""
            <p><b>Buenas tardes,</b></p>
            <p>
            De acuerdo a lo establecido en la resolución CREG 015/2018, los niveles de calidad individual del servicio en los SDL se identificarán a través de los indicadores DIU y FIU. 
            Estos indicadores se utilizarán para identificar los niveles mínimos de calidad que deben garantizar los OR. 
            La comparación entre los mínimos garantizados y la calidad individual brindada dará lugar a la aplicación del esquema de compensaciones descrito en el numeral 5.2.4.3. de la resolución CREG 015/2018.
            </p>
            <p>
            De acuerdo a lo establecido en el numeral 5.2.16 Transición literal e) de la resolución CREG 015/2018 el cual dice:
            </p>
            <p><i>“…………….e) A partir del mes siguiente al de entrada en vigencia de la resolución en la que se le aprueban los ingresos al OR, el comercializador deberá calcular y aplicar las compensaciones de cada mes del periodo facturado. 
            Las compensaciones pendientes de los meses transcurridos desde enero de 2019 deberán incluirse una a una en las facturas emitidas a partir del mes siguiente a que hayan sido reportadas, hasta que todas sean reconocidas.………”.</i></p>
            <p>
            Lo que indica, las compensaciones que apliquen deben ser canceladas por parte de los OR después de la aprobación de cargos.
            </p>
            <p>De acuerdo a lo anterior, ISAGEN realizó el cálculo de compensaciones y el resultado es:</p>

            {data.to_html(index=False)}

            <p>Lo cual dio un total de: {total}</p>
            
            <p><b>Por favor confirmar la aplicación del cobro compensación en la factura de SDL del mes de {resultado[0]} de {resultado[1]}.</b></p>
            
            <p><span style="color:blue;">
            <b>Saludos,<br>
            BREYNER ESCAMILLA CHITO<br>
            Servicios y Operaciones Comerciales<br>
            ISAGEN S.A E.S.P.<br></b>
            Carrera 30 No. 10C - 280 Transversal inferior, Medellín<br>
            (574) 3257832<br>
            Cel: 3167401700<br>
            brescamilla@isagen.com.co<br>
            </span></p>
            """
            
            mail.Attachments.Add(attachment_path)
            mail.Display()  # Abre la ventana del correo
            mail_window = outlook.ActiveWindow()
            
            self.text_box.delete(0, tk.END)
            self.text_box.insert(0, f"Esperando que el correo para {operador} sea enviado o cerrado...")
            self.text_box.update()
            # Ciclo para monitorear si el correo fue enviado o la ventana fue cerrada
            while True:
                try:
                    # Si el correo fue cerrado sin ser enviado
                    if outlook.ActiveWindow() != mail_window:
                        self.text_box.delete(0, tk.END)
                        self.text_box.insert(0, f"INFO, El correo para {operador} fue cerrado o fue enviado.")
                        self.text_box.update()
                        break
        
                    time.sleep(2)  # Espera 2 segundos y vuelve a comprobar
                
                except pywintypes.com_error as e:
                    self.text_box.delete(0, tk.END)
                    self.text_box.insert(0, f"ERROR: No se pudo verificar el estado del correo para {operador}.")
                    self.text_box.update()
                    
            # Eliminar el archivo temporal una vez enviado o cerrado
            if os.path.exists(attachment_path):
                os.remove(attachment_path)

        self.text_box.delete(0, tk.END)
        self.text_box.insert(0, f"EXITO, Se gestionaron ya todos los correos.")
        self.text_box.update()

    def on_mousewheel(self, event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def resource_path(self, relative_path):
        """ Devuelve la ruta absoluta del recurso, ya sea en desarrollo o en el ejecutable """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))  # _MEIPASS es el directorio temporal del ejecutable
        return os.path.join(base_path, relative_path)