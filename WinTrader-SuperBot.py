from iqoptionapi.stable_api import IQ_Option
from time import localtime, strftime
from biblioteca.conecta import carregaConfig, leituraLista
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
load = '|'
configurado = False
tempAnterior = strftime("%S", localtime())
tempMinAnterior = strftime("%M", localtime())
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
			e = estrategias(API, config, paresId, texto)
			if config['MHI'] == 'S':
				t['MHI'] = threading.Thread(target=e.MHI, args=())
				t['MHI'].start()
			if config['Lista'] == 'S':
				lista = leituraLista()
				t['Lista'] = threading.Thread(target=e.lista, args=())
				t['Lista'].start()
			print('####  BUSCANDO OPORTUNIDADES  ########')
		else:
			segundoAtual = strftime("%S", localtime())		
			if len(texto) > 0:
					print(strftime("%d/%m/%Y, %H:%M:%S", localtime()), '-', texto.pop())
			else:		
				if tempAnterior != segundoAtual:
					tempAnterior = segundoAtual
					MinutoAtual = strftime("%M", localtime())
					horaAtual = strftime("%H", localtime())
					
					if load == '|':
						load = '/'
					elif load == '/':
						load = '-'
					elif load == '-':
						load = '\\'
					else:
						load = '|'
						
					print(load, ' - ', horaAtual,':', MinutoAtual, ':', segundoAtual, end="\r")
						
					#MHITemp = '- MHI Esta procurando oportunidade' if config['MHI'] == 'S' else ''
					#print(load, ' - ', horaAtual,':', MinutoAtual, ':', segundoAtual, MHITemp, end="\r")

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
