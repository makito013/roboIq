sinaisPreparados = {'hora':[], 'minuto':[], 'par':[], 'sinal':[]}
from time import localtime, strftime
from biblioteca.diversos import salvaTransacaoTXT, salvaOperacaoNaoAbertaTXT
from biblioteca.tendencias import medias
from biblioteca import banca
from datetime import datetime, timedelta
import time
from biblioteca.indicadores import indicadores
import sqlite3
import threading

class estrategias ():
    def __init__(self, API, config, paresId):
        ''' Construtor '''
        self.API = API
        self.config = config
        self.paresId = paresId
        self.indicadores = indicadores(API, config)
        self.medias = medias(API, config)

    def MHI(self):
        API = self.API
        config = self.config
        par = 'EURJPY-OTC'
        tempoDelay = 0
        filtroIndi = self.indicadores

        if config['DelayMHI'] != 0:
            tempoDelay = 10 - config['DelayMHI']
        
        while True:
            minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
            entrar = True if (minutos >= (5 - config['DelayMHI']) and minutos <= 5) or minutos >= tempoDelay else False
            
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
                                    salvaTransacaoTXT('WIN MHI==> Posição: ' + dir + " || Velas: "+ velasLog + '|| Valor:' + str(config['ValorNegociacao']))  
                                    print('\nWIN MHI==> Posição: ', dir, "Velas: ", velasLog, '\n')
                                    #ganhoTotal = ganhoTotal + valor
                                    break
                                else:
                                    salvaTransacaoTXT('LOSS MHI==> Posição: '+ dir+ "Velas: " + velasLog + '|| VelasFiltro: ' + coresFiltro + ' || Valor:' + str(config['ValorNegociacao']))    
                                    print('\nLOSS MHI==> Posição: ', dir, "Velas: ", velasLog, '\n')
                                    #ganhoTotal = ganhoTotal + valor
                                    if config['MartingaleMHI'] > m:
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
        

        _han = int((datetime.now()).strftime('%H')) - 1
        _man = int((datetime.now()).strftime('%M')) - 1
        while True:
            #Timer Hora
            #A cada hora atualiza a lista
            _hat = int((datetime.now()).strftime('%H'))
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
                _seg = int((datetime.now()).strftime('%S'))
                for posicoes in listaAguardando:

                    if int(posicoes[1]) == _man and _seg < 30:
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
        if self.medias.analisadorTendenciaLista(par, tempo, operation) == False:
            return

        tipoOperacao = self.verificaPayout(par, tempo)
        datahora = ":".join([str(hora), str(minuto)])
        if tipoOperacao != False:
            _tabertura = datetime.strptime(datahora, '%H:%M')
            _tabertura = _tabertura + timedelta(minutes=1)
            _tabertura = float(_tabertura.strftime('%H%M.%S'))
            while True:
                _tatual = float((datetime.now()).strftime('%H%M.%S'))      
                # and _tatual <= _tabertura          
                entrar = True if (_tatual >= (_tabertura - self.config['Delay'])) else False

                if entrar == True:
                    status = False
                    id = 0

                    if tipoOperacao == 'digital':
                        status,id = self.API.buy_digital_spot(par, self.config['ValorNegociacao'], operation, tempo)
                    elif tipoOperacao == 'binario':
                        status,id = self.API.buy(self.config['ValorNegociacao'], par, operation, tempo)
                    else:
                        break
                    
                    if status == True:
                        print('Aberto negociação -> ', par, '-', tempo, '-', operation)
                        _tfinal = float((datetime.now() + timedelta(minutes=tempo)).strftime('%H%M.%S'))
                        m = 0
                        while True:
                            _tatual = float((datetime.now()).strftime('%H%M.%S'))
                            if _tatual >= _tfinal - self.config['DelayMartingale']:
                                valor = 0
                                velas = self.API.get_candles(par, 60 * tempo, 1, time.time())
                                velas[0] = 'call' if velas[0]['open'] < velas[0]['close'] else 'put' if velas[0]['open'] > velas[0]['close'] else 'd'
                                if velas[0] == operation:
                                    status, valor = False, False
                                    while not(status):
                                        status, valor = self.API.check_win_digital_v2(id)

                                if valor > 0:
                                    salvaTransacaoTXT('WIN LISTA ==> ' + par + " || "+ str(tempo) + 'm || ' + operation)  
                                    print('\nWIN LISTA ==> ', par, "||", tempo, 'm ||', operation, '\n')
                                    #ganhoTotal = ganhoTotal + valor
                                    break
                                else:
                                    salvaTransacaoTXT('LOSS LISTA ==> ' + par + " || "+ str(tempo) + 'm || ' + operation)  
                                    print('\nLOSS LISTA ==> ', par, "||", tempo, 'm ||', operation, '\n')
                                    #ganhoTotal = ganhoTotal + valor
                                    if self.config['Martingale'] > m:
                                        if tipoOperacao == 'digital':
                                            status,id = self.API.buy_digital_spot(par, self.config['ValorNegociacao']*2, operation, tempo)
                                        elif tipoOperacao == 'binario':
                                            status,id = self.API.buy(self.config['ValorNegociacao']*2, par, operation, tempo)

                                        status,id = self.API.buy_digital_spot(par, self.config['ValorNegociacao']*2, dir, 1)
                                        salvaTransacaoTXT('ABERTO MARTINGALE ' + str(m+1))    
                                        print('\nABERTO MARTINGALE = ', m+1 , '\n')
                                        m = m + 1
                                    else:
                                        break
                    else:    
                        print('Não foi possível abrir a negociação -> ', par, '-', tempo, '-', operation)

                    break

    
    def verificaPayout(self, par, tempo):
        try:
            _db = False
        
            binario = False
            digital = False
            _vBinario = 0    
            _vDigital = 0 
            parId = self.paresId[par]
            self.API.subscribe_strike_list(par, tempo)
            digital = self.API.get_digital_current_profit(par, tempo) * 100
            b = {}

            if tempo > 5:
                binario = False
            else:
                b = self.API.get_all_init()
                b = b['result']['turbo']['actives']
                binario = b[str(parId)]['enabled']

            if digital == 0:
                print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Par',par,'Não Disponivel na opção digital')
                salvaOperacaoNaoAbertaTXT('- Par '+par+' Não Disponível na opção digital')
                _vDigital = 0
            
            if binario == False:
                print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Par',par,'Não Disponivel na opção binario')
                salvaOperacaoNaoAbertaTXT('- Par '+par+' Não Disponível na opção binario')
                _vBinario = 0
            else:
                _vBinario = 100 - b[str(parId)]['option']['profit']['commission']

            if digital == False and binario == False:
                print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Posição não pode ser aberta pois par', par ,' não se encontra disponível')
                salvaOperacaoNaoAbertaTXT('- Posição não pode ser aberta pois '+par+' não se encontra disponível')
                return False
            else:
                if digital >= _vBinario:
                    if digital >= self.config['Payout']:
                        return 'digital'
                    else:
                        print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Negociação não foi aberta: Par', par ,'fora do payout')
                        salvaOperacaoNaoAbertaTXT('Negociação não foi aberta: Par '+ par +' fora do payout')
                        return False
                else:
                    if _vBinario >= self.config['Payout']:
                        #print('Dentro do payout')
                        return 'binario'
                    else:
                        print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Negociação não foi aberta: Par', par ,'fora do payout')
                        salvaOperacaoNaoAbertaTXT('Negociação não foi aberta: Par '+ par +' fora do payout')
                        return False
        except:
            print('Ops, aconteceu algum erro ao abrir a negociação')
            print('Par:',par, 'Tempo', tempo)
            # print(minuto, par, tempo, operation)

