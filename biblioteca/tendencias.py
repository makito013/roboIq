import logging, json, sys, time
import time
import numpy as np
#from biblioteca.diversos import salvaTransacaoTXT, salvaOperacaoNaoAbertaTXT
from talib import abstract

class medias ():
    def __init__(self, API, config, logTransacao, logNaoAberto):
        ''' Construtor '''
        self.API = API
        self.config = config
        self.logTransacao = logTransacao
        self.logNaoAberto = logNaoAberto

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
        velas = self.API.get_candles(par, 60 * tempo, self.config['PeriodoSMA'] + 3, time.time())

        valores = {'open': np.array([]), 'high': np.array([]), 'low': np.array([]), 'close': np.array([]), 'volume': np.array([]) }
	
        for x in velas:
            valores['open'] = np.append(valores['open'], x['open'])
            valores['high'] = np.append(valores['open'], x['max'])
            valores['low'] = np.append(valores['open'], x['min'])
            valores['close'] = np.append(valores['open'], x['close'])
            valores['volume'] = np.append(valores['open'], x['volume'])
        
        calculo_sma = abstract.SMA(valores, timeperiod=self.config['PeriodoSMA'])
        ultimo = len(calculo_sma)
        
        if calculo_sma[ultimo-1] > valores['close'][len(valores)-1]:
            #print('tendencia de queda')
            return 'PUT'
        elif calculo_sma[ultimo-1] < valores['close'][len(valores)-1]:
            #print('tendencia de alta')
            return 'CALL'
        else:
            #print('tendencia neutra')
            return 'neutra'

    def EMA(self, par, tempo):
        velas = self.API.get_candles(par, 60 * tempo, self.config['PeriodoEMA'] + 3, time.time())

        valores = {'open': np.array([]), 'high': np.array([]), 'low': np.array([]), 'close': np.array([]), 'volume': np.array([]) }
	
        for x in velas:
            valores['open'] = np.append(valores['open'], x['open'])
            valores['high'] = np.append(valores['open'], x['max'])
            valores['low'] = np.append(valores['open'], x['min'])
            valores['close'] = np.append(valores['open'], x['close'])
            valores['volume'] = np.append(valores['open'], x['volume'])
        
        calculo_ema = abstract.EMA(valores, timeperiod=self.config['PeriodoEMA'])
        ultimo = len(calculo_ema)
        ultimoCandle = 'CALL' if(valores['close'][len(valores)-1] > valores['open'][len(valores)-1]) else 'PUT'
        

        if ultimoCandle == 'CALL' and valores['close'][len(valores)-1] > calculo_ema[ultimo-1] and valores['open'][len(valores)-1] < calculo_ema[ultimo-1]:
            #print('To no meio')
            self.logNaoAberto.append('Vela Sobre a linha de Tendência')
            return 'NEUTRO'
        elif ultimoCandle == 'PUT' and valores['close'][len(valores)-1] < calculo_ema[ultimo-1] and valores['open'][len(valores)-1] > calculo_ema[ultimo-1]:
            #print('To no meio')
            self.logNaoAberto.append('Vela Sobre a linha de Tendência')
            return 'NEUTRO'
        elif calculo_ema[ultimo-1] > valores['close'][len(valores)-1]:
            #print('tendencia de queda')
            self.logNaoAberto.append('Tendência de Baixa')
            return 'PUT'
        elif calculo_ema[ultimo-1] < valores['close'][len(valores)-1]:
            #print('tendencia de alta')
            self.logNaoAberto.append('Tendência de Alta')
            return 'CALL'

        print(calculo_ema)