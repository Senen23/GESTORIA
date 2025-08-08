import pandas as pd
import re
from datetime import datetime
from database.search_data import search_data

def manage_data(df,file_type):
    #control de los dataframes
    if file_type in ["zref"]:
        df = df.iloc[:, :51]
        #verifica que no hayan datos regados en el excel y los elimina
        if df['Num. Factura'].isna().any():
            df = df.loc[:df['Num. Factura'].isna().idxmax()-1] 
        if "Impuesto Guajira" in df.columns:
            df = df.drop("Impuesto Guajira", axis=1)
        
        return df
    
    elif file_type in["tc1"]:
        
        if df.columns[2].startswith('Unnamed:'):
            # Encuentra la primera fila en la tercera columna que no sea nula
            fila_encabezado = df.iloc[:, 2].dropna().iloc[0]
            
            if pd.notna(fila_encabezado):
                # Asignar los nombres de columna encontrados en la fila válida
                nueva_filas_encabezado = df.iloc[df.iloc[:, 2].dropna().index[0]].tolist()
                df.columns = nueva_filas_encabezado
                
                # Eliminar las filas usadas para nombres de columna
                df = df.iloc[df.iloc[:, 2].dropna().index[0] + 1:].reset_index(drop=True)
        
        #s eliminia la columna item, que no necesitamos su informacion
        df = df.drop(df.columns[[0]], axis='columns')
        df = df.iloc[:, :109]
        
        df.columns.values[0] = 'SIC'
        df.columns.values[2] = '# Cuenta'  

        #elimina columnas sobrantes a la derecha, !si se cambia el formato toca editarlo, por la ultima columna valida
        last_col_name = df.columns[-1]
        if last_col_name != "Capacidad contrato de respaldo 3":
            df = df.drop(columns=[last_col_name])
        
        if df['SIC'].isna().any():
            df = df.loc[:df['SIC'].isna().idxmax()-1]
        
        if 'NIT' not in df.columns:
            # Insertamos una columna 'NIT' con valores NaN
            df['NIT'] = pd.NA

        # Si 'NIT' no está en la posición 4 (índice 3), la movemos
        if df.columns.get_loc('NIT') != 3:
        # Obtenemos la lista de columnas
            cols = df.columns.tolist()
            # Eliminamos 'NIT' de su posición actual
            cols.remove('NIT')
            # Insertamos 'NIT' en la posición 4 (índice 3)
            cols.insert(3, 'NIT')
            # Reordenamos las columnas del DataFrame
            df = df[cols]
        
        return df
    
    elif file_type in["cs2"]: 
           
        df = df.iloc[:, :9]
        #verifica que no hayan datos regados en el excel y los elimina
        if df['NIU'].isna().any():
            df = df.loc[:df['NIU'].isna().idxmax()-1]
        
        validar = search_data("verificar", None, None)
        validar['NIU'] = validar['NIU'].astype(str)
        df['NIU'] = df['NIU'].astype(str)
        
        df = pd.merge(df, validar[['OPERADOR_RED', 'NIU']], on='NIU', how='left')
                
        return df
    
    elif file_type in["dt"]:
        newdf = pd.DataFrame()
        
        # Lista de entidades
        entidades = search_data("or", "none", None)
        entidades = entidades.set_index('ABREVIATURA')['CODIGO'].to_dict()
        #se agregan otros nombres posibles al diccionario
        entidades.update({'TOLIMA': 7, 'CARTAGO': 25})
        
        nombre_columna = df.columns[1]

        # Variable para guardar la entidad encontrada
        palabra_encontrada = None

        # Busca cada entidad en el nombre de la columna
        for palabra, indice in entidades.items():
            if re.search(r'\b' + re.escape(palabra) + r'\b', nombre_columna):
                palabra_encontrada = palabra
                indice_encontrado = indice

        
        if df.columns[5].startswith('Unnamed:'):
            # Encuentra la primera fila en la tercera columna que no sea nula
            fila_encabezado = df.iloc[:, 2].dropna().iloc[0]
            
            if pd.notna(fila_encabezado):
                # Asignar los nombres de columna encontrados en la fila válida
                nueva_filas_encabezado = df.iloc[df.iloc[:, 2].dropna().index[0]].tolist()
                df.columns = nueva_filas_encabezado
                
                # Eliminar las filas usadas para nombres de columna
                df = df.iloc[df.iloc[:, 2].dropna().index[0] + 1:].reset_index(drop=True)
        
        # Diccionario para convertir nombres de meses a números
        meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
            'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        #obtiene el valor de la fecha
        fecha_str = df.columns[2]
        
        # Divide el string en mes y año
        partes = fecha_str.lower().split()
        mes_str = partes[0]
        ano = partes[1]
        
        # Obtén el número del mes
        mes = meses.get(mes_str)
        
        if mes is None:
            raise ValueError(f"Mes no reconocido: {mes_str}")
        
        # Formatear la fecha en "01/mm/aaaa" (donde el día es el primer día del mes)
        fecha_convertida = datetime(year=int(ano), month=mes, day=1)
        
        #agrega loa valores de los dt
        newdf['VALOR'] = df.iloc[1:5, [5]]
        #agrega el nivel de tension
        NIVEL_TENSION = newdf.index.values
        newdf['NIVEL TENSION'] = NIVEL_TENSION
        
        newdf['T MEDIDA'] = 'DT' + newdf['NIVEL TENSION'].astype(str)
        #agrega el codido de operador
        newdf['CODIGO_OPERADOR_RED'] = indice_encontrado
        #agrega la entidad al tadaframe
        newdf['ENTIDAD'] = palabra_encontrada
        #agrega la fecha al df
        newdf['FECHA'] = fecha_convertida
        
        #reordena el df
        nuevo_orden_columnas = [
            'CODIGO_OPERADOR_RED',
            'NIVEL TENSION',
            'ENTIDAD',
            'T MEDIDA',
            'FECHA',
            'VALOR'
        ]

        # Reordenar las columnas del DataFrame
        df = newdf[nuevo_orden_columnas]
        print(df)
        return df
                  
    elif file_type in["or"]:
        new_order = ['Código_v1', 'Código_v2', 'Código', 'Abreviatura', 'Operador_red']

        # Reordenar el DataFrame según el nuevo orden de columnas
        df = df[new_order]
        return df
    
    elif file_type in["instalaciones"]:
        # Usar la segunda fila como encabezado
        df.columns = df.iloc[0]  
        df = df[1:]
        
        #filtro para que unicamente guarde informacion dentro de la tabla
        if df.iloc[:, 0].isna().any():
            df = df.loc[:df.iloc[:, 0].isna().idxmax()-1]
            
        return df
          
    else:
        #retorna los datos para los formatoc que no necesitan cambios
        return df
    
