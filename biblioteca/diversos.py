from time import localtime, strftime

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
