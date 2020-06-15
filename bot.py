from iqoptionapi.stable_api import IQ_Option
from time import localtime, strftime
from biblioteca.conecta import conecta, carregaConfig, leituraLista
from biblioteca.estrategias import MHI
import sys
import _thread
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

while True:
	if API.check_connect() == False:
		conecta(API)
	else:		
		if configurado == False:
			print('####  Conectado com sucesso  ########')
			print('####  Carregando Configuracao  ########')
			config = carregaConfig(API)
			if config["Lista"] == 'S':
				lista = leituraLista()
			configurado = True

			if config['MHI'] == 'S':
				temp = MHI(API, config)
				_thread.start_new_thread(temp.str, ())
				#threadMHI.join()
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