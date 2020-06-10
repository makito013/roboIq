#Função de conexão
def conecta(API):
    if rec < 5:
        rec = rec + 1
        print('Erro ao logar')
        API.connect()
    else:
        print('Numero de tentativas excedido')			

def carregaConfig(API):
    arquivo = open('config.txt', 'r')
    try:
        i = 0
        for linha in arquivo:
            if linha[0] != '#':                
                linhaConfig = linha.split('=')
                if linhaConfig[0] == 'Conta':
                    API.change_balance(linhaConfig[1])                 
                i = i + 1
        print('Carteira: R$', API.get_balance())
    except:
        print('Arquivo de configuração não foi encontrado!')