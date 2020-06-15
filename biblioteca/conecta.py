from time import localtime, strftime

#Função de conexão
def conecta(API):
    try:
        if rec < 5:
            rec = rec + 1
            print('Erro ao logar')
            API.connect()
        else:
            print('Numero de tentativas excedido')
    except:
        print('Erro desconhecido')

def textTmp(text):
    textoTemp = ''
    if text == 'S':
        textoTemp = 'Ativado'
    elif text == 'N':
        textoTemp = 'Desativado'	
    return textoTemp

def carregaConfig(API):
    arquivo = open('config.txt', 'r')
    config = {'StopGain': '50%', 'StopLoss': '30%', 'MHI': 'S', 'Lista': 'S', 'TipoConta':''}
    balance = API.get_balance()
    try:
        i = 0
        print()
        print('==========  CARREGANDO CONFIGURAÇÕES, AGUARDE ==========')
        for linha in arquivo:
            if '#' not in linha and '=' in linha:                
                linhaConfig = linha.split('=')
                linhaConfig[1] = linhaConfig[1].rstrip('\n')
                

                if linhaConfig[0] == 'Conta':
                    config['TipoConta'] = linhaConfig[1]
                    API.change_balance(linhaConfig[1])
                elif linhaConfig[0] == 'ValorNegociacao':
                    if '%' in linhaConfig[1]:
                        config['ValorNegociacao'] = balance * (int(linhaConfig[1].rstrip('%'))/100)
                    elif '$' in linhaConfig[1]:
                        config['ValorNegociacao'] = int(linhaConfig[1].rstrip('$'))
                elif linhaConfig[0] == 'StopGain':
                    if '%' in linhaConfig[1]:
                        config['StopGain'] = (balance * (int(linhaConfig[1].rstrip('%'))/100)) + balance
                    elif '$' in linhaConfig[1]:
                        config['StopGain'] = int(linhaConfig[1].rstrip('$')) + balance
                elif linhaConfig[0] == 'StopLoss':
                    if '%' in linhaConfig[1]:
                        config['StopLoss'] = balance - (balance * (int(linhaConfig[1].rstrip('%'))/100))
                    elif '$' in linhaConfig[1]:
                        config['StopLoss'] = balance - int(linhaConfig[1].rstrip('$')) 
                elif linhaConfig[0] == 'MHI':                    
                    config['MHI'] = linhaConfig[1]
                elif linhaConfig[0] == 'Lista':
                    config['Lista'] = linhaConfig[1]
                elif linhaConfig[0] == 'Martingale':
                    config['Martingale'] = int(linhaConfig[1])
                elif linhaConfig[0] == 'MiniVela':
                    config['MiniVela'] = linhaConfig[1]
                elif linhaConfig[0] == 'HumorTraders':
                    config['HumorTraders'] = linhaConfig[1]
                elif linhaConfig[0] == 'porcetagemHumor':
                    config['porcetagemHumor'] = int(linhaConfig[1].rstrip('%'))
                elif linhaConfig[0] == 'Delay':
                    config['Delay'] = int(linhaConfig[1]) / 100

                i = i + 1
                #print('==========  (',i/total*100,'% ) ==========', end="\r")
                
        print('Tipo de Conta: ', config['TipoConta'])
        print('Delay: ', config['Delay'])
        print('StopGain: ', config['StopGain'])
        print('StopLoss: ', config['StopLoss'])
        print('ValorNegociação: ', config['ValorNegociacao'])
        print('MHI: ', textTmp(config['MHI']))
        print('FiltroMHIbot: ', textTmp(config['FiltroMHIbot']))
        print('HumorTraders: ', textTmp(config['HumorTraders']))
        print('porcetagemHumor: ', config['porcetagemHumor'])
        print('Lista: ', textTmp(config['Lista']))
        print('==========  CONFIGURAÇÃO CARREGADA COM SUCESSO ==========')
        print()
        print('Carteira: R$', balance)
        print()
        arquivo.close()
        return config
    except:
        print('Arquivo de configuração não foi encontrado!')

def leituraLista():
    #Variaveis
    #arquivo = ['19:40,USDCAD,PUT', '10:41,USDCAD,PUT', '10:49,USDCAD,PUT']
    arquivo = open('lista.txt', 'r')
    sinais = {'hora':[], 'minuto':[], 'par':[], 'posicao':[]}
    #hora = []
    #minuto = []
    #par = []
    #posicao = []
    i = 0
    #horaAtual = strftime("%H", localtime())
    #minutoAtual = strftime("%M", localtime())
    #segundoAtual = strftime("%S", localtime())
    print(" -------  LENDO LISTA DE SINAIS  --------- \r")
    #Lê arquivo
    try:
        for linha in arquivo:
            if linha[0] != '#':
                linha = linha.rstrip('\n')
                print(linha)
                separado = linha.split(',')
                time = separado[0].split(':')
                sinais['hora'].append(time[0])
                sinais['minuto'].append(time[1])
                sinais['par'].append(separado[1])
                sinais['posicao'].append(separado[2])
                i = i + 1
        arquivo.close()
        print()
        print(" -------  LISTA CARREGADA COM SUCESSO  --------- \r")
        return sinais
        
        #horaAtual = strftime("%H", localtime())
    except:
        print("Erro na lista")
