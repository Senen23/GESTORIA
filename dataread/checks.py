import pandas as pd
from datetime import datetime
from dataread.data_manager import manage_type
from database.update_data import update_data
from database.search_data import search_data

class Checks:
    def __init__(self):
        self.df_total = search_data("final", None, None)
        self.df_total = self.df_total.sort_values(by=['FECHA', 'OPERADOR_RED']).reset_index(drop=True)
        self.df_actualizaciones = pd.DataFrame()       
        
    def get_pendientes(self):
        #datos de compensaciones pendientes
        self.df_actualizaciones = self.df_total[(self.df_total['VF_A_COMP'] > 0) & (self.df_total['PAGADO_ISAGEN'] == 0) & (self.df_total['RECHAZADA'] != 1)].reset_index(drop=True)
        self.df_operar = self.df_actualizaciones.loc[:, ['FECHA', 'OPERADOR_RED', 'NIU', 'SIC', 'VF_A_COMP', 'INSTALACION_BD', 'PAGADO_ISAGEN', 'PAGADO_OR', 'FACTURACION_ISAGEN', 'FACTURACION_OR', 'OBSERVACIONES', 'RECHAZADA']]
        
    def get_pendientes_mes(self, date):
        date = date.strftime('%Y-%m-%d')
        self.df_actualizaciones = self.df_total[(self.df_total['VF_A_COMP'] > 0) & (self.df_total['FECHA'] == date)].reset_index(drop=True)
        self.df_operar = self.df_actualizaciones.loc[:, ['FECHA', 'OPERADOR_RED', 'NIU', 'SIC', 'VF_A_COMP', 'INSTALACION_BD', 'PAGADO_ISAGEN', 'PAGADO_OR', 'FACTURACION_ISAGEN', 'FACTURACION_OR', 'OBSERVACIONES', 'RECHAZADA']]
       
    def send_data(self):
        #reasignar cambios en total
        self.df_total['PAGADO_ISAGEN'] = self.df_operar['PAGADO_ISAGEN']
        self.df_total['PAGADO_OR'] = self.df_operar['PAGADO_OR']
        self.df_total['FACTURACION_ISAGEN'] = self.df_operar['FACTURACION_ISAGEN']
        self.df_total['FACTURACION_OR'] = self.df_operar['FACTURACION_OR']
        self.df_total['OBSERVACIONES'] = self.df_operar['OBSERVACIONES']
        self.df_total['RECHAZADA'] = self.df_operar['RECHAZADA']
        
        #reasignar cambios en total
        self.df_actualizaciones['PAGADO_ISAGEN'] = self.df_operar['PAGADO_ISAGEN']
        self.df_actualizaciones['PAGADO_OR'] = self.df_operar['PAGADO_OR']
        self.df_actualizaciones['FACTURACION_ISAGEN'] = self.df_operar['FACTURACION_ISAGEN']
        self.df_actualizaciones['FACTURACION_OR'] = self.df_operar['FACTURACION_OR']
        self.df_actualizaciones['OBSERVACIONES'] = self.df_operar['OBSERVACIONES']
        self.df_actualizaciones['RECHAZADA'] = self.df_operar['RECHAZADA']
    
        count = update_data(self.df_actualizaciones, "final")
        
        return count