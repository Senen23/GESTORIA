import tkinter as tk
from tkinter import filedialog, messagebox
from dataread.data_manager import manage_data
import os
import pandas as pd

def leer_carpeta(file_type):
    # Crear un DataFrame vacío para almacenar los datos combinados
    df = pd.DataFrame()
    
    # Solicitar al usuario seleccionar una carpeta
    folder_path = filedialog.askdirectory()
    if not folder_path:
        # Si no se selecciona una carpeta, simplemente salir
        return
    
    # Obtener todos los archivos .xlsx en la carpeta seleccionada
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xlsx')]
    
    
    # Extraer solo el nombre de cada archivo
    file_names = [os.path.basename(file) for file in files]
    file_list = "\n".join(file_names)

    # Mostrar un cuadro de diálogo OK/Cancel con los archivos listados por línea
    confirmation = messagebox.askokcancel(
        "Confirmar archivos", 
        f"Se encontraron los siguientes archivos:\n\n{file_list}\n\n¿Deseas proceder con la carga?")    
    if not confirmation:
        return 
    
    if not files:
        # Si no se encuentran archivos .xlsx, mostrar una advertencia
        messagebox.showwarning("Warning", "No se encontraron archivos .xlsx en esta carpeta.")
        return
    
    # Leer y concatenar los archivos .xlsx
    for file_path in files:
        try:
            # Leer el archivo .xlsx en un DataFrame
            file_df = pd.read_excel(file_path)
            
            #organizar la información leida
            file_df = manage_data(file_df,file_type)
            
            # Concatenar el contenido del archivo con el DataFrame existente
            df = pd.concat([df, file_df], ignore_index=True)

            
        except Exception as e:
            # Manejar cualquier error al leer el archivo
            messagebox.showerror("Error", f"No se pudo leer el archivo {file_path}: {e}")
            
    if file_type in ["tc1"]:
        while not df.columns.empty and df.columns[-1] != "Capacidad contrato de respaldo 3":
            last_col_name = df.columns[-1]
            df = df.drop(columns=[last_col_name]) 
            
    return df

def leer_archivo(file_type):
    # Solicitar al usuario seleccionar un archivo .xlsx
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    
    if file_path:
        # Extraer solo el nombre de cada archivo
        file_name = os.path.basename(file_path)

        #pedir confirmacion del archivo cargado
        confirmation = messagebox.askokcancel(
            "Confirmar archivos", 
            f"Se encontraron los siguientes archivos:\n\n{file_name}\n\n¿Deseas proceder con la carga?")    
        if not confirmation:
            return 
    
        try:
            # Leer el archivo .xlsx en un DataFrame
            df = pd.read_excel(file_path)
            #organizar la información leida
            df = manage_data(df,file_type)
            
            return df
        except Exception as e:
            # Manejar cualquier error al leer el archivo
            messagebox.showerror("Error", f"No se pudo leer el archivo {file_path}: {e}")
            return
    else:
        # Si no se selecciona un archivo, retornar
        return