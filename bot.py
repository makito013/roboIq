from iqoptionapi.stable_api import IQ_Option
from time import localtime, strftime
from biblioteca.conecta import conecta, carregaConfig, leituraLista
from biblioteca.estrategias import estrategias
import sys
import threading
import time

#Variaveis Globais
ganhoTotal = 0

#Conexão API
API = IQ_Option('bandradest@gmail.com', 'Bruno9107')
API.connect()
rec = 0

#While
load = '|'
configurado = False
tempAnterior = strftime("%S", localtime())
tempMinAnterior = strftime("%M", localtime())
config = {}
lista = {}
t = {}
e = {}
while True:
	if API.check_connect() == False:
		conecta(API)
	else:		
		if configurado == False:
			print(API.get_digital_current_profit('USDCHF', 5))
			d = API.get_all_profit()
			print(d["CADCHF"]["turbo"])
			
			print('####  Conectado com sucesso  ########')
			print('####  Carregando Configuracao  ########')
			config = carregaConfig(API)
			if config["Lista"] == 'S':
				lista = leituraLista()
			configurado = True
			e = estrategias(API, config)
			if config['MHI'] == 'S':
				t['MHI'] = threading.Thread(target=e.MHI, args=())
				t['MHI'].start()
			if config['Lista'] == 'S':
				t['Lista'] = threading.Thread(target=e.MHI, args=())
				t['Lista'].start()
		else:
			segundoAtual = strftime("%S", localtime())				
			if tempAnterior != segundoAtual:
				if load == '|':
					load = '/'
				elif load == '/':
					load = '-'
				elif load == '-':
					load = '\\'
				else:
					load = '|'

				tempAnterior = segundoAtual
				MinutoAtual = strftime("%M", localtime())
				horaAtual = strftime("%H", localtime())
				MHITemp = '- MHI Esta procurando oportunidade' if config['MHI'] == 'S' else ''
				print(load, ' - ', horaAtual,':', MinutoAtual, ':', segundoAtual, MHITemp, end="\r")

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