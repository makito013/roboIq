from iqoptionapi.stable_api import IQ_Option
from time import localtime, strftime, sleep
from biblioteca.conecta import carregaConfig, leituraLista
from biblioteca.diversos import printLog
from biblioteca.estrategias import estrategias
from datetime import datetime
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
login = 'bandradest@gmail.com'
senha = 'Bruno9107'

#Conexão API
API = IQ_Option(login, senha)
API.connect()

dateServer = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%m.%d'))
print(datetime.now())
validade = float((datetime.strptime('2020-08-13', '%Y-%m-%d').date()).strftime('%m.%d'))

if dateServer > validade:
	print('LICENÇA EXPIRADA')
	sys.exit()

rec = 0
texto = []
#While

configurado = False
tempAnterior = strftime("%S", localtime())
tempMinAnterior = strftime("%M", localtime())
logNaoAberto = []
logTransacao = []
config = {'continua': True}
paresId = {}
lista = {}
t = {}
e = {}
rec = 0

while config['continua']:
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
			#	API.subscribe_live_deal('live-deal-digital-optio', 'EURJPY','PT1M', 10)
			else:
				print('Numero de tentativas excedido')
		except:
			print('Erro desconhecido')
	else:		
		#time = 'PT1M'
		#buffersize=10
		
		#trades = API.get_live_deal('live-deal-digital-optio', 'EURJPY', 'PT1M')

		#if len(trades) > 0:
			#entra se tiver alguma posicao sendo aberta
		#	print(trades)

		if configurado == False:
			print('####  Conectado com sucesso  ########')
			print('####  Carregando Configuracao  ########')
			config, paresId = carregaConfig(API)
			
			if config == False:
				break

			config['continua'] = True	
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
			t['Lista'] = threading.Thread(target=printLog, args=(texto, logTransacao, logNaoAberto, config))
			t['Lista'].start()	
		else:
			MinutoAtual = int(strftime("%M", localtime()))

			if tempMinAnterior != MinutoAtual:
				tempMinAnterior = MinutoAtual
				montanteAtual = 100000#API.get_balance()
				if config['StopGain'] <= montanteAtual:
					print()
					print('###### PARABENS STOP GAIN ########## \n TOTAL GANHO:',montanteAtual)
					logNaoAberto.append('###### PARABENS STOP GAIN ########## \n TOTAL GANHO:' + str(montanteAtual))
					logTransacao.append('###### PARABENS STOP GAIN ########## \n TOTAL GANHO:' + str(montanteAtual))					
					config['continua'] = False
					input('\n Aperte qualquer tecla para finalizar')

				elif config['StopLoss'] >= montanteAtual + config['ValorNegociacao']:
					print()
					logNaoAberto.append('###### OPS STOP TENTE OUTRO DIA ########## \n TOTAL DA BANCA:' + str(montanteAtual))
					logTransacao.append('###### OPS STOP TENTE OUTRO DIA ########## \n TOTAL DA BANCA:' + str(montanteAtual))
					print('###### OPS STOP TENTE OUTRO DIA ########## \n TOTAL DA BANCA:',montanteAtual)
					config['continua'] = False
					input('\n Aperte qualquer tecla para finalizar')

	sleep(1)