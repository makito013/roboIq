import time
from biblioteca.diversos import salvaOperacaoNaoAbertaTXT

class indicadores ():
    def __init__(self, API, config):
        ''' Construtor '''
        self.API = API
        self.config = config

    def verificaIndicadores(self, par, dir):
        if dir == False:
            return False

        retornoIndicador = True

        if self.config['MiniVela'] == 'S' and retornoIndicador == True:
            retornoIndicador = self.miniVelas(par,dir)

        if self.config['HumorTraders'] == 'S' and retornoIndicador == True:
            retornoIndicador = self.humorTraders(par,dir)

        return retornoIndicador

    def miniVelas(self, par, dir):
        ## FILTRO PARA MHI
        API = self.API
        
        velaFiltro = API.get_candles(par, 15, 20, time.time())
        
        i = 0
        
        for x in velaFiltro:
            coresFiltro += 'g' if x['open'] < x['close'] else 'r' if x['open'] > x['close'] else 'd'                 
            i = i + 1

        if coresFiltro.count('g') > coresFiltro.count('r') and dir == 'call' : return True
        if coresFiltro.count('r') > coresFiltro.count('g') and dir == 'put' : return True
        
        salvaOperacaoNaoAbertaTXT('Indicador Minivela não permitiu operação')
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
            salvaOperacaoNaoAbertaTXT('Humor dos traders abaixo do programado')
            return False