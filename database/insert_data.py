import cx_Oracle
from tkinter import messagebox
from database.connection import get_connection

# 👈 importa el adaptador
from convertir_zref import cargar_zref

def insert_data(df, file_type):
    try:
        if df.empty:
            return None
        else:
            # 👈 si es ZREF, pasamos el DataFrame por el adaptador
            if file_type.lower() == "zref":
                df = cargar_zref(df)

            # Crear el DSN y conectar a la base de datos
            connection = get_connection()
            cursor = connection.cursor()
            
            # Establecer el formato de fecha para la sesión
            cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'DD/MM/YYYY'")
            
            # Determinar la tabla de destino en función del tipo de archivo
            table_mappings = {
                "tc1": "CS_TC1",
                "cs2": "CS_CS2",
                "zref": "CS_CONSUMO",
                "diug_fiug": "CS_DIUGFIUG",
                "dt": "CS_DT",
                "%t": "CS_PORCENTAJE_T",
                "or": "CS_OPERADOR_RED",
                "instalaciones": "CS_INSTALACIONES",
                "final": "CS_TABLA_FINAL"
            }
            
            table_name = table_mappings.get(file_type.lower())
            
            if not table_name:
                raise ValueError("Invalid file type")
            
            # Obtener los nombres de las columnas de la tabla
            cursor.execute(f"""
                SELECT COLUMN_NAME 
                FROM ALL_TAB_COLUMNS 
                WHERE TABLE_NAME = :table_name
                ORDER BY COLUMN_ID
            """, table_name=table_name.upper())
            
            # Extraer los nombres de las columnas
            columns = [row[0] for row in cursor]
            
            # Construir la consulta SQL de inserción
            column_list = ', '.join([f'"{col}"' for col in columns])
            placeholders = ', '.join([f':{i+1}' for i in range(len(df.columns))])
            insert_sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
            
            # Convertir el DataFrame a una lista de listas
            data = df[df.columns].values.tolist()

            # Ejecutar la consulta para cada fila del DataFrame
            cursor.executemany(insert_sql, data)
            rows = cursor.rowcount
            
            # Confirmar los cambios
            connection.commit()
            
            return rows

    except cx_Oracle.IntegrityError as e:
        error_code, = e.args[0].code,
        if error_code == 1:  # ORA-00001: Violación de clave primaria
            messagebox.showerror("Error de clave primaria", "Error: Estás intentando agregar un dato que ya existe en la tabla.")
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
