import cx_Oracle
import pandas as pd
from datetime import datetime
from database.connection import get_connection
from tkinter import messagebox

def sum_data(columna, fecha_ini, fecha_fin):
    try:
        # Obtener la conexión a la base de datos
        connection = get_connection()
        cursor = connection.cursor()
        
        query = f"""
        SELECT SIC, SUM({columna}) AS suma_total 
        FROM CS_TABLA_FINAL 
        WHERE fecha >= TO_DATE('{fecha_ini}', 'MM/YYYY')
        AND fecha <= TO_DATE('{fecha_fin}', 'MM/YYYY')
        GROUP BY SIC
        """
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        df = pd.DataFrame(results, columns=columns)
        
        columna_minuscula = columna.lower()  # Convertir el nombre de la columna a minúsculas
        df.columns = ['sic', f't{columna_minuscula}']
        
        return df
        
    except cx_Oracle.DatabaseError as e:
        # Manejo de errores de la base de datos
        error_msg = f"Error en la base de datos: {str(e)}"
        messagebox.showerror("Error en la base de datos", error_msg)
        
    except ValueError as e:
        # Manejo de errores de valor
        error_msg = f"Error de valor: {str(e)}"
        messagebox.showerror("Error de valor", error_msg)
        
    except Exception as e:
        # Manejo general de cualquier otro tipo de excepción
        error_msg = f"Ocurrió un error inesperado: {str(e)}"
        messagebox.showerror("Error inesperado", error_msg)
        
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        connection.close()