import pandas as pd
from database.get_fechas import get_fechas
from database.search_data import search_data

def statistics(df):
    if df.empty:
        mensaje = 'No se encontraron datos'
    else:
        df = df.rename(columns={'vf_a_comp': 'compensa'})

        # Filtrar solo las filas donde 'compensa' sea mayor que 0
        df_filtrado = df[df['compensa'] > 0]

        # Agrupar por 'operador_red' y realizar la sumatoria y conteo de fronteras
        df_agrupado = df_filtrado.groupby('operador_red').agg(
            cant_fronteras=('compensa', 'count'),
            compensa=('compensa', lambda x: f"${x.sum():,.3f}")
        ).reset_index()

        # Calcular el total general
        total_compensacion = df_filtrado['compensa'].sum()
        total_fronteras = df_filtrado['compensa'].count()

        df_agrupado['operador_red'] = df_agrupado['operador_red'].astype(int)
        
        # se buscan los datos de los operadores red
        opr = search_data("or", None, None)
        opr = opr[["CODIGO", "ABREVIATURA"]]
        opr = opr.rename(columns={"CODIGO": 'operador_red'})
        
        df_agrupado = pd.merge(df_agrupado, opr, on='operador_red')
        df_agrupado = df_agrupado.drop('operador_red', axis=1)
        df_agrupado = df_agrupado.rename(columns={"ABREVIATURA": 'operador_red'})
        
        fecha =  df['fecha'].head(1).iloc[0]
        fecha = fecha.strftime('%d/%m/%Y')
        fechas = get_fechas(fecha)
        fechas = fechas.sort_values(by='FECHA').reset_index(drop=True)
        # Crear el mensaje final
        mensaje = (
            f"Se detectó que los siguientes operadores red tienen que compensar:\n\n"
            f"{df_agrupado.to_string(index=False, col_space=15)}\n\n"
            f"Hubo un total de {total_fronteras} fronteras a compensar por un monto total de ${total_compensacion:,.3f}.\n\n"
            f"Las fechas usadas para calcular estos datos fueron:\n {fechas.to_string(index=False, col_space=15)}"
        )
  
    return mensaje