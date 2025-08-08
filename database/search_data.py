import cx_Oracle
import pandas as pd
from datetime import datetime
from database.connection import get_connection
from tkinter import messagebox

def search_data(file_type, date_option, date_value):
    try:
        # Obtener la conexión a la base de datos
        connection = get_connection()
        cursor = connection.cursor()
        
        if file_type:
            
            # Determinar la tabla y la columna de fecha basada en el tipo de archivo
            table_mappings = {
                "tc1": ("CS_TC1", "FECHA"),
                "cs2": ("CS_CS2", "FECHA_APLICACION"),
                "zref": ("CS_CONSUMO", "FECHAINICIAL"),
                "%t": ("CS_PORCENTAJE_T", None),
                "or": ("CS_OPERADOR_RED", None),
                "dt": ("CS_DT", "FECHA"),
                "diug_fiug": ("CS_DIUGFIUG", "AÑO"),
                "instalaciones": ("CS_INSTALACIONES","FECHA"),
                "final": ("CS_TABLA_FINAL","FECHA"),
                "verificar":("CS_VERIFICAR",None),
                "correo": ("CS_CORREOS", None)
            }
            
            if date_value == None:
                #Obtener el nombre de la tabla 
                table_name, date_col = table_mappings.get(file_type.lower(), (None, None))
                if not table_name:
                    raise ValueError("Tipo de archivo no válido")
                
                query = f"SELECT * FROM {table_name} WHERE 1=1 "
                
                cursor.execute(query)
                # Obtener los nombres de las columnas
                columns = [desc[0] for desc in cursor.description]
                # Obtener los resultados de la consulta
                results = cursor.fetchall()
                # Convertir los resultados a un DataFrame de pandas
                df = pd.DataFrame(results, columns=columns)
                
            else:    
                # Obtener el nombre de la tabla y la columna de fecha correspondiente al tipo de archivo
                table_name, date_col = table_mappings.get(file_type.lower(), (None, None))
                if not table_name:
                    raise ValueError("Tipo de archivo no válido")

                # Crear la consulta SQL inicial
                query = f"SELECT * FROM {table_name} WHERE 1=1 "
                params = {}

                if date_col:
                    if file_type == "diug_fiug":
                        # Buscar directamente el valor en la columna para "diug_fiug"
                        query += f"AND {date_col} = :value "
                        params['value'] = date_value
                    elif file_type in ["%t", "or"]:
                        # No se requiere búsqueda por fecha para "%t" y "or"
                        pass
                    elif date_option in ["month", "year"]:
                        try:
                            # Parsear la fecha de entrada asumiendo el formato DD/MM/YYYY
                            date_obj = datetime.strptime(date_value, "%d/%m/%Y")
                            year = date_obj.year
                            month = date_obj.month if date_option == "month" else None
                        except ValueError:
                            raise ValueError("Fecha no válida. Debe estar en formato DD/MM/YYYY.")

                        if date_option == "month":
                            # Agregar condiciones para buscar por mes y año
                            query += f"AND EXTRACT(MONTH FROM {date_col}) = :month_value AND EXTRACT(YEAR FROM {date_col}) = :year_value "
                            params['month_value'] = month
                            params['year_value'] = year
                        elif date_option == "year":
                            # Agregar condición para buscar por año
                            query += f"AND EXTRACT(YEAR FROM {date_col}) = :year_value "
                            params['year_value'] = year
            
                # Ejecutar la consulta con los parámetros proporcionados
                cursor.execute(query, params)
                # Obtener los nombres de las columnas
                columns = [desc[0] for desc in cursor.description]
                # Obtener los resultados de la consulta
                results = cursor.fetchall()
                # Convertir los resultados a un DataFrame de pandas
                df = pd.DataFrame(results, columns=columns)
                
            return df
        
        else:
            date_obj = datetime.strptime(date_value, "%m/%Y")
            formatted_date_value = date_obj.strftime("%m/%Y")

            #INSTALACIONES
            query = """
            SELECT "SIC", "INSTALACION"
            FROM "CS_INSTALACIONES"
            WHERE "FECHA" = TO_DATE(:date_value, 'MM/YYYY')
            """
            cursor.execute(query, date_value=formatted_date_value)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            instalaciones = pd.DataFrame(results, columns=columns)
            
            # Consulta para TC1
            query = """
            SELECT "NIU", "SIC", "Codigo_transformador_3", "Nivel_de_Tension_3", "Grupo_de_calidad", "Tipo_de_conexion_3", "Codigo_circuito_o_linea_3"
            FROM "CS_TC1"
            WHERE "FECHA" = TO_DATE(:date_value, 'MM/YYYY')
            """
            cursor.execute(query, date_value=formatted_date_value)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            tc1 = pd.DataFrame(results, columns=columns)

            # CS2
            query = """
            SELECT "DIU", "DIUM", "FIU", "FIUM", "CODIGO_CAUSA", "NI", "DI", "NIU", "CODIGO_OPERADOR_RED" 
            FROM CS_CS2 
            WHERE FECHA_APLICACION = TO_DATE(:date_value, 'MM/YYYY')
            """
            cursor.execute(query, date_value=formatted_date_value)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            cs2 = pd.DataFrame(results, columns=columns)

            # ZREF
            query = """
            SELECT "TOTALENERGIAAKWH", "INSTALACION", "NOMBREDELCLIENTE", "OPERADORRED", "CODIGOSIC"
            FROM CS_CONSUMO 
            WHERE FECHAINICIAL = TO_DATE(:date_value, 'MM/YYYY')
            """
            cursor.execute(query, date_value=formatted_date_value)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            zref = pd.DataFrame(results, columns=columns)

            # OR
            query = """
            SELECT "CODIGO", "ABREVIATURA" 
            FROM CS_OPERADOR_RED 
            """
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            operador_red = pd.DataFrame(results, columns=columns)

            # DT
            query = """
            SELECT "CODIGO_OPERADOR_RED", "NIVEL_TENSION", "VALOR"
            FROM CS_DT
            WHERE FECHA = TO_DATE(:date_value, 'MM/YYYY')
            """
            cursor.execute(query, date_value=formatted_date_value)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            dt = pd.DataFrame(results, columns=columns)

            # DIUG_FIUG
            if date_obj.year < 2024:
                año = "2019 - 2023"
            else:
                año = str(date_obj.year)

            query = """
            SELECT "CODIGO_OPERADOR_RED", "NIVEL_TENSION", "GRUPO_CALIDAD", "DIUG", "FIUG"
            FROM "CS_DIUGFIUG"
            WHERE "AÑO" = :año
            """
            cursor.execute(query, año=año)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            diugFiug = pd.DataFrame(results, columns=columns)

            # %T
            año_actual = str(date_obj.year)
            año_anterior = str(date_obj.year - 2)

            query = """
            SELECT "PORCENTAJE", "AÑO"
            FROM "CS_PORCENTAJE_T"
            WHERE "AÑO" IN (:año_actual, :año_anterior)
            """
            cursor.execute(query, año_actual=año_actual, año_anterior=año_anterior)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            porcentaje_t = pd.DataFrame(results, columns=columns)
            
            return tc1, cs2, zref, operador_red, dt, diugFiug, porcentaje_t, instalaciones
            
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