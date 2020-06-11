# ____________________________________________________________________________                                                                       
#     ____________________     __          __       ___   ____ ___   ____ 
#    /  _/  _/ ____/ ____/    / /   ____ _/ /_     |__ \ / __ \__ \ / __ \
#    / / / // __/ / __/      / /   / __ `/ __ \    __/ // / / /_/ // / / /
#  _/ /_/ // /___/ /___     / /___/ /_/ / /_/ /   / __// /_/ / __// /_/ / 
# /___/___/_____/_____/    /_____/\__,_/_.___/   /____/\____/____/\____/  
# ____________________________________________________________________________                                                                       
# servidor.py
# Autor: Daniela Rojas
# Muestra en consola los datos que estan llegando al servidor a través de Wifi.
# ____________________________________________________________________________                                                                       
#

import time
import socket
import os

TIEMPO_INICIO = time.time() #Variable que guarda el tiempo en el que el servidor empezó a correr
fechaYhora = "" #Variable para etiquetar los datos con fechas y horas
nuevaLineaDatos = [0,0,0,0,0,0,0,0,0,""]

UDP_IP = socket.gethostbyname(socket.gethostname())
UDP_PORT = 9001 ## Este puerto debe coincidir con el configurado en el módulo wifi para el envío de datos
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((UDP_IP, UDP_PORT))
print("____________________________________________")
print("Puerto Abierto")
print("____________________________________________")	
print("Esperando ... ")

while True:
	data, addr = s.recvfrom(1024)
	data = data.decode()
	file = open(str(TIEMPO_INICIO)+".txt","a") #Se activa (crea) el archivo para guardar (escribir) un nuevo dato
	try:
		ArrayData = data.split("#")
		Ax = float(ArrayData[0])
		Ay = float(ArrayData[1])
		Az = float(ArrayData[2])
		Gx = float(ArrayData[3])
		Gy = float(ArrayData[4])
		Gz = float(ArrayData[5])
		IdClient = int(ArrayData[6])-1
		NumeroPaquete = float(ArrayData[7])
		fechaYhora = str(time.strftime("%c"))
		nuevaLineaDatos = [ Ax,Ay,Az,Gx,Gy,Gz,IdClient,NumeroPaquete, fechaYhora]
		file.write( ( fechaYhora + "	 %.1f	 %.5f	 %.5f	 %.5f	 %.5f	 %.5f	 %.5f	 %.5f"%(NumeroPaquete, IdClient, Ax, Ay, Az, Gx, Gy, Gz) )  + "	\n" )
		print(( fechaYhora + "	 %.1f	 %.5f	 %.5f	 %.5f	 %.5f	 %.5f	 %.5f	 %.5f"%(NumeroPaquete, IdClient, Ax, Ay, Az, Gx, Gy, Gz) ) + "	\n" )
		file.close() #Cada vez que el servidor recibe un dato lo guarda adecuamente en el archivo plano de texto para evitar perdidas de datos
	except Exception as e:
		print(e)
		print("Error en dato")


# ____________________________________________________________________________                                                                       
# ______            _      _        ______      _           
# |  _  \          (_)    | |       | ___ \    (_)          
# | | | |__ _ _ __  _  ___| | __ _  | |_/ /___  _  __ _ ___ 
# | | | / _` | '_ \| |/ _ \ |/ _` | |    // _ \| |/ _` / __|
# | |/ / (_| | | | | |  __/ | (_| | | |\ \ (_) | | (_| \__ \
# |___/ \__,_|_| |_|_|\___|_|\__,_| \_| \_\___/| |\__,_|___/
#                                             _/ |          
#                                            |__/           
# ____________________________________________________________________________                                                                       
#
#