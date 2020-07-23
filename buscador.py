from iqoptionapi.stable_api import IQ_Option
import iqoptionapi.country_id as Pais
import time, logging
from datetime import datetime, date, timedelta
from dateutil import tz
import getpass
import sys

logging.disable(level=(logging.DEBUG))

print('\n - Buscador de Traders - \n')

login = input("Digite seu e-mail cadastrado na IqOption: ")
senha = getpass.getpass("Digite sua senha (por segugurança ela ficar invisível): ")
API = IQ_Option(login, senha)
API.connect()

API.change_balance('REAL') # PRACTICE / REAL

while True:
	if API.check_connect() == False:
		print('Erro ao se conectar')
		
		API.connect()
	else:
		print('\n\nConectado com sucesso')
		break
	
	time.sleep(1)

def timestamp_converter(x):
	hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
	hora = hora.replace(tzinfo=tz.gettz('GMT'))
	
	return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6]


primeiro_nome = input('\nDigite o primeiro nome caso souber: ')
outro_nome = input('\nCaso souber outra parte do nome, digite: ')
outro_nome = '3214768413168431354684' if outro_nome == '' else outro_nome

print('\nEscreva a sigla do pais ou deixe vazio', end='')
while True:
	pais = input(':')
	if pais != '':
		if pais.upper() in Pais.ID:
			break
	else:
		break
		
print('\n1 - Metodo Rapido: Busca apenas pelo primeiro nome')
print('2 - Metodo Lento: Realiza uma busca completa')
print('3 - Metodo Misto: Se o primeiro nome for igual, procura pelo outro nome')
metodo = input('Digite a opcao: ')
metodo = 3 if metodo == '' or int(metodo) >= 4 else metodo

print('\n Busca iniciada, aguarde..\n')

last = 1
for i in range(1, 1000):
	quantidade = int(i) * 500
	
	data = API.get_leader_board('Worldwide' if pais == '' else pais.upper(), last, quantidade, 0)
	
	for colocacao in data['result']['positional']:
		nome_ranking = data['result']['positional'][colocacao]['user_name']

		if int(metodo) == 2 or int(metodo) == 3 and primeiro_nome.lower() in nome_ranking.lower():
			segunda_busca = API.get_user_profile_client(data['result']['positional'][colocacao]['user_id'])
		else:
			segunda_busca = {'user_name': '', 'registration_time': 0}
		
		if (int(metodo) == 1 and primeiro_nome.lower() in nome_ranking.lower()) or (int(metodo) == 2 and primeiro_nome.lower() in nome_ranking.lower() or outro_nome.lower() in segunda_busca['user_name'].lower()) or (int(metodo) == 3 and primeiro_nome.lower() in nome_ranking.lower() and outro_nome.lower() in segunda_busca['user_name'].lower()): 
		
			if int(metodo) != 2:
				segunda_busca = API.get_user_profile_client(data['result']['positional'][colocacao]['user_id'])
			
			print('\n\n ['+str(colocacao)+']Nome:',nome_ranking,'/',segunda_busca['user_name'])
			print(' User ID:',data['result']['positional'][colocacao]['user_id'])
			print(' Se registrou em:',timestamp_converter(segunda_busca['registration_time']))
			print(' Pais: '+data['result']['positional'][colocacao]['flag'])
			print(' Imagem de perfil:',(segunda_busca['img_url'] if segunda_busca['img_url'] != '' else 'Imagem nao disponivel'))
			print(' Faturamento esta semana:',round(data['result']['positional'][colocacao]['score'], 2))
			print('\n')
			input('Deseja continuar? Aperte enter, para encerrar o codigo, aperte CRTL+C\n')
			
	
	if len(data) == 0:
		print('\nBusca finalizada\n')
		break
	
	last = quantidade