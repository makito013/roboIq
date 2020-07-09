from iqoptionapi.stable_api import IQ_Option
from time import localtime, strftime
from biblioteca.conecta import carregaConfig, leituraLista
from biblioteca.diversos import printLog
from biblioteca.estrategias import estrategias
import sys
import threading
import time
import getpass

#Variaveis Globais
ganhoTotal = 0

#Texto de Inicialização
print('\n\n\n\n#######################################################')
print('#######------------------------------------------######')
print('#######------------  WIN TRADER  ----------------######')
print('#######---------------  BOT  --------------------######')
print('#######------------------------------------------######')
print('#######################################################\n\n\n\n\n')

#Pegar Login e senha
#login = input("Digite seu e-mail cadastrado na IqOption: ")
#senha = getpass.getpass("Digite sua senha (por segugurança ela ficar invisível): ")
login = 'bandradest@gmail.com'
senha = 'Bruno9107'

#Conexão API
API = IQ_Option(login, senha)
API.connect()
rec = 0
texto = []
#While

configurado = False
tempAnterior = strftime("%S", localtime())
tempMinAnterior = strftime("%M", localtime())
logNaoAberto = []
logTransacao = []
config = {}
paresId = {}
lista = {}
t = {}
e = {}
rec = 0

while True:
	if API.check_connect() == False:
		try:
			if rec < 5:
				rec = rec + 1
				print('Erro ao logar, tente novamente!')
				#Pegar Login e senha
				login = input("Digite seu e-mail cadastrado na IqOption: ")
				senha = getpass.getpass("Digite sua senha (por segugurança ficará invisível): ")

				#Conexão API
				API = IQ_Option(login, senha)
				API.connect()
			else:
				print('Numero de tentativas excedido')
		except:
			print('Erro desconhecido')
	else:		
		if configurado == False:
			print('####  Conectado com sucesso  ########')
			print('####  Carregando Configuracao  ########')
			config, paresId = carregaConfig(API)		
			if config == False:
				break
			configurado = True			
			e = estrategias(API, config, paresId, texto, logTransacao, logNaoAberto)
			if config['MHI'] == 'S':
				t['MHI'] = threading.Thread(target=e.MHI, args=())
				t['MHI'].start()
			if config['Lista'] == 'S':
				lista = leituraLista()
				t['Lista'] = threading.Thread(target=e.lista, args=())
				t['Lista'].start()
			#Carrega LOG
			print('####  BUSCANDO OPORTUNIDADES  ########')
			t['Lista'] = threading.Thread(target=printLog, args=(texto, logTransacao, logNaoAberto))
			t['Lista'].start()	
		else:
			MinutoAtual = int(strftime("%M", localtime()))
			
			if tempMinAnterior != MinutoAtual:
				tempMinAnterior = MinutoAtual
				montanteAtual = API.get_balance()
				if config['StopGain'] <= montanteAtual:
					print()
					print('###### PARABENS STOP GAIN ########## \n TOTAL GANHO:',montanteAtual)
					#input('\n Aperte qualquer tecla para finalizar')
					break
					#sys.exit()
				elif config['StopLoss'] >= montanteAtual + config['ValorNegociacao']:
					print()
					print('###### OPS STOP TENTE OUTRO DIA ########## \n TOTAL DA BANCA:',montanteAtual)
					#input('\n Aperte qualquer tecla para finalizar')
					break
