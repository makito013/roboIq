from time import localtime, strftime
import sqlite3



def printLog(texto, logTransacao, logNotOperacao):
    load = '|'
    tempAnterior = False
    while True:
        segundoAtual = int(strftime("%S", localtime()))
        
        if len(texto) > 0:
            print(strftime("%H:%M:%S", localtime()), '-', texto.pop())   
        else:
            if len(logTransacao) > 0 :
                salvaTransacaoTXT(logTransacao)
            elif len(logNotOperacao) > 0:
                salvaOperacaoNaoAbertaTXT(logNotOperacao)
            if tempAnterior != segundoAtual:
                tempAnterior = segundoAtual
                
                if load == '|':
                    load = '/'
                elif load == '/':
                    load = '-'
                elif load == '-':
                    load = '\\'
                else:
                    load = '|'
                    
                print(load, ' - ', strftime("%H:%M:%S", localtime()) , end="\r")
    #MHITemp = '- MHI Esta procurando oportunidade' if config['MHI'] == 'S' else ''
	#print(load, ' - ', horaAtual,':', MinutoAtual, ':', segundoAtual, MHITemp, end="\r")



def salvaTransacaoTXT(texto):
    with open('log_Transacoes.txt', 'a') as arquivo:
        conteudo = []
        while len(texto) > 0:
            conteudo.append('\n' + strftime("%d/%m/%Y, %H:%M:%S", localtime()) + ' - ' + texto.pop())
        arquivo.writelines(conteudo)
        arquivo.close()
        
def salvaConfigTXT(texto):
    with open('log_Config.txt', 'a') as arquivo:
        conteudo = []
        while len(texto) > 0:
            conteudo.append('\n' + strftime("%d/%m/%Y, %H:%M:%S", localtime()) + ' - ' + texto.pop())
        arquivo.writelines(conteudo)
        arquivo.close()

def salvaOperacaoNaoAbertaTXT(texto):
    with open('log_OpNA.txt', 'a+') as arquivo:
        conteudo = []
        while len(texto) > 0:
            conteudo.append('\n' + strftime("%d/%m/%Y, %H:%M:%S", localtime()) + ' - ' + texto.pop())
        arquivo.writelines(conteudo)
        arquivo.close()

def criaTabela():
    # conectando...
    conn = sqlite3.connect('robot')
    # definindo um cursor
    cursor = conn.cursor()

    # criando a tabela (schema)
    cursor.execute("DROP TABLE IF EXISTS lista")
    cursor.execute("""
    CREATE TABLE lista (
            id INTEGER NOT NULL PRIMARY KEY,
            hora INTEGER,
            minuto INTEGER,
            par TEXT,
            tempo INTEGER,
            operation TEXT
    );
    """)

    print('Tabela criada com sucesso.')
    # desconectando...
    conn.close()

    