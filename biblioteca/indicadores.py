import time
#from biblioteca.diversos import salvaOperacaoNaoAbertaTXT

class indicadores ():
    def __init__(self, API, config, logTransacao, logNaoAberto):
        ''' Construtor '''
        self.API = API
        self.config = config
        self.logTransacao = logTransacao
        self.logNaoAberto = logNaoAberto

    def verificaIndicadores(self, par, dir, tempo):
        if dir == False:
            return False

        retornoIndicador = True

        if self.config['OposicaoDeVela'] == 'S' and retornoIndicador == True:
            retornoIndicador = self.OposicaoDeVela(par,dir, tempo)

        # if self.config['HumorTraders'] == 'S' and retornoIndicador == True:
        #     retornoIndicador = self.humorTraders(par,dir)

        return retornoIndicador

    def OposicaoDeVela(self, par, dir, tempo):
        ## FILTRO PARA MHI
        API = self.API
        
        velaFiltro = API.get_candles(par, 60 * tempo, 1, time.time())
        velaAnterior = 'CALL' if velaFiltro[0]['open'] < velaFiltro[0]['close'] else 'PUT' if velaFiltro[0]['open'] > velaFiltro[0]['close'] else 'd'
        
        if velaAnterior == 'd':
            self.logNaoAberto.append('Indicador Oposição de Vela não permitiu operação - Vela Aterior é um Doji')
            return False
        elif velaAnterior != dir :
            return True
        else:
            self.logNaoAberto.append('Indicador Oposição de Vela não permitiu operação - Vela Aterior é igual a da ordem')
            return False            
        
        
        return False
        ## FIM FILTRO PARA MHI

    def humorTraders(self, par, dir):        
        self.API.start_mood_stream(par)
        porcentagem = self.API.get_traders_mood(par)
        porCall = int(100 * round(porcentagem, 2))
        porPut = 100 - porCall
        self.API.stop_mood_stream(par)

        if dir == 'call' and porCall >= self.config['porcetagemHumor']:
            return True
        elif dir == 'putt' and porPut >= self.config['porcetagemHumor']:
            return True
        else:
            self.logNaoAberto.append('Humor dos traders abaixo do programado')
            return False