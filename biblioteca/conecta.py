from time import localtime, strftime
from datetime import datetime, timedelta
from biblioteca.diversos import criaTabela
import sqlite3
import getpass


def textTmp(text):
    textoTemp = ''
    if text == 'S':
        textoTemp = 'Ativado'
    elif text == 'N':
        textoTemp = 'Desativado'
    return textoTemp

def carregaConfig(API):
    # arquivo = open('./config.txt', 'r')
    config = {'StopGain': '50%', 'StopLoss': '30%', 'MHI': 'N', 'Lista': 'S', 'TipoConta':''}
    balance = 0
    try:
        i = 0
        print()
        print('==========  CARREGANDO CONFIGURAÇÕES, AGUARDE ==========')
        conn = sqlite3.connect('cn_et')
        cursor = conn.cursor()
        cursor.execute("SELECT CAMPO, VALOR FROM CONFIGS ")
        for linhaConfig in cursor.fetchall():
            #if '#' not in linha and '=' in linha:
            #linhaConfig = linha.split('=')
            #linhaConfig[1] = linhaConfig[1].rstrip('\n')

            if linhaConfig[0] == 'tipoConta':
                if linhaConfig[1] == 'Demo':
                    API.change_balance('PRACTICE')
                else:
                    API.change_balance('REAL')

                balance = API.get_balance()
                config['TipoConta'] = linhaConfig[1]
            elif linhaConfig[0] == 'negociacao':
                config['ValorNegociacao'] = int(linhaConfig[1])
            elif linhaConfig[0] == 'tipoValor':
                if '%' in linhaConfig[1]:
                    config['ValorNegociacao'] = round(balance * (config['ValorNegociacao']/100),2)
            elif linhaConfig[0] == 'qtdMartingale':
                config['Martingale'] = int(linhaConfig[1])
            elif linhaConfig[0] == 'delay':
                config['Delay'] = int(linhaConfig[1])
            elif linhaConfig[0] == 'delayMartingale':
                config['DelayMartingale'] = int(linhaConfig[1])
            elif linhaConfig[0] == 'stopGain':
                config['StopGain'] = int(linhaConfig[1])
            elif linhaConfig[0] == 'tipoStopGain':
                if '%' in linhaConfig[1]:
                    config['StopGain'] = (balance * (config['StopGain']/100)) + balance
                elif '$' in linhaConfig[1]:
                    config['StopGain'] = config['StopGain'] + balance
            elif linhaConfig[0] == 'stopLoss':
                config['StopLoss'] = int(linhaConfig[1])
            elif linhaConfig[0] == 'tipoStopLoss':
                if '%' in linhaConfig[1]:
                    config['StopLoss'] = balance - (balance * (config['StopLoss']/100))
                elif '$' in linhaConfig[1]:
                    config['StopLoss'] = balance - config['StopLoss']
            elif linhaConfig[0] == 'minimoPayout':
                config['Payout'] = float(linhaConfig[1])
            elif linhaConfig[0] == 'SMA':
                config['SMA'] = 'S' if linhaConfig[1] == '1' else 'N'
            elif linhaConfig[0] == 'EMA':
                config['EMA'] = 'S' if linhaConfig[1] == '1' else 'N'
            elif linhaConfig[0] == 'periodoEMA':
                config['PeriodoEMA'] = int(linhaConfig[1])
            elif linhaConfig[0] == 'periodoSMA':
                config['PeriodoSMA'] = int(linhaConfig[1])
            elif linhaConfig[0] == 'lista':
                config['Lista'] = 'S' if linhaConfig[1] == '1' else 'N'
            elif linhaConfig[0] == 'MHI':
                config['MHI'] = 'S' if linhaConfig[1] == '1' else 'N'
            elif linhaConfig[0] == 'oposicaoVela':
                config['OposicaoDeVela'] = 'S' if linhaConfig[1] == '1' else 'N'
            elif linhaConfig[0] == 'tendencia':
                config['Tendencia'] = 'S' if linhaConfig[1] == '1' else 'N'

            elif linhaConfig[0] == 'MartingaleMHI':
                config['MartingaleMHI'] = int(linhaConfig[1])

            # elif linhaConfig[0] == 'HumorTraders':
            #     config['HumorTraders'] = linhaConfig[1]
            # elif linhaConfig[0] == 'PorcentagemHumor':
            #     config['PorcentagemHumor'] = int(linhaConfig[1])

            elif linhaConfig[0] == 'DelayMHI':
                config['DelayMHI'] = int(linhaConfig[1]) / 100





            i = i + 1
            #print('==========  (',i/total*100,'% ) ==========', end="\r")

        print('==========  CONFIGURAÇÃO Geral ')
        print('Tipo de Conta: ', config['TipoConta'])
        print('StopGain: ', config['StopGain'])
        print('StopLoss: ', config['StopLoss'])
        print('ValorNegociação: ', config['ValorNegociacao'])
        print('Payout Minimo: ', config['Payout'])

        if config['MHI'] == 'S':
            print('==========  CONFIGURAÇÃO MHI ')
            print('MHI: ', textTmp(config['MHI']))
            print('Delay: ', config['DelayMHI'])
            print('DelayMartingale: ', config['DelayMartingale'])

        print('==========  CONFIGURAÇÃO Lista ')
        print('Lista: ', textTmp(config['Lista']))
        if config['Lista'] == 'S':
            print('Delay: ', config['Delay'])
            print('DelayMartingale: ', config['DelayMartingale'])
            print('Martingale: ', config['DelayMartingale'])
            print('Analise de Tendencia: ', textTmp(config['Tendencia']))

        print('==========  CONFIGURAÇÃO Analisador de Tendencia ')
        print('--- EMA ---')
        print('EMA: ', textTmp(config['EMA']))
        if config['EMA'] == 'S':
            print('Periodo: ', config['PeriodoEMA'])

        print('--- SMA ---')
        print('SMA: ', textTmp(config['SMA']))
        if config['SMA'] == 'S':
            print('Periodo: ', config['PeriodoSMA'])


        print('==========  CONFIGURAÇÃO CARREGADA COM SUCESSO ==========')
        print()
        print('Carteira: R$', balance)
        print()

        paresId = API.get_all_ACTIVES_OPCODE()

        return (config, paresId)
    except:
        print('Arquivo de configuração não foi encontrado!')
        return False, False