def manage_type(df, file_type):
    # Define una función auxiliar para manejar valores nulos antes de la conversión de tipos
    def fill_missing_values(df, float_indices, date_indices, str_indices):
        # Rellenar valores nulos para columnas float con NaN (o un valor predeterminado si es necesario)
        df.iloc[:, float_indices] = df.iloc[:, float_indices].fillna(0.0)
        # Rellenar valores nulos para columnas de con NaT
        df.iloc[:, date_indices] = df.iloc[:, date_indices].fillna(pd.NaT)
        # Rellenar valores nulos para columnas de cadena con cadenas vacías
        df.iloc[:, str_indices] = df.iloc[:, str_indices].fillna('')
        return df

    if file_type in ["cs2"]:
        float_indices = [0, 1, 2, 3, 5, 7, 8, 9, 10]
        date_index = [4]
        str_index = [6]

        # Rellenar valores nulos antes de la conversión
        df = fill_missing_values(df, float_indices, date_index, str_index)
        
        # Conversión de tipos de datos
        df.iloc[:, float_indices] = df.iloc[:, float_indices].astype(float)
        df.iloc[:, str_index] = df.iloc[:, str_index].astype(str)
        
        return df
    
    elif file_type in ["tc1"]:
        float_indices = [2, 18, 19, 20, 24, 35, 36, 37, 40, 45, 81, 82, 83, 87, 98, 99, 100, 103, 108]
        str_indices = [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 38, 39, 41, 42, 43, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 84, 85, 86, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 101, 102, 104, 105, 106, 107]
        date_index = [109]
        
        # Rellenar valores nulos antes de la conversión
        df = fill_missing_values(df, float_indices, date_index, str_indices)
        
        # Conversión de tipos de datos
        df.iloc[:, float_indices] = df.iloc[:, float_indices].astype(float)
        df.iloc[:, str_indices] = df.iloc[:, str_indices].astype(str)
                
        return df
    
    elif file_type in ["zref"]:
        float_indices = [18, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]
        str_indices = [0, 1, 2, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 42, 43, 44, 45, 46, 47, 48, 49]
        date_indices = [3, 4, 8, 9]
        
        # Rellenar valores nulos antes de la conversión
        df = fill_missing_values(df, float_indices, date_indices, str_indices)
        
        # Conversión de tipos de datos
        df.iloc[:, str_indices] = df.iloc[:, str_indices].astype(str)
        df.iloc[:, float_indices] = df.iloc[:, float_indices].astype(float)
        
        return df
    
    elif file_type in ["diug_fiug"]:
        str_indices = [0]  # Índice de la columna "AÑO"
        float_indices = [1, 2, 3, 4, 5]  # Índices de las columnas NUMBER

        # Rellenar valores nulos antes de la conversión
        df = fill_missing_values(df, float_indices, [], str_indices)
        
        # Conversión de tipos de datos
        df.iloc[:, str_indices] = df.iloc[:, str_indices].astype(str)
        df.iloc[:, float_indices] = df.iloc[:, float_indices].astype(float)
        
        return df
    
    elif file_type in ["dt"]:
        float_indices = [0, 1, 5]  # Índices de las columnas NUMBER
        str_indices = [2, 3]  # Índices de las columnas VARCHAR2
        date_index = [4]  # Índice de la columna DATE ("FECHA")
        print(df)
        # Rellenar valores nulos antes de la conversión
        df = fill_missing_values(df, float_indices, date_index, str_indices)
        
        # Conversión de tipos de datos
        df.iloc[:, float_indices] = df.iloc[:, float_indices].astype(float)
        df.iloc[:, str_indices] = df.iloc[:, str_indices].astype(str)
        
        return df
    
    elif file_type in ["%t"]:
        str_indices = [0]
        float_indices = [1]

        # Rellenar valores nulos antes de la conversión
        df = fill_missing_values(df, float_indices, [], str_indices)
        
        # Conversión de tipos de datos
        df.iloc[:, str_indices] = df.iloc[:, str_indices].astype(str)
        df.iloc[:, float_indices] = df.iloc[:, float_indices].astype(float)
        
        return df
    
    elif file_type in ["or"]:
        str_indices = [0, 1, 3, 4]  # Índices de las columnas VARCHAR2
        float_index = [2]  # Índice de la columna NUMBER ("CODIGO")

        # Rellenar valores nulos antes de la conversión
        #df = fill_missing_values(df, [float_index], [], str_indices)
        
        # Conversión de tipos de datos
        df.iloc[:, str_indices] = df.iloc[:, str_indices].astype(str)
        df.iloc[:, float_index] = df.iloc[:, float_index].astype(float)
        
        return df
    
    elif file_type in ["instalaciones"]:
        str_indices = [0, 1, 3]
        float_index = [4]
        date_index = [5]
        
        df = fill_missing_values(df, float_index, date_index, str_indices)
        
        df.iloc[:, str_indices] = df.iloc[:, str_indices].astype(str)
        df.iloc[:, float_index] = df.iloc[:, float_index].astype(float)
        
        return df
    
    elif file_type in ["final"]:
        str_indices = [1, 2, 3, 27, 28, 34]
        float_indices = [0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 30, 31, 35]
        date_index = [29, 32, 33]
        
        df = fill_missing_values(df, float_indices, [], str_indices)
        
        df.iloc[:, str_indices] = df.iloc[:, str_indices].astype(str)
        df.iloc[:, float_indices] = df.iloc[:, float_indices].astype(float)
        
        for index in date_index:
            # Verificar si la columna ya está en formato datetime
            if pd.api.types.is_datetime64_any_dtype(df.iloc[:, index]):
                # Si ya está en formato fecha, aplicamos el formato 'dd/mm/yyyy'
                df.iloc[:, index] = df.iloc[:, index].dt.strftime('%d/%m/%Y')
            else:
                # Intentar convertir a fecha en formato 'dd/mm/yyyy'
                try:
                    df.iloc[:, index] = pd.to_datetime(df.iloc[:, index], errors='coerce', format='%d/%m/%Y')
                except Exception as e:
                    print(f"Error al convertir la columna en la posición {index}: {e}")
        
        if 'compensa_duracion' in df.columns:
            df['compensa_duracion'] = df['compensa_duracion'].astype(int)
        elif 'COMPENSA_DURACION' in df.columns:
            df['COMPENSA_DURACION'] = df['COMPENSA_DURACION'].astype(int)

        if 'compensa_frecuencia' in df.columns:
            df['compensa_frecuencia'] = df['compensa_frecuencia'].astype(int)
        elif 'COMPENSA_FRECUENCIA' in df.columns:
            df['COMPENSA_FRECUENCIA'] = df['COMPENSA_FRECUENCIA'].astype(int)
            
        if 'pagado_isagen' in df.columns:
            df['pagado_isagen'] = df['pagado_isagen'].astype(int)
        elif 'PAGADO_ISAGEN' in df.columns:
            df['PAGADO_ISAGEN'] = df['PAGADO_ISAGEN'].astype(int)
            
        if 'pagado_or' in df.columns:
            df['pagado_or'] = df['pagado_or'].astype(int)
        elif 'PAGADO_OR' in df.columns:
            df['PAGADO_OR'] = df['PAGADO_OR'].astype(int)
            
        if 'rechazada' in df.columns:
            df['rechazada'] = df['rechazada'].astype(int)
        elif 'RECHAZADA' in df.columns:
            df['RECHAZADA'] = df['RECHAZADA'].astype(int)
         
        return df
    
def actualizar_info(df,file_type):
    if file_type == "tc1":
        tc1 = search_data("verificar", None, None)
        
        formato = tc1[['NIU', 'SIC', 'CODIGO_TRANSFORMADOR_3']]
        
        df_merged = pd.merge(df, formato, on='SIC', how='left', suffixes=('', '_act'))
        columnas = ['NIU']

        # Actualizar las columnas
        for col in columnas:
            df_merged[col] = df_merged[col + '_act'].combine_first(df_merged[col])

            df_merged.drop([col + '_act' for col in columnas], axis=1, inplace=True)

        df_merged = df_merged.reindex_like(df)
        
        df_merged = df_merged.drop_duplicates(subset=['SIC'])
        
        df = df_merged

    return df
    