import pandas as pd
import os
import numpy as np
from tkinter import filedialog
from database.search_data import search_data

def create_file(date):
    
    date = pd.to_datetime(date, format='%d/%m/%Y')
    df = search_data("final", None, None)
    
    df_operar = df[df['FECHA'] == date].reset_index(drop=True)
    # Seleccionar las columnas requeridas
    datos = df_operar[['INSTALACION_BD', 'GRUPO_CALIDAD', 'PORCENTAJE_T', 'DIUG', 'FIUG', 'DIU', 'FIU', 'HC', 'VC', 'CARGO_DIST', 'CECF', 'CECD', 'VF_A_COMP', 'TRAFO', 'FACTURACION_ISAGEN']]
    datos['CEC'] = np.where(df_operar['CECF'] > 0, datos['CECF'], datos['CECD'])
    datos['CEC'] = np.where((df_operar['CECD'] > 0), datos['CECD'], datos['CEC']) 
    
    datos.drop(columns=['CECF', 'CECD'], inplace=True)
    datos['INSTALACION_BD'] = datos['INSTALACION_BD'].astype(str)

    
    #cambiar nombre de columnas
    datos = datos.rename(columns={
        'GRUPO_CALIDAD': 'Grupo_Calidad',
        'PORCENTAJE_T': '%t',
        'DIUG': 'DIUG',
        'FIUG': 'FIUG',
        'DIU': 'DIU',
        'FIU': 'FIU',
        'HC': 'HC',
        'VC': 'VC',
        'CEC': 'CEC',
        'CARGO_DIST': 'Dt',
        'VF_A_COMP': 'Valor_a_compensar',
        'TRAFO': 'Codigo_Circuito'
    })
    
    # Convertir la columna de fecha a datetime y obtener la fecha inicial y final del mes
    fecha_ini = date + pd.DateOffset(months=1)
    fecha_ini = pd.to_datetime(fecha_ini, format='%d/%m/%Y')
    fecha_fin = fecha_ini + pd.offsets.MonthEnd(0)
        
    # Crear un diccionario para almacenar DataFrames
    total_dfs = {}
    
    # Iterar sobre las columnas seleccionadas y crear DataFrames
    for col in datos.columns:
        if col not in ['INSTALACION_BD', 'FACTURACION_ISAGEN']: 
            # Crear los tadrames con los datos
            if col == 'Valor_a_compensar':
                # Crear columnas temporales con solo el mes y el año para la verificación
                df['MES_AÑO_PAGO'] = pd.to_datetime(df['FACTURACION_ISAGEN'], errors='coerce').dt.to_period('M')
                mes_año = (date + pd.DateOffset(months=2)).to_period('M')
                
                # Verificar las fechas de compensación usando solo el mes y el año, y agregar los datos
                data = df[df['MES_AÑO_PAGO'] == mes_año][['INSTALACION_BD', 'VF_A_COMP']]
                data = data.groupby('INSTALACION_BD').sum().reset_index()
                
                # Asegurar que todos los datos de df_operar estén presentes en el DataFrame final
                data = pd.merge(df_operar[['INSTALACION_BD']], data, on='INSTALACION_BD', how='left')
                data['VF_A_COMP'].fillna(0, inplace=True)
                df.drop(columns=['MES_AÑO_PAGO'], inplace=True)
                
            else:
                data = datos[['INSTALACION_BD', col]].copy()
                
            data[['inicio_consumo']] = fecha_ini
            data[['fin_consumo']] = fecha_fin
            
            # Crear el nombre del archivo CSV
            fecha_formateada = data['inicio_consumo'].dt.strftime('%m_%Y').iloc[0] 
            name = f'{fecha_formateada}_{col}'
            
            data['inicio_consumo'] = pd.to_datetime(data['inicio_consumo']).dt.strftime('%d/%m/%Y')
            data['fin_consumo'] = pd.to_datetime(data['fin_consumo']).dt.strftime('%d/%m/%Y')
            
            if col == 'Valor_a_compensar':
                data['COP'] = 'COP'
            
            # Almacenar el DataFrame en el diccionario
            total_dfs[name] = data
            
    # Imprimir el diccionario de DataFrames
    return total_dfs

def export_files(total_dfs):
    destino_carpeta = filedialog.askdirectory(title="Selecciona la carpeta donde guardar los archivos CSV")
    
    if destino_carpeta:
        for nombre_archivo, df in total_dfs.items():
            ruta_csv = os.path.join(destino_carpeta, f"{nombre_archivo}.xlsx")
            df.to_excel(ruta_csv, index=False)
        return destino_carpeta
    else:
        return
