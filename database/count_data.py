import cx_Oracle
import pandas as pd
from database.connection import get_connection

def count_data():
    try:
        # Obtener la conexión a la base de datos
        connection = get_connection()
        cursor = connection.cursor()
        
        query = """
        SELECT 
            TO_CHAR(FECHA, 'MM/YYYY') AS MES,
            'tc1' AS TIPO_ARCHIVO,
            COUNT(*) AS CANTIDAD
        FROM CS_TC1
        GROUP BY TO_CHAR(FECHA, 'MM/YYYY')

        UNION ALL

        SELECT 
            TO_CHAR(FECHA_APLICACION, 'MM/YYYY') AS MES,
            'cs2' AS TIPO_ARCHIVO,
            COUNT(*) AS CANTIDAD
        FROM CS_CS2
        GROUP BY TO_CHAR(FECHA_APLICACION, 'MM/YYYY')

        UNION ALL 

        SELECT
            TO_CHAR(FECHAINICIAL, 'MM/YYYY') AS MES,
            'zref' AS TIPO_ARCHIVO,
            COUNT(*) AS CANTIDAD
        FROM CS_CONSUMO
        GROUP BY TO_CHAR(FECHAINICIAL, 'MM/YYYY')

        UNION ALL

        SELECT
            TO_CHAR(FECHA, 'MM/YYYY') AS MES,
            'dt' AS TIPO_ARCHIVO,
            COUNT(*) AS CANTIDAD
        FROM CS_DT
        GROUP BY TO_CHAR(FECHA, 'MM/YYYY')
        
        UNION ALL

        SELECT
            TO_CHAR(FECHA, 'MM/YYYY') AS MES,
            'instalaciones' AS TIPO_ARCHIVO,
            COUNT(*) AS CANTIDAD
        FROM CS_INSTALACIONES
        GROUP BY TO_CHAR(FECHA, 'MM/YYYY')

        UNION ALL

        SELECT
            TO_CHAR(FECHA, 'MM/YYYY') AS MES,
            'tabla final' AS TIPO_ARCHIVO,
            COUNT(*) AS CANTIDAD
        FROM CS_TABLA_FINAL
        GROUP BY TO_CHAR(FECHA, 'MM/YYYY')
        ORDER BY MES
        """
        
        # Ejecutar la consulta y obtener los datos
        cursor.execute(query)
        results = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        df = pd.DataFrame(results, columns=['FECHA', 'TIPO_ARCHIVO', 'CANTIDAD'])
        
        # Pivotar los datos para tener una columna por TIPO_ARCHIVO
        df = df.pivot(index='FECHA', columns='TIPO_ARCHIVO', values='CANTIDAD').fillna(0)

        # Restablecer el índice para incluir la fecha como una columna
        df = df.reset_index()

        # Calcular la fila TOTAL
        total_row = df.sum(numeric_only=True)
        total_row['FECHA'] = 'TOTAL'
        total_row_df = pd.DataFrame([total_row])

        # Usar pd.concat en lugar de append
        df = pd.concat([df, total_row_df], ignore_index=True)
        return df

    except cx_Oracle.DatabaseError as e:
        print(f"Error al conectar con la base de datos: {e}")
        return pd.DataFrame()  # Retornar un DataFrame vacío en caso de error

    except Exception as e:
        print(f"Se ha producido un error: {e}")
        return pd.DataFrame()  

    finally:
        # Asegurarse de cerrar el cursor y la conexión
        cursor.close()
        connection.close()
