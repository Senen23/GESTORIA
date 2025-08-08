import cx_Oracle
import pandas as pd
from datetime import datetime, timedelta
from database.connection import get_connection
from tkinter import messagebox
from dateutil.relativedelta import relativedelta

def get_fechas(fecha):
    try:
        # Calcular la fecha 11 meses antes
        date_ini = datetime.strptime(fecha, '%d/%m/%Y').replace(day=1) - timedelta(days=11*30)
        date_ini = date_ini.strftime("%d/%m/%Y")
        # Calcula el valor de 'date_fin' como un mes antes de 'date'
        date_fin = datetime.strptime(fecha, '%d/%m/%Y') - relativedelta(months=1)
        date_fin = date_fin.strftime("%d/%m/%Y")
        
        # Obtener la conexión a la base de datos
        connection = get_connection()
        cursor = connection.cursor()
        
        # Crear la consulta SQL con las fechas dinámicas
        query = f"""
        SELECT DISTINCT FECHA
        FROM CS_TABLA_FINAL
        WHERE FECHA BETWEEN TO_DATE('{date_ini}', 'DD/MM/YYYY') 
                        AND TO_DATE('{date_fin}', 'DD/MM/YYYY')
        """
        
        # Ejecutar la consulta
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        df = pd.DataFrame(results, columns=columns)
        
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