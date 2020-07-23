from iqoptionapi.stable_api import IQ_Option
import getpass
import sys

print('\n - Buscador de Top Traders - \n')
#Pegar Login e senha
login = input("Digite seu e-mail cadastrado na IqOption: ")
senha = getpass.getpass("Digite sua senha (por segugurança ela ficar invisível): ")

#Conexão API
API = IQ_Option(login, senha)
API.connect()
API.change_balance('REAL') # PRACTICE / REAL

ranking = API.get_leader_board('Worldwide', 1, 10, 0)


for n in ranking['result']['positional']:
	id = ranking['result']['positional'][n]['user_id']
	perfil_info = API.get_user_profile_client(id)

	print('---- POSIÇÂO',n,'------')
	print('Nome:', perfil_info['user_name'])
	print('Status:', perfil_info['status'])
	print('Conta Demo?', 'Não' if perfil_info['is_demo_account'] == False else 'Sim')
	print('Conta VIP?', 'Não' if perfil_info['is_vip'] == False else 'Sim')

	if perfil_info['status'] == 'online':
		op = API.get_users_availability(id)
		
		try:			
			tipo = op['statuses'][0]['selected_instrument_type']
			par = API.get_name_by_activeId(op['statuses'][0]['selected_asset_id']).replace('/', '')
				
			print('Tipo Intrumento:', tipo)			
			print('Vendo Par:', par)
			
			
		except:
			pass
	print()