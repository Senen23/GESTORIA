import numpy as np
import pandas as pd
from database.sum_data import sum_data
from database.search_data import search_data
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

class DoMath:
    def __init__(self):
        # Definir variables
        self.df_data = pd.DataFrame(columns=[
            'operador_red',
            'niu',
            'sic',
            'trafo',
            'nivel_tension',
            'grupo_calidad',
            'porcentaje_t',
            'diug',
            'fiug',
            'diu',
            'dium',
            'fiu',
            'fium',
            'exclu',
            'cf',
            'hc',
            'thc',
            'compensa_duracion',
            'vc',
            'tvc',
            'compensa_frecuencia',
            'cargo_dist',
            'cecd',
            'cecf',
            'vcdd',
            'vcff',
            'vf_a_comp',
            'instalacion_bd',
            'nombre_cliente',
            'fecha',
            'pagado_isagen',
            'pagado_or',
            'facturacion_isagen',
            'facturacion_or',
            'observaciones',
            'rechazada'
        ])

    def extract_data(self, date):
        data = search_data(None, None, date)

        tc1 = data[0]
        cs2 = data[1] 
        zref = data[2]
        operador_red = data[3]
        dt = data[4]
        diugFiug = data[5]
        porcentaje_t = data[6]
        instalaciones = data[7]
        
        # Renombrar las columnas 
        # #TC1
        # Asegurarse de que no haya valores None  
        tc1['Tipo_de_conexion_3'] = tc1['Tipo_de_conexion_3'].fillna('') 
        tc1['Codigo_circuito_o_linea_3'] = tc1['Codigo_circuito_o_linea_3'].fillna('')
        
        # Utilizar un bucle para asegurar la asignación correcta 
        for idx, row in tc1.iterrows(): 
            if row['Tipo_de_conexion_3'] == '1': 
                tc1.at[idx, 'Codigo_transformador_3'] = row['Codigo_circuito_o_linea_3'] 
        print(tc1[['Tipo_de_conexion_3', 'Codigo_circuito_o_linea_3', 'Codigo_transformador_3']])
        tc1 = tc1.rename(columns={
            'NIU': 'niu', 
            'SIC': 'sic', 
            'Codigo_transformador_3': 'trafo', 
            'Nivel_de_Tension_3': 'nivel_tension', 
            'Grupo_de_calidad': 'grupo_calidad'
        })
        
        tc1 = tc1.drop(columns=['Codigo_circuito_o_linea_3', 'Tipo_de_conexion_3'])
        tc1['sic'] = tc1['sic'].str.lower()
        
        validar = search_data("verificar", None, None)
        validar['sic'] = validar['SIC'].str.lower()
        validar['niu'] = validar['NIU']
        validar['operador_red'] = validar['OPERADOR_RED']
        tc1 = tc1.drop_duplicates(subset=['sic'])
        
        tc1 = pd.merge(tc1, validar[['operador_red', 'sic', 'niu']], on='sic', how='left',  suffixes=('', '_new')) 
        tc1['niu'] = tc1['niu'].fillna(tc1['niu_new'])
        tc1.drop(columns=['niu_new'], inplace=True)
        tc1['niu'] = tc1['niu'].astype(str)
        
        
        # CS2
        cs2 = cs2.rename(columns={
            'DIU': 'diu',
            'DIUM': 'dium',
            'FIU': 'fiu',
            'FIUM': 'fium',
            'NIU': 'niu',
            'DI': 'exclu',
            'CODIGO_OPERADOR_RED': 'operador_red'
        })
        # Filtrar por valores menores a 16
        cs21 = cs2[cs2['CODIGO_CAUSA'] < 16]
        # Convertir columnas a numérico para manejar NaN y vacíos correctamente
        cs21['NI'] = pd.to_numeric(cs21['NI'], errors='coerce')
        cs21['exclu'] = pd.to_numeric(cs21['exclu'], errors='coerce')
        # Agrupar por 'niu' y calcular la suma de 'NI' y 'exclu'
        suma = cs21.groupby('niu').agg({'NI': 'sum', 'exclu': 'sum'}).reset_index()
        # Reemplazar NaN con 0
        suma = suma.fillna(0)
        cs2['niu'] = cs2['niu'].astype(str)
        suma['niu'] = suma['niu'].astype(str)
        
        #ZREF
        zref = zref.rename(columns={ 
            'TOTALENERGIAAKWH': 'cf',
            'INSTALACION': 'instalacion_bd', 
            'NOMBREDELCLIENTE': 'nombre_cliente', 
            'OPERADORRED': 'ABREVIATURA', 
            'CODIGOSIC': 'sic'
        })
        
        #OPERADOR RED
        operador_red = operador_red.rename(columns={
            'CODIGO': 'operador_red'
        })
        zref = pd.merge(zref, operador_red, on='ABREVIATURA', how='left')
        
        #DT
        dt = dt.rename(columns={
            'CODIGO_OPERADOR_RED': 'operador_red',
            'NIVEL_TENSION': 'nivel_tension',
            'VALOR': 'cargo_dist'
        })
        
        #DIUG_FIUG
        diugFiug = diugFiug.rename(columns={
            'CODIGO_OPERADOR_RED': 'operador_red',
            'NIVEL_TENSION': 'nivel_tension',
            'GRUPO_CALIDAD': 'grupo_calidad',
            'DIUG': 'diug',
            'FIUG': 'fiug'
        })
        
        #INSTALACIONES
        instalaciones = instalaciones.rename(columns={
            'SIC': 'sic',
            'INSTALACION': 'instalacion_bd'
        })
        instalaciones['sic'] = instalaciones['sic'].str.lower()
        
        #juntar toda la informacion de las diferentes tablas
        
        df_final = pd.merge(instalaciones, tc1, on='sic', how='left')
        df_final = pd.merge(df_final, cs2[['diu','dium','fiu','fium','niu','operador_red']], on=['niu', 'operador_red'], how='left')
        df_final = pd.merge(df_final, suma[['exclu','niu']], on='niu', how='left')
        df_final['exclu'].fillna(0, inplace=True)
        
        zref['cf'] = zref['cf'].str.replace(',', '.')
        zref['cf'] = pd.to_numeric(zref['cf'])
        zref = zref[zref['cf'] > 0]
        df_final['sic'] = df_final['sic'].str.lower()
        zref['sic'] = zref['sic'].str.lower()

        #SE AGREGA LA INFORMACION 
        # Realizar la combinación
        df_final = pd.merge(df_final, zref[['cf', 'nombre_cliente', 'sic']], on='sic', how='left')
        # Eliminar duplicados basados en las columnas que te interesen 
        df_final = df_final.drop_duplicates(subset='sic')
        
        df_final = pd.merge(df_final, dt, on=['operador_red', 'nivel_tension'], how='left')        
        df_final = pd.merge(df_final, diugFiug, on =['operador_red', 'nivel_tension', 'grupo_calidad'], how='left')
        
        año_actual = int(date.split('/')[1])
        porcentaje_t['AÑO'] = porcentaje_t['AÑO'].astype(int)
        # Asignar el porcentaje utilizando un lambda
        if año_actual > 2020:
            df_final.loc[df_final['operador_red'].isin([12, 18]), 'porcentaje_t'] = df_final['operador_red'].apply(
            lambda x: porcentaje_t.loc[porcentaje_t['AÑO'] == (año_actual - 2), 'PORCENTAJE'].values[0]
            )
        # Asignar el porcentaje del año actual a las demás filas
        df_final.loc[~df_final['operador_red'].isin([12, 18]), 'porcentaje_t'] = porcentaje_t.loc[porcentaje_t['AÑO'] == año_actual, 'PORCENTAJE'].values[0]
                
        fecha_convertida = datetime.strptime(date, '%m/%Y').strftime('01/%m/%Y')
        df_final['fecha'] = fecha_convertida
        
        self.df_data = self.df_data.fillna(0)
    
        self.df_data = pd.concat([self.df_data, df_final], ignore_index=True)
        
        #ELIMINA POSIBLES FILAS VACIAS
        self.df_data = self.df_data[self.df_data['sic'].str.strip().astype(bool)]
        
        return self.mats(date)
      
    def mats(self, date):
        # Calcula el valor de 'date_ini'
        date_ini = datetime.strptime(date, '%m/%Y').replace(day=1) - timedelta(days=11*30)
        date_ini = date_ini.strftime("%m/%Y")
        # Calcula el valor de 'date_fin' como un mes antes de 'date'
        date_fin = datetime.strptime(date, '%m/%Y') - relativedelta(months=1)
        date_fin = date_fin.strftime("%m/%Y")
        
        #se hace sumatoria para hc
        thc = sum_data('HC', date_ini, date_fin)
        thc_dict = dict(zip(thc['sic'], thc['thc']))
        # Asignar la columna 'thc' al DataFrame principal
        self.df_data['thc'] = self.df_data['sic'].map(thc_dict)
        self.df_data['thc'] = self.df_data['thc'].fillna(0)  
         
        self.df_data['hc'] = (round(self.df_data['diu'], 5) - self.df_data['diug'] - self.df_data['thc'])
        # Redondea a 8 decimales y convierte valores menores a 8 decimales en 0
        self.df_data['hc'] = self.df_data['hc'].apply(lambda x: round(x, 8) if round(x, 8) >= 10**-8 else 0)
        
        self.df_data['compensa_duracion'] = np.where(self.df_data['hc'] > 0, 1, 0)
        
        #se hace sumatoria para vc
        tvc = sum_data('VC', date_ini, date_fin)
        tvc_dict = dict(zip(tvc['sic'], tvc['tvc']))
        # Asignar la columna 'tvc' al DataFrame principal
        self.df_data['tvc'] = self.df_data['sic'].map(tvc_dict)    
        self.df_data['tvc'] = self.df_data['tvc'].fillna(0)  
         
        self.df_data['vc'] = (self.df_data['fiu'] - self.df_data['fiug'] - self.df_data['tvc']).clip(lower=0)
        
        self.df_data['compensa_frecuencia'] = np.where(self.df_data['vc'] > 0, 1, 0)
        
        # se calculan cecd y cecf
        cec = (self.df_data['cf'] / (720 - self.df_data['exclu'] - self.df_data['dium']) ) * self.df_data['dium'] + (self.df_data['cf'])

        # Filtrar las filas donde 'compensa_duracion' es 1 y hacer la asignación
        mask_duracion = self.df_data['compensa_duracion'] == 1
        self.df_data.loc[mask_duracion, 'cecd'] = cec
        self.df_data.loc[mask_duracion, 'vcdd'] = self.df_data.loc[mask_duracion, 'cecd'] * self.df_data.loc[mask_duracion, 'cargo_dist'] * self.df_data.loc[mask_duracion, 'porcentaje_t']

        # Filtrar las filas donde 'compensa_frecuencia' es 1 y hacer la asignación
        mask_frecuencia = self.df_data['compensa_frecuencia'] == 1
        self.df_data.loc[mask_frecuencia, 'cecf'] = cec
        self.df_data.loc[mask_frecuencia, 'vcff'] = self.df_data.loc[mask_frecuencia, 'cecf'] * self.df_data.loc[mask_frecuencia, 'cargo_dist'] * self.df_data.loc[mask_frecuencia, 'porcentaje_t']

        # Calcular 'vf_a_comp' sumando 'vcdd' y 'vcdf', manejando posibles NaN
        self.df_data['vf_a_comp'] = self.df_data[['vcdd', 'vcff']].fillna(0).sum(axis=1)
        
        self.df_data['pagado_isagen'] = np.where(self.df_data['vf_a_comp'] > 0, 0, 1)
        self.df_data['pagado_or'] = np.where(self.df_data['vf_a_comp'] > 0, 0, 1)
        
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        self.df_data['facturacion_isagen'] = np.where(self.df_data['pagado_isagen'] == 1, fecha_actual, None)
        self.df_data['facturacion_or'] = np.where(self.df_data['pagado_or'] == 1, fecha_actual, None)
        
        self.df_data.to_excel("UltimosCalculosRealizados.xlsx", index=False)
        return self.df_data
