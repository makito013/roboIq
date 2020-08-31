sinaisPreparados = {'hora':[], 'minuto':[], 'par':[], 'sinal':[]}
from time import localtime, strftime, sleep
#from biblioteca.diversos import salvaTransacaoTXT, salvaOperacaoNaoAbertaTXT
from biblioteca.tendencias import medias
from biblioteca import banca
from datetime import datetime, timedelta
import time
from biblioteca.indicadores import indicadores
import sqlite3
import threading

class estrategias ():
    def __init__(self, API, config, paresId, texto, logTransacao, logNaoAberto):
        ''' Construtor '''
        self.API = API
        self.config = config
        self.paresId = paresId
        self.indicadores = indicadores(API, config, logTransacao, logNaoAberto)
        self.medias = medias(API, config, logTransacao, logNaoAberto)
        self.texto = texto
        self.logTransacao = logTransacao
        self.logNaoAberto = logNaoAberto

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

                if cores.count('g') > cores.count('r') and cores.count('d') == 0 : dir = 'PUT'
                if cores.count('r') > cores.count('g') and cores.count('d') == 0 : dir = 'CALL'

                if dir != False and filtroIndi.verificaIndicadores(par, dir, 1) == False:
                    dir = False
                    print('MHI Não aberto pelo filtro de indicadores')

                if dir :
                    status,id = API.buy_digital_spot(par, config['ValorNegociacao'], dir.lower(), 1)
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
                                velas[0] = 'CALL' if velas[0]['open'] < velas[0]['close'] else 'PUT' if velas[0]['open'] > velas[0]['close'] else 'd'
                                if velas[0] == dir:
                                    status, valor = False, False
                                    while not(status):
                                        status, valor = API.check_win_digital_v2(id)

                                #if status:
                                if valor > 0:
                                    self.logTransacao.append('WIN MHI==> Posição: ' + dir + " || Velas: "+ velasLog + '|| Valor:' + str(config['ValorNegociacao']))
                                    print('\nWIN MHI==> Posição: ', dir, "Velas: ", velasLog, '\n')
                                    #ganhoTotal = ganhoTotal + valor
                                    break
                                else:
                                    self.logTransacao.append('LOSS MHI==> Posição: '+ dir+ "Velas: " + velasLog + '|| VelasFiltro: ' + coresFiltro + ' || Valor:' + str(config['ValorNegociacao']))
                                    print('\nLOSS MHI==> Posição: ', dir, "Velas: ", velasLog, '\n')
                                    #ganhoTotal = ganhoTotal + valor
                                    if config['MartingaleMHI'] > m:
                                        status,id = API.buy_digital_spot(par, config['ValorNegociacao']*2, dir.lower(), 1)
                                        self.logTransacao.append('ABERTO MARTINGALE ' + str(m+1))
                                        print('\nABERTO MARTINGALE = ', m+1 , '\n')
                                        m = m + 1
                                    else:
                                        break
                            sleep(0.5)
                    else:
                        print('\nErro ao abrir posição\n')
                else:
                    print('\nMHI Posição não aberta Velas: ', velasLog, ' Filtro: ',  coresFiltro ,'\n')
        
            sleep(0.1)

    def lista(self):
        listaAguardando = []

        x = 1
        _han = int((datetime.now()- timedelta(hours=1)).strftime('%H'))
        _man = int((datetime.now()- timedelta(minutes=1)).strftime('%M'))
        while self.config['continua']:
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
            #_man = False
            if _mat != _man:
                _man = _mat

                i = 0
                _seg = int((datetime.now()).strftime('%S'))
                for posicoes in listaAguardando:

                    if int(posicoes[1]) == _man and _seg < 30:
                        minut = 0
                        if int(posicoes[1]) == 59:
                            minut = 00
                        else:
                            minut = int(posicoes[1]) + 1
                        
                        verificaPayout = []
                        verificaPayout.append(linha)
                        #verificar payout aqui apo´s armazenar todos as posicoes dessa hora
                        #após isso abre thread
                        #separar argumentos da thread para n ser reconhecida como ponteiro de memoria
                        t = None
                        t = threading.Thread(target=self.threadAbrePosicao, args=(posicoes[0], minut, posicoes[2], posicoes[3], posicoes[4]))
                        t.start()
                        listaAguardando.pop(i)
                    i = i + 1

            #minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
            #entrar = True if (minutos >= (5 - self.config['Delay']) and minutos <= 5) or minutos >= tempoDelay else False
            #if hora in lista['hora'] or hora in lista['hora']:
            #    print('Achei Hora')
            #if entrar:
            sleep(0.1)

    def threadAbrePosicao(self, hora, minuto, par, tempo, operation):
        if self.medias.analisadorTendenciaLista(par, tempo, operation) == False:
            linha = str(hora) + ':' + str(minuto) + ',' + par + ',' + str(tempo) + ',' + operation
            self.texto.append(linha + ' - Operação não realizada por estar contra a tendência')
            self.logNaoAberto.append(linha + ' - Operação não realizada por estar contra a tendência')
            return

        tipoOperacao = self.verificaPayout(par, tempo)
        datahora = ":".join([str(hora), str(minuto)])
        if tipoOperacao != False:
            _tabertura = datetime.strptime(datahora, '%H:%M')
            _tabertura = _tabertura - timedelta(seconds=self.config['Delay'])
            _tabertura = float(_tabertura.strftime('%H%M.%S'))
            while self.config['continua']:
                _tatual = float((datetime.now()).strftime('%H%M.%S'))
                # and _tatual <= _tabertura
                entrar = True if (_tatual >= (_tabertura)) else False

                if entrar == True:

                    filtroIndi = self.indicadores
                    if filtroIndi.verificaIndicadores(par, operation, tempo) == False:
                        self.texto.append('Operação Não aberto pelo filtro de indicadores')
                        #print('Operação Não aberto pelo filtro de indicadores')
                        break

                    status = False
                    id = 0

                    if tipoOperacao == 'digital':
                        status,id = self.API.buy_digital_spot(par, self.config['ValorNegociacao'], operation.lower(), tempo)
                    elif tipoOperacao == 'binario':
                        status,id = self.API.buy(self.config['ValorNegociacao'], par, operation.lower(), tempo)
                    else:
                        break

                    if status == True:
                        self.texto.append('Aberto negociação em ' + tipoOperacao + ' -> ' + par + ' - ' + str(tempo) + ' - ' + operation)
                        #print('Aberto negociação -> ', par, '-', tempo, '-', operation)
                        _tfinal = float((datetime.strptime(datahora, '%H:%M') + timedelta(minutes=int(tempo)) - timedelta(seconds=self.config['DelayMartingale'])).strftime('%H%M.%S'))
                        m = 0
                        vm = 1
                        while True:
                            _tatual = float((datetime.now()).strftime('%H%M.%S'))
                            if _tatual >= _tfinal:
                                valor = 0
                                velas = self.API.get_candles(par, 60 * tempo, 1, time.time())
                                resultado = 'CALL' if velas[0]['open'] < velas[0]['close'] else 'PUT' if velas[0]['open'] > velas[0]['close'] else 'd'
                                if resultado == operation:
                                    status = False
                                    while valor == 0:
                                        if tipoOperacao == 'digital':
                                            status, valor = self.API.check_win_digital_v2(id)
                                        elif tipoOperacao == 'binario':
                                            valor = self.API.check_win_v3(id)
                                if valor == None: #Em caso de dodge
                                    valor = 0

                                if valor > 0:
                                    self.logTransacao.append('WIN LISTA ==> ' + par + " || "+ str(tempo) + 'm || ' + operation)
                                    self.texto.append('WIN LISTA ==> ' + par + " || "+ str(tempo) + 'm || ' + operation)
                                    # print('\nWIN LISTA ==> ', par, "||", tempo, 'm ||', operation, '\n')
                                    #ganhoTotal = ganhoTotal + valor
                                    break
                                else:
                                    if m == 0:
                                        self.logTransacao.append('LOSS LISTA ==> ' + par + " || "+ str(tempo) + 'm || ' + operation)
                                        self.texto.append('LOSS LISTA ==> ' + par + " || "+ str(tempo) + 'm || ' + operation)
                                    else:
                                        self.logTransacao.append('LOSS MARTINGALE '+ str(m) +' LISTA ==> ' + par + " || "+ str(tempo) + 'm || ' + operation)
                                        self.texto.append('LOSS MARTINGALE '+ str(m) +' LISTA ==> ' + par + " || "+ str(tempo) + 'm || ' + operation)
                                    #print('\nLOSS LISTA ==> ', par, "||", tempo, 'm ||', operation, '\n')
                                    #ganhoTotal = ganhoTotal + valor
                                    if self.config['Martingale'] > m and self.config['continua'] == True:
                                        vm = vm * 2
                                        if tipoOperacao == 'digital':
                                            status,id = self.API.buy_digital_spot(par, self.config['ValorNegociacao']*(vm), operation.lower(), tempo)
                                        elif tipoOperacao == 'binario':
                                            status,id = self.API.buy(self.config['ValorNegociacao']*(vm), par, operation.lower(), tempo)                                        
                                        _tfinal = float((datetime.strptime(_tfinal, '%H%M.%S') + timedelta(minutes=int(tempo)) - timedelta(seconds=self.config['DelayMartingale'])).strftime('%H%M.%S'))
                                        self.logTransacao.append('ABERTO MARTINGALE '+ par + ' ' + str(m+1))
                                        self.texto.append('ABERTO MARTINGALE '+ par + ' ' + str(m+1))
                                        #print('\nABERTO MARTINGALE = ', m+1 , '\n')
                                        m = m + 1
                                    else:
                                        break
                            sleep(0.1)
                    else:
                        self.texto.append('Não foi possível abrir a negociação -> ' + par + ' - ' + str(tempo) + ' - ' + operation)
                        #print('Não foi possível abrir a negociação -> ', par, '-', tempo, '-', operation)

                    break
                sleep(0.1)


    def verificaPayout(self, par, tempo):
        try:
            _db = False

            binario = False
            digital = False
            _vBinario = 0
            _vDigital = 0
            parId = self.paresId[par]
            self.API.subscribe_strike_list(par, tempo)
            sleep(2)
            digital = self.API.get_digital_current_profit(par, tempo)
            b = {}

            if tempo > 5:
                binario = False
            else:
                b = self.API.get_all_init()
                b = b['result']['turbo']['actives']
                binario = b[str(parId)]['enabled']

            if digital == 0:
                #self.texto.append('Par '+par+' Não Disponível na opção digital')
                #print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Par',par,'Não Disponivel na opção digital')
                #self.logNaoAberto.append('- Par '+par+' Não Disponível na opção digital')
                _vDigital = 0

            if binario == False:
                #self.texto.append('Par '+par+' Não Disponível na opção binario')
                #print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Par',par,'Não Disponivel na opção binario')
                #self.logNaoAberto.append('- Par '+par+' Não Disponível na opção binario')
                _vBinario = 0
            else:
                _vBinario = 100 - b[str(parId)]['option']['profit']['commission']

            #self.API.unsubscribe_strike_list(par, tempo)

            if digital == False and binario == False:
                self.texto.append('Posição não pode ser aberta pois '+par+' não se encontra disponível')
                #print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Posição não pode ser aberta pois par', par ,' não se encontra disponível')
                self.logNaoAberto.append('- Posição não pode ser aberta pois '+par+' não se encontra disponível')
                return False
            else:
                if digital >= _vBinario:
                    if digital >= self.config['Payout']:
                        return 'digital'
                    else:
                        self.texto.append('Negociação não foi aberta: Par '+ par +' fora do payout')
                        #print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Negociação não foi aberta: Par', par ,'fora do payout')
                        self.logNaoAberto.append('Negociação não foi aberta: Par '+ par +' fora do payout')
                        return False
                else:
                    if _vBinario >= self.config['Payout']:
                        #print('Dentro do payout')
                        return 'binario'
                    else:
                        self.texto.append('Negociação não foi aberta: Par '+ par +' fora do payout')
                        #print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '- Negociação não foi aberta: Par', par ,'fora do payout')
                        self.logNaoAberto.append('Negociação não foi aberta: Par '+ par +' fora do payout')
                        return False
        except:
            self.texto.append('Ops, aconteceu algum erro ao abrir a negociação')
            self.texto.append('Par: ' + par + ' - Tempo: ' + str(tempo))
            #print('Ops, aconteceu algum erro ao abrir a negociação')
            #print('Par:',par, 'Tempo', tempo)
            # print(minuto, par, tempo, operation)
