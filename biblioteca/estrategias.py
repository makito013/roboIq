sinaisPreparados = {'hora':[], 'minuto':[], 'par':[], 'sinal':[]}
from time import localtime, strftime
from biblioteca.diversos import salvaTransacaoTXT
from biblioteca import banca
from datetime import datetime
import time
from biblioteca.estrategias import indicadores

def lista(sinais, config):
    #index = 0;
    #verifica hora atual#horaAtual = ""
    horaAtual = strftime("%H", localtime())
    #minutoAtual = strftime("%M", localtime())
    #segundoAtual = strftime("%S", localtime())
    if horaAtual in sinais['hora']:
        #i = 0
        for horaTemp in sinais['hora']:
            if horaTemp == horaAtual:
                sinaisPreparados['hora'].append(horaTemp)

        #index = hora.index(horaAtual)


class MHI ():
    def __init__(self, API, config):
        ''' Construtor '''
        self.API = API
        self.config = config

    def str(self):
        API = self.API
        config = self.config
        par = 'EURJPY-OTC'
        tempoDelay = 0
        filtroIndi = indicadores(API, config)

        if config['Delay'] != 0:
            tempoDelay = 10 - config['Delay']
        
        while True:
            minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
            entrar = True if (minutos >= (5 - config['Delay']) and minutos <= 5) or minutos >= tempoDelay else False
            
            if entrar:        
                dir = False
                velas = API.get_candles(par, 60, 5, time.time())
                coresFiltro = ''
                velas[0] = 'g' if velas[0]['open'] < velas[0]['close'] else 'r' if velas[0]['open'] > velas[0]['close'] else 'd'
                velas[1] = 'g' if velas[1]['open'] < velas[1]['close'] else 'r' if velas[1]['open'] > velas[1]['close'] else 'd'
                velas[2] = 'g' if velas[2]['open'] < velas[2]['close'] else 'r' if velas[2]['open'] > velas[2]['close'] else 'd'
                velas[3] = 'g' if velas[3]['open'] < velas[3]['close'] else 'r' if velas[3]['open'] > velas[3]['close'] else 'd'
                velas[4] = 'g' if velas[4]['open'] < velas[4]['close'] else 'r' if velas[4]['open'] > velas[4]['close'] else 'd'                                
                
                cores = velas[2] + velas[3] + velas[4]
                velasLog = velas[0] + velas[1] + velas[2] + velas[3] + velas[4]

                if cores.count('g') > cores.count('r') and cores.count('d') == 0 : dir = 'put' 
                if cores.count('r') > cores.count('g') and cores.count('d') == 0 : dir = 'call'
                
                if dir != False and filtroIndi.verificaIndicadores(par, dir) == False: 
                    dir = False
                    print('MHI Não aberto pelo filtro de indicadores')
                
                if dir : 
                    status,id = API.buy_digital_spot(par, config['ValorNegociacao'], dir, 1)
                    if status:
                        print('\nMHI => ABERTO UMA NEGOCIAÇÃO NO \nPAR:', par, '\nDIREÇÃO:',dir,'\nVALOR:', config['ValorNegociacao'], '\n')
                        m = 0
                        minutoAnterior = int(((datetime.now()).strftime('%M'))[1:])
                        while True:
                            minutosAtual = int(((datetime.now()).strftime('%M'))[1:])
                            
                            if minutosAtual != minutoAnterior :
                                minutoAnterior = minutosAtual
                                #status, valor = API.check_win_digital_v2(id)
                                valor = 0
                                velas = API.get_candles(par, 60, 1, time.time())
                                velas[0] = 'call' if velas[0]['open'] < velas[0]['close'] else 'put' if velas[0]['open'] > velas[0]['close'] else 'd'
                                if velas[0] == dir:
                                    status, valor = False, False
                                    while not(status):
                                        status, valor = API.check_win_digital_v2(id)

                                #if status:
                                if valor > 0:
                                    salvaTransacaoTXT('WIN ==> Posição: ' + dir + " || Velas: "+ velasLog + '|| Valor:' + str(config['ValorNegociacao']))  
                                    print('\nWIN ==> Posição: ', dir, "Velas: ", velasLog, '\n')
                                    #ganhoTotal = ganhoTotal + valor
                                    break
                                else:
                                    salvaTransacaoTXT('LOSS ==> Posição: '+ dir+ "Velas: " + velasLog + '|| VelasFiltro: ' + coresFiltro + ' || Valor:' + str(config['ValorNegociacao']))    
                                    print('\nLOSS ==> Posição: ', dir, "Velas: ", velasLog, '\n')
                                    #ganhoTotal = ganhoTotal + valor
                                    if config['Martingale'] > m:
                                        status,id = API.buy_digital_spot(par, config['ValorNegociacao']*2, dir, 1)
                                        salvaTransacaoTXT('ABERTO MARTINGALE ' + str(m+1))    
                                        print('\nABERTO MARTINGALE = ', m+1 , '\n')
                                        m = m + 1
                                    else:
                                        break
                    else:
                        print('\nErro ao abrir posição\n')
                else:
                    print('\nMHI Posição não aberta Velas: ', velasLog, ' Filtro: ',  coresFiltro ,'\n') 
