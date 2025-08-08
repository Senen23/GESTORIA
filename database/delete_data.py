import cx_Oracle
from tkinter import messagebox
from database.connection import get_connection

def delete_data(file_type, op, date):
    try:
        # Obtener la conexión a la base de datos
        connection = get_connection()
        cursor = connection.cursor()
        
        table_mappings = {
            "tc1": ("CS_TC1", ("FECHA")), 
            "cs2": ("CS_CS2", ("FECHA_APLICACION", "CODIGO_OPERADOR_RED")),
            "zref": ("CS_CONSUMO", ("FECHAINICIAL")),
            "%t": ("CS_PORCENTAJE_T", ("AÑO")),
            "or": ("CS_OPERADOR_RED", ("CODIGO")),
            "dt": ("CS_DT", ("FECHA", "CODIGO_OPERADOR_RED")),
            "diug_fiug": ("CS_DIUGFIUG", ("AÑO", "CODIGO_OPERADOR_RED")),
            "instalaciones": ("CS_INSTALACIONES", ("FECHA")),
            "final": ("CS_TABLA_FINAL", ("FECHA")),
            "verificar": ("CS_VERIFICAR", (None))
        }
        
         # Verificar si el file_type es válido
        if file_type not in table_mappings:
            raise ValueError(f"El tipo de archivo {file_type} no es válido.")
        
        # Obtener la tabla y columnas correspondientes
        table_name, columns =  table_mappings.get(file_type.lower(), (None, None))
        
        if columns is None:
            raise ValueError(f"No se puede eliminar datos de la tabla {table_name}.")
        
        # Crear la cláusula WHERE basada en las columnas
        if file_type in ["tc1", "zref", "%t", "or", "final", "instalaciones"]:
            if "AÑO" == columns:
                # Eliminación por año
                date = "'"+str(date)+"'"
                where_clause = f"{columns} = {date}"
                
            elif "CODIGO" == columns:
                where_clause = f"{columns} = {op}"
                 
            else:
                # Eliminación solo por fecha
                date = "'"+str(date)+"'"
                where_clause = f"{columns} = {date}"
                
        elif file_type in ["cs2", "dt", "diug_fiug"]:
            date = "'"+str(date)+"'"
            if "AÑO" in columns[0]:
                # Eliminación por año y código
                where_clause = f"{columns[0]} = {date} AND {columns[1]} = {op}"
                
            else:
                # Eliminación por fecha y código
                where_clause = f"{columns[0]} = {date} AND {columns[1]} = {op}"
                
                
        else:
            raise ValueError(f"Las columnas para el tipo de archivo {file_type} no están bien definidas.")
        
        # Construir la consulta SQL
        sql_query = f"DELETE FROM {table_name} WHERE {where_clause}"
        print(sql_query)
        # Ejecutar la consulta
        cursor.execute(sql_query)
        
        rows = cursor.rowcount
        
        # Confirmar la transacción
        connection.commit()
        
        return rows
    
    except cx_Oracle.IntegrityError as e:
        error_code = e.args[0].code  # Extraer el código de error
        if error_code == 2292:  # ORA-02292: Restricción de clave externa violada
            messagebox.showerror("Error de integridad referencial", "No se puede eliminar el dato porque está relacionado con otra tabla.")
        else:
            messagebox.showerror("Error de integridad", f"Ocurrió un error de integridad en la base de datos: {e}")
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Error de base de datos", f"Ocurrió un error en la base de datos: {e}")
    except ValueError as ve:
        messagebox.showerror("Error de valor", f"Error de valor: {ve}")
    except Exception as ex:
        messagebox.showerror("Error", f"Ocurrió un error: {ex}")
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        connection.close()
        