import pandas as pd
from database.search_data import search_data

def mail_manager(df):
    # inicializa diccionario 
    data = {}
    #extrae datos operadores red
    operadores_red = search_data("or", None, None)
    operadores_red = operadores_red[["CODIGO", "ABREVIATURA"]]
    operadores_red = operadores_red.rename(columns={"CODIGO": 'OPERADOR_RED'})
    
    # Filtra unicamente por las filas que compensen 
    df = df[df['VF_A_COMP'] > 0]
    df = df.iloc[:, :30]
    
    # Realiza el merge para asociar los valores de OPERADOR_RED a OPERADOR_RED
    df = df.merge(operadores_red, on='OPERADOR_RED', how='left')

    # Reemplaza los valores de la columna OPERADOR_RED con los valores de ABREVIATURA
    df['OPERADOR_RED'] = df["ABREVIATURA"]
    df = df.drop(columns=["ABREVIATURA"])
    
    df = df[['FECHA', 'NIU', 'SIC', 'TRAFO', 'NIVEL_TENSION', 'GRUPO_CALIDAD', 'PORCENTAJE_T', 'DIUG', 'FIUG', 'DIU', 'DIUM', 'FIU', 'FIUM', 'EXCLU', 'CF', 'HC', 'THC', 'COMPENSA_DURACION', 'VC', 'TVC', 'COMPENSA_FRECUENCIA', 'CARGO_DIST', 'CECD', 'CECF', 'VCDD', 'VCFF', 'VF_A_COMP', 'OPERADOR_RED']]
    
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y').dt.strftime('%b-%Y')
    df['COMPENSA_DURACION'] = df['COMPENSA_DURACION'].apply(lambda x: 'si' if x == 1 else 'no')
    df['COMPENSA_FRECUENCIA'] = df['COMPENSA_FRECUENCIA'].apply(lambda x: 'si' if x == 1 else 'no')
    df['VCDD'] = df['VCDD'].apply(lambda x: "$   {:,.0f}".format(x))
    df['VCFF'] = df['VCFF'].apply(lambda x: "$   {:,.0f}".format(x))
    df['VF_A_COMP'] = df['VF_A_COMP'].apply(lambda x: "$   {:,.0f}".format(x))
    df['PORCENTAJE_T'] = df['PORCENTAJE_T'].apply(lambda x: "{:.0f}%".format(x * 100))
    df['NIVEL_TENSION'] = df['NIVEL_TENSION'].apply(lambda x: int(x))
    df['GRUPO_CALIDAD'] = df['GRUPO_CALIDAD'].apply(lambda x: int(x))
    
    for operador in df['OPERADOR_RED'].unique():
        data[operador] = df[df['OPERADOR_RED'] == operador]
        
    return data