def leituraLista():
    #Variaveis
    #arquivo = ['19:40,USDCAD,PUT', '10:41,USDCAD,PUT', '10:49,USDCAD,PUT']
    arquivo = open('lista.txt', 'r')
    #sinais = []
    sinais = {'hora':[], 'minuto':[], 'par':[], 'posicao':[], 'tempo':[]}
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
        criaTabela()
        conn = sqlite3.connect('robot')
        cursor = conn.cursor()
        for linha in arquivo:
            if linha[0] != '#':
                linha = linha.rstrip('\n')
                linha = linha.rstrip(' ')
                print(linha)
                separado = linha.split(',')
                time = separado[0].split(':')
                if int(time[0])+ int(time[1]) == 0:
                    print('Sinal a meia noite não é permitido')
                else:
                    #mmdd.hhmm
                    date = datetime.strptime(time[0]+':'+time[1], '%H:%M')
                    date = date - timedelta(minutes=1)
                    horaString = date.strftime('%H')
                    minutoString = date.strftime('%M')
                    comando =  "INSERT INTO lista (id, hora, minuto, par, tempo, operation) VALUES ("+str(i)+","+horaString+","+minutoString+",'"+separado[1]+"',"+separado[2]+",'"+separado[3]+"')"
                    cursor.execute(comando)
                    #temp = {'hora':[], 'minuto':[], 'par':[], 'posicao':[], 'tempo':[]}
                    #sinais['hora'].append(int(time[0]))
                    #sinais['minuto'].append(int(time[1]))
                    #sinais['par'].append(separado[1])
                    #sinais['posicao'].append(separado[2])
                    #sinais['tempo'].append(separado[3])
                i = i + 1
        arquivo.close()
        conn.commit()
        #print('Dados inseridos com sucesso.')
        conn.close()
        print()
        print(" -------  LISTA CARREGADA COM SUCESSO  --------- \r")
        return sinais

        #horaAtual = strftime("%H", localtime())
    except:
        print("Erro na lista")
