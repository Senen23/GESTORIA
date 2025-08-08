import cx_Oracle
from tkinter import messagebox
from database.connection import get_connection

def update_data(df, file_type):
    try:
        if df.empty:
            return None
        
        # Convertir los nombres de las columnas del DataFrame a mayúsculas
        df.columns = df.columns.str.upper()
        
        # Crear el DSN y conectar a la base de datos
        connection = get_connection()
        cursor = connection.cursor()
        
        # Establecer el formato de fecha para la sesión
        cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'DD/MM/YYYY'")
        
        # Determinar la tabla de destino y las claves primarias en función del tipo de archivo
        table_mappings = {
            "tc1": {"table_name": "CS_TC1", "primary_keys": ["SIC", "FECHA"]},
            "cs2": {"table_name": "CS_CS2", "primary_keys": ["FECHA_APLICACION", "CODIGO_OPERADOR_RED", "NIU", "CODIGO_CAUSA", "NI"]},
            "zref": {"table_name": "CS_CONSUMO", "primary_keys": ["NUMFACTURA"]},
            "diug_fiug": {"table_name": "CS_DIUGFIUG", "primary_keys": ["AÑO", "CODIGO_OPERADOR_RED", "NIVEL_TENSION", "GRUPO_CALIDAD"]},
            "dt": {"table_name": "CS_DT", "primary_keys": ["CODIGO_OPERADOR_RED", "NIVEL_TENSION", "FECHA"]},
            "%t": {"table_name": "CS_PORCENTAJE_T", "primary_keys": ["AÑO"]},
            "or": {"table_name": "CS_OPERADOR_RED", "primary_keys": ["CODIGO"]},
            "instalaciones": {"table_name": "CS_INSTALACIONES", "primary_keys": ["SIC", "FECHA"]},
            "final": {"table_name": "CS_TABLA_FINAL", "primary_keys": ["SIC", "FECHA"]}
        }
        
        mapping = table_mappings.get(file_type.lower())
        
        if not mapping:
            raise ValueError("Invalid file type")
        
        table_name = mapping["table_name"]
        primary_keys = mapping["primary_keys"]

        # Convertir las claves primarias a mayúsculas para coincidir con el DataFrame
        primary_keys = [key.upper() for key in primary_keys]

        # Verificar que las columnas de las claves primarias estén en el DataFrame
        for key in primary_keys:
            if key not in df.columns:
                raise ValueError(f"La columna clave primaria '{key}' no está presente en el DataFrame.")
        
        # Obtener los nombres de las columnas de la tabla
        cursor.execute(f"""
            SELECT COLUMN_NAME 
            FROM ALL_TAB_COLUMNS 
            WHERE TABLE_NAME = :table_name
            ORDER BY COLUMN_ID
        """, table_name=table_name.upper())
        
        columns = [row[0].upper() for row in cursor]  # Convertir todas las columnas de la tabla a mayúsculas

        count = 0
        
        set_clause = ', '.join([f'"{col}" = :{i+1}' for i, col in enumerate(columns) if col not in primary_keys])
        where_clause = ' AND '.join([f'"{key}" = :{len(columns) - len(primary_keys) + i + 1}' for i, key in enumerate(primary_keys)])
        
        update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

        count = 0
        # Iterar sobre cada fila del DataFrame
        for idx, row in df.iterrows():
            # Intentar actualizar cada fila
            update_data = list(row[col] for col in columns if col not in primary_keys) + list(row[key] for key in primary_keys)
            cursor.execute(update_sql, update_data)
            count += 1
            # Si no se actualizó ninguna fila, insertar el registro con todos los valores, incluidas las claves primarias
            if cursor.rowcount == 0:
                insert_columns = ', '.join([f'"{col}"' for col in columns])
                insert_values = ', '.join([f':{i+1}' for i in range(len(columns))])
                insert_sql = f"INSERT INTO {table_name} ({insert_columns}) VALUES ({insert_values})"
                
                # Insertar con todos los valores, incluidas las claves primarias
                insert_data = [row[col] for col in columns]
                cursor.execute(insert_sql, insert_data)
        
        connection.commit()
        
        return count

    except cx_Oracle.IntegrityError as e:
        error_code, = e.args[0].code,
        if error_code == 1:  # ORA-00001: Violación de clave primaria
             messagebox.showerror("Error", "Estás intentando actualizar un dato con una clave que no existe en la tabla.")
        else:
             messagebox.showerror("Error",f"Ocurrió un error de integridad en la base de datos: {e}")
    except cx_Oracle.DatabaseError as e:
         messagebox.showerror("Error",f"Ocurrió un error en la base de datos: {e}")
    except ValueError as ve:
         messagebox.showerror("Error",f"Error de valor: {ve}")
    except Exception as ex:
         messagebox.showerror("Error",f"Ocurrió un error: {ex}")
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        connection.close()
