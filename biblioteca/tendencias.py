import logging, json, sys, time
import time
import numpy as np
from talib import abstract

class medias ():
    def __init__(self, API, config):
        ''' Construtor '''
        self.API = API
        self.config = config

    def analisadorTendenciaLista(self, par, tempo, operation):
        if self.config['Tendencia'] == 'S':
            if self.config['EMA'] == 'S':
                if self.EMA(par, tempo) == operation:
                    return True
                else:
                    return False
            elif self.config['SMA'] == 'S':
                if self.SMA(par, tempo) == operation:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return True
    
    def SMA(self, par, tempo):
        velas = self.API.get_candles(par, 60 * tempo, self.config['PeriodoEMA'] + 3, time.time())

        valores = {'open': np.array([]), 'high': np.array([]), 'low': np.array([]), 'close': np.array([]), 'volume': np.array([]) }
	
        for x in velas:
            valores['open'] = np.append(valores['open'], x['open'])
            valores['high'] = np.append(valores['open'], x['max'])
            valores['low'] = np.append(valores['open'], x['min'])
            valores['close'] = np.append(valores['open'], x['close'])
            valores['volume'] = np.append(valores['open'], x['volume'])
        
        calculo_sma = abstract.SMA(valores, timeperiod=self.config['PeriodoEMA'])
        ultimo = len(calculo_sma)
        
        if calculo_sma[ultimo-1] > valores['close'][ultimo-1]:
            print('tendencia de queda')
            return 'queda'
        elif calculo_sma[ultimo-1] < valores['close'][ultimo-1]:
            print('tendencia de alta')
            return 'alta'
        else:
            print('tendencia neutra')
            return 'neutra'

        print(calculo_sma)

    def EMA(self, par, tempo):
        velas = self.API.get_candles(par, 60 * tempo, self.config['PeriodoSMA'] + 3, time.time())

        valores = {'open': np.array([]), 'high': np.array([]), 'low': np.array([]), 'close': np.array([]), 'volume': np.array([]) }
	
        for x in velas:
            valores['open'] = np.append(valores['open'], x['open'])
            valores['high'] = np.append(valores['open'], x['max'])
            valores['low'] = np.append(valores['open'], x['min'])
            valores['close'] = np.append(valores['open'], x['close'])
            valores['volume'] = np.append(valores['open'], x['volume'])
        
        calculo_ema = abstract.EMA(valores, timeperiod=self.config['PeriodoSMA'])
        ultimo = len(calculo_ema)
        ultimoCandle = 'call' if(valores['close'][ultimo-1] > valores['open'][ultimo-1]) else 'put'
        

        if ultimoCandle == 'call' and valores['close'][ultimo-1] > calculo_ema[ultimo-1] and valores['open'][ultimo-1] < calculo_ema[ultimo-1]:
            print('To no meio')
            return 'neutro'
        elif ultimoCandle == 'put' and valores['close'][ultimo-1] < calculo_ema[ultimo-1] and valores['open'][ultimo-1] > calculo_ema[ultimo-1]:
            print('To no meio')
            return 'neutro'
        elif calculo_ema[ultimo-1] > valores['close'][ultimo-1]:
            print('tendencia de queda')
            return 'put'
        elif calculo_ema[ultimo-1] < valores['close'][ultimo-1]:
            print('tendencia de alta')
            return 'call'

        print(calculo_ema)