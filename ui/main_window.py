import tkinter as tk
import os
import sys
from tkinter import ttk, PhotoImage
from ui.check_carga import CheckCargasTab
from ui.load_data_tab import LoadDataTab
from ui.search_data_tab import SearchTab
from ui.math_tab import MathTab
from ui.check_tab import CheckTab
from ui.add_user_tab import AddUserWindow

class MainApp:
    def __init__(self, root, role):
        self.root = root
        self.root.state('zoomed')
        self.root.title("APLICACION COMPENSACIONES")
        self.root.configure(bg='#191970')  # Color de fondo claro

        # Definir los estilos
        style = ttk.Style()
        style.configure('TNotebook', background='#191970', padding=10)
        style.configure('TNotebook.Tab', padding=10)
        style.configure('TLabel', foreground='#ffffff', font=('Helvetica', 14))
        style.configure('TFrame', background='#ffffff')
        style.configure("TButton", compound="left")

        #imagen
        ruta_imagen = self.resource_path("images/logo.png")
        ruta_usuario = self.resource_path("images/usuario.png")
        self.logo_image = PhotoImage(file=ruta_imagen)
        self.usuario_image = PhotoImage(file=ruta_usuario)
        
        # Guardar la referencia de la imagen en el objeto raíz
        root.logo_image_ref = self.logo_image
        root.usuario_image_ref = self.usuario_image
        
        # Colocar la imagen en la parte superior izquierda
        self.image_label = ttk.Label(root, image=self.logo_image, background='#191970')
        self.image_label.place(x=0, y=0, anchor='nw')  # Ancla en la parte superior izquierda.

        # Título
        self.title_label = ttk.Label(root, background='#191970', text="", font=('Helvetica', 18, 'bold'))
        self.title_label.pack(pady=20)

        # Texto de bienvenida en la parte superior derecha
        self.welcome_label = ttk.Label(root, background='#191970', text="Bienvenido\nAplicación Compensaciones", font=('Helvetica', 14, 'bold'))
        self.welcome_label.place(x=root.winfo_screenwidth() - 20, y=20, anchor='ne')  # Ancla en la parte superior derecha

        if role == "admin":
            # Botón de gestionar usuarios
            self.edit_user_button = ttk.Button(root, text="Gestionar Usuarios", image=self.usuario_image, command= self.open_add_user_window)  
            self.edit_user_button.place(x=self.image_label.winfo_width() + 250, y=20, anchor='nw') 
        
        # Crear un Notebook para las pestañas
        self.notebook = ttk.Notebook(root, style='TNotebook')
        self.notebook.pack(pady=10, expand=True, fill='both')

        # Crear las pestañas
        self.tab_add = ttk.Frame(self.notebook, style='TFrame')
        self.tab_math = ttk.Frame(self.notebook, style='TFrame')
        self.tab_check = ttk.Frame(self.notebook, style='TFrame')
        self.tab_search = ttk.Frame(self.notebook, style='TFrame')
        self.tab_check_cargas = ttk.Frame(self.notebook, style='TFrame')

        # Añadir pestañas al Notebook
        self.notebook.add(self.tab_add, text="Agregar Información", padding=10)
        self.notebook.add(self.tab_math, text="Calcular Compensaciones", padding=10)
        self.notebook.add(self.tab_check, text="Verificar Compensaciones", padding=10)
        self.notebook.add(self.tab_search, text="Buscar Información", padding=10)
        self.notebook.add(self.tab_check_cargas, text="Verificar Datos Cargados", padding=10)
        
        # Instanciar las clases
        self.load_data_tab = LoadDataTab(self.tab_add)
        self.math_tab = MathTab(self.tab_math)
        self.check_tab = CheckTab(self.tab_check)
        self.search_tab = SearchTab(self.tab_search)
        self.check_cargas_tab = CheckCargasTab(self.tab_check_cargas)
        
    def resource_path(self, relative_path):
        """ Devuelve la ruta absoluta del recurso, ya sea en desarrollo o en el ejecutable """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__)) 
        return os.path.join(base_path, relative_path)
    
    def open_add_user_window(self):
        AddUserWindow(self.root)
