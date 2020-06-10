from iqoptionapi.stable_api import IQ_Option
from time import localtime, strftime
from biblioteca.conecta import *

#Conexão API
API = IQ_Option('bandradest@gmail.com', 'Bruno9107')
API.connect()
rec = 0

#Variaveis
#arquivo = ['19:40,USDCAD,PUT', '10:41,USDCAD,PUT', '10:49,USDCAD,PUT']
arquivo = open('lista.txt', 'r')
hora = []
minuto = []
par = []
posicao = []
i = 0
horaAtual = strftime("%H", localtime())
minutoAtual = strftime("%M", localtime())
segundoAtual = strftime("%S", localtime())
print("Aguarde... \r")
print(" -------  LENDO LISTA DE SINAIS  --------- \r")
#Lê arquivo
for linha in arquivo:
	if linha[0] != '#':
		separado = linha.split(',')
		time = separado[0].split(':')
		hora.append(time[0])
		minuto.append(time[1])
		par.append(separado[1])
		posicao.append(separado[2])
		i = i + 1
#arquivo.close()

#verifica hora atual#horaAtual = ""
try:
	horaAtual = strftime("%H", localtime())
	minutoAtual = strftime("%M", localtime())
	segundoAtual = strftime("%S", localtime())
	print(horaAtual)
	index = hora.index(horaAtual)
	print(minuto[index])
	#horaAtual = strftime("%H", localtime())
except:
	print("Nenhuma posição para a hora atual")

#While
load = '|'
configurado = False
tempAnterior = strftime("%S", localtime())
while True:
	if API.check_connect() == False:
		conecta(API)
	else:
		if configurado == False:
			print('####  Conectado com sucesso  ########')
			print('####  Carregando Configuracao  ########')
			carregaConfig(API)
			configurado = True
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
				minutoAtual = strftime("%M", localtime())
				horaAtual = strftime("%H", localtime())
				print(load, ' - ', horaAtual,':', minutoAtual, ':', segundoAtual, end="\r")
	