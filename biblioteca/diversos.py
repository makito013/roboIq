from time import localtime, strftime
import sqlite3

def salvaTransacaoTXT(texto):
    with open('log_Transacoes.txt', 'a+') as arquivo:
        conteudo = arquivo.readlines()
        conteudo.append('\n' + strftime("%d/%m/%Y, %H:%M:%S", localtime()) + ' - ' + texto)
        arquivo.writelines(conteudo)
        arquivo.close()
        
def salvaConfigTXT(texto):
    with open('log_Config.txt', 'a+') as arquivo:
        conteudo = arquivo.readlines()
        conteudo.append('\n' + strftime("%d/%m/%Y, %H:%M:%S", localtime()) + ' - ' + texto)
        arquivo.writelines(conteudo)
        arquivo.close()

def salvaOperacaoNaoAbertaTXT(texto):
    with open('log_OpNA.txt', 'a+') as arquivo:
        conteudo = arquivo.readlines()
        conteudo.append('\n' + strftime("%d/%m/%Y, %H:%M:%S", localtime()) + ' - ' + texto)
        arquivo.writelines(conteudo)
        arquivo.close()

def criaTabela():
    # conectando...
    conn = sqlite3.connect('robot')
    # definindo um cursor
    cursor = conn.cursor()

    # criando a tabela (schema)
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