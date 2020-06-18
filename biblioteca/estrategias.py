sinaisPreparados = {'hora':[], 'minuto':[], 'par':[], 'sinal':[]}
from time import localtime, strftime
from biblioteca.diversos import salvaTransacaoTXT, salvaOperacaoNaoAbertaTXT
from biblioteca import banca
from datetime import datetime
import time
from biblioteca.indicadores import indicadores
import sqlite3
import threading

class estrategias ():
    def __init__(self, API, config):
        ''' Construtor '''
        self.API = API
        self.config = config
        self.indicadores = indicadores(API, config)

    def MHI(self):
        API = self.API
        config = self.config
        par = 'EURJPY-OTC'
        tempoDelay = 0
        filtroIndi = self.indicadores

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

    def lista(self):
        listaAguardando = []
        

        
        while True:
            #Timer Hora
            #A cada hora atualiza a lista
            _hat = int((datetime.now()).strftime('%H'))
            _han = 0
            if _hat != _han:
                _han = _hat
                conn = sqlite3.connect('robot')
                cursor = conn.cursor()
                cursor.execute("SELECT hora, minuto, par, tempo, operation FROM lista WHERE Hora = " + (datetime.now()).strftime('%H'))
               

                for linha in cursor.fetchall():
                    listaAguardando.append(linha)

                cursor.execute("DELETE FROM lista WHERE Hora = " + (datetime.now()).strftime('%H'))
                conn.commit()
                conn.close()
            #Timer Segundo

            #Timer Minuto
            _mat = int((datetime.now()).strftime('%M'))
            _man = False
            if _mat != _man:
                _man = _mat

                i = 0
                for posicoes in listaAguardando:
                    if int(posicoes[1]) == _man:
                        t = threading.Thread(target=self.threadAbrePosicao, args=(posicoes))
                        t.start()
                        listaAguardando.pop(i)
                    i = i + 1
            

            #minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
            #entrar = True if (minutos >= (5 - self.config['Delay']) and minutos <= 5) or minutos >= tempoDelay else False
            
            #if hora in lista['hora'] or hora in lista['hora']:
            #    print('Achei Hora')
            #if entrar:
    
    def threadAbrePosicao(self, hora, minuto, par, tempo, operation):
        tipoOperacao = self.verificaPayout(par, tempo)
        
        if tipoOperacao != False
            
            while True:
                _tabertura = datetime.strptime(hora+':'minuto, '%H:%M')
                _tabertura = _tabertura + timedelta(minutes=1)
                _tabertura = float(_tabertura.strftime('%H%M.%S'))
                _tatual = float((datetime.now()).strftime('%H%M.%S'))                
                entrar = True if (minutos >= (5 - config['Delay']) and minutos <= 5) or minutos >= tempoDelay else False
                status,id = API.buy_digital_spot(par, config['ValorNegociacao'], dir, 1)
            
    
    def verificaPayout(self, par, tempo):
        _db = False
        if tempo < 15:
            binario = 0
            digital = 0
            
            digital = self.API.get_digital_current_profit(par, tempo)
            d = self.API.get_all_profit()
            binario = d[par]["turbo"]
            print(binario)

            if digital == False:
                print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Par',par,'Não Disponivel na opção digital')
                salvaOperacaoNaoAbertaTXT('- Par '+par+' Não Disponível na opção digital')
                digital = 0
            
            if binario == {}:
                print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Par',par,'Não Disponivel na opção binario')
                salvaOperacaoNaoAbertaTXT('- Par '+par+' Não Disponível na opção binario')
                binario = 0

            if digital == 0 and binario == 0:
                print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Posição não pode ser aberta pois par não se encontra disponível')
                salvaOperacaoNaoAbertaTXT('- Posição não pode ser aberta pois par não se encontra disponível')
                return False
            else:
                if digital > binario:
                    if digital >= self.config['Payout']:
                        return 'digital'
                    else:
                        print('Negociação não foi aberta: Par fora do payout')
                        return False
                else:
                    if binario >= self.config['Payout']:
                        print('Dentro do payout')
                        return 'binario'
                    else:
                        print('Negociação não foi aberta: Par fora do payout')
                        return False

           # print(minuto, par, tempo, operation)

