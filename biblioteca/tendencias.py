import logging, json, sys, time
import time
import numpy as np
from talib import abstract

class medias ():
    def __init__(self, API, config):
        ''' Construtor '''
        self.API = API
        self.config = config
    
    def SMA(self, par, tempo):
        velas = self.API.get_candles(par, 60 * tempo, self.config['PeriodoSMA'] + 1, time.time())

        valores = {'open': np.array([]), 'high': np.array([]), 'low': np.array([]), 'close': np.array([]), 'volume': np.array([]) }
	
        for x in velas:
            valores['open'] = np.append(valores['open'], x['open'])
            valores['high'] = np.append(valores['open'], x['max'])
            valores['low'] = np.append(valores['open'], x['min'])
            valores['close'] = np.append(valores['open'], x['close'])
            valores['volume'] = np.append(valores['open'], x['volume'])
        
        calculo_sma = abstract.SMA(valores, timeperiod=self.config['PeriodoSMA'])