# Importamos todo lo necesario
import os
from flask import Flask, render_template, request, redirect, url_for,session,g
from werkzeug.utils import secure_filename
from datetime import datetime

### clase Usuario
class User:
	def __init__(self, id, username, password, start_Time, final_Time, conecctions):
		self.id = id
		self.username = username
		self.password = password
		self.start_Time =  start_Time
		self.final_Time = final_Time
		self.conecctions = int(conecctions)

		[horas_finales, minutos_finales, segundos_finales] = final_Time.split(":")
		self.horas_finales = horas_finales
		self.minutos_finales = minutos_finales
		self.segundos_finales = segundos_finales

		def __repr__(self):
			return f'<User: {self.username}>'

		### verifica si el usuario esta en turno para acceder a la verificación
	def itsTime(self):
		now = datetime.now().time()
		tiempoInicioDT = datetime.strptime(str(self.start_Time), "%H:%M:%S").time()
		tiempoFinalDT = datetime.strptime(str(self.final_Time), "%H:%M:%S").time()
		if now > tiempoInicioDT and now < tiempoFinalDT:
			return True
		return False

		###  revisa la cantidad de conecciones con el usuario para saber si es posible conectar una nueva
	def availableConnection(self):
		if self.conecctions>0:
			return True
		return False

		###  resta uno a la cantidad de intentos
	def userConected_log_in(self):
		self.conecctions = self.conecctions -1
		return self.conecctions

		###  suma uno a la cantidad de intentos, porque un usuario hizo logOut
	def userConected_log_out(self):
		self.conecctions = self.conecctions + 1
		return self.conecctions



### leer usuarios, contraseñas y hotas de un archivo .csv
global df
import pandas as pd
new_names = ['LOGIN', 'PASSWD', 'INICIO', 'FIN', 'INTENTOS']
df = pd.read_csv('SED-virtuallab.csv',sep=';',skiprows=1,names=new_names)

global schedule_horas, schedule_usuarios,schedule_color
schedule_horas = ['']
schedule_usuarios =['']
schedule_color = ['']

users = []
users.append(User(id=1, username='admin', password='password', start_Time="00:00:00", final_Time="23:59:59",conecctions =2))

for index, row in df.iterrows():
	if not existeUsuario(row['LOGIN']):
		users.append(User(id=index+2, username= row['LOGIN'], password=row['PASSWD'], start_Time=row['INICIO'], final_Time=row['FIN'], conecctions = row['INTENTOS']))
	else:
		
users.append(User(id=40, username='admin2', password='secret', start_Time="00:00:00", final_Time="23:59:59",conecctions =1))


def existeUsuario(username_buscar):
	for u in users:
		if (u.username == username_buscar):
			return True

	return False



# instancia del objeto Flask
app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

# variable global para cambiar el mensaje en la pagina de error
global mensaje_Error
mensaje_Error = " Error "

# Carpeta donde se guardan los archivos que llegan
app.config['UPLOAD_FOLDER'] = './received_Files'
global filename
global MENSAJE_CONSOLA
filename = " "
MENSAJE_CONSOLA = ""

# serial
import serial
global estadosSW
estadosSW = [ '' , '']
#Creamos los parametros para comunicacion serial
DIRECCION_Serial = "/dev/tty.usbmodem14201"
BAUD_RATE = 9600
try:
	serialFPGA = serial.Serial(DIRECCION_Serial, baudrate=BAUD_RATE)
	print("Comunicacion Serial inicializado")
except:
	print("No fue posible iniciar el serial")

	
#Iniciamos la comunicacion Serial
def iniciarSerial():
	try:
		serialFPGA = serial.Serial(DIRECCION_Serial, baudrate=BAUD_RATE)
		print("Comunicacion Serial inicializado")
		return 1
	except:
		print("No fue posible iniciar el serial")
		return 0

# Funcion para enviar por serial
def enviarPorSerial(mensaje):
	serialFPGA.write( ( (str(mensaje)+'\n') ).encode() )

# Funcion para apagar la camara
def apagarCamara():
	#COMANDO_SHUT_DOWN_STREAMING ='killall obs'
	#ans = os.popen(COMANDO_SHUT_DOWN_STREAMING).read()
	#print(ans)
	print('apagar Camara')

# Funcion para prender la camara
def prenderCamara():
	print('prender')
	#COMANDO_START_STREAMING ='obs --startstreaming'
	#ans = os.popen(COMANDO_START_STREAMING).read()
	#print(ans)

# funcion donde se actualiza el cronograma de los grupos para ser moestrado en la pagina de login
def actualizar_schedule():
	global schedule_horas, schedule_usuarios,schedule_color
	schedule_horas = []
	schedule_usuarios =[]
	schedule_color = []
	for index, row in df.iterrows():
		now = datetime.now().time()
		tiempoInicioDT = datetime.strptime(str(row['INICIO'] ), "%H:%M:%S").time()
		tiempoFinalDT = datetime.strptime(str(row['FIN']), "%H:%M:%S").time()
		if now > tiempoInicioDT and now < tiempoFinalDT:
			if len(schedule_horas)>=1:
				schedule_horas = [schedule_horas[-1]]
				schedule_usuarios = [schedule_usuarios[-1]]
				schedule_color = [schedule_color[-1]]
			schedule_horas.append(row['INICIO'])
			schedule_usuarios.append(row['LOGIN'])
			schedule_color.append('stage-verde-disponible')
		elif now > tiempoInicioDT and now > tiempoFinalDT:
			schedule_horas.append(row['INICIO'])
			schedule_usuarios.append(row['LOGIN'])
			schedule_color.append('stage-rojo-no-disponible')
			#pass
		else:
			schedule_horas.append(row['INICIO'])
			schedule_usuarios.append(row['LOGIN'])
			schedule_color.append('stage-azul-futuro')

	if len(schedule_horas)==0:
		schedule_horas.append('--:--')
		schedule_usuarios.append('admin time')
		schedule_color.append('stage-rojo-no-disponible')
	if len(schedule_horas)>=10:
		schedule_horas = schedule_horas[0:10]
		schedule_usuarios = schedule_usuarios[0:10]
		schedule_color = schedule_color[0:10]
	return True

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		user = [x for x in users if x.id == session['user_id']][0]
		g.user = user

@app.route("/")
def inicio():
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	global mensaje_Error
	if request.method == 'POST':
		session.pop('user_id', None)

		username = request.form['username']
		password = request.form['password']

		try:
			user = [x for x in users if x.username == username][0]
		except Exception as e:
			mensaje_Error = "User incorrect"
			return redirect(url_for('error'))
		
		if user and user.password == password:
			session['user_id'] = user.id

			if not  user.availableConnection():
				mensaje_Error = " No additional sessions available  "
				return redirect(url_for('error'))
			else:
				user.userConected_log_in()
				return redirect(url_for('index'))
		else:
			mensaje_Error = "Password incorrect"
			return redirect(url_for('error'))


	global schedule_horas, schedule_usuarios,schedule_color
	actualizar_schedule()

	return render_template('login.html',len = len(schedule_horas), schedule_horas=schedule_horas, schedule_usuarios=schedule_usuarios,schedule_color=schedule_color)


@app.route("/error")
def error():
	global mensaje_Error
	return render_template('error.html', mensaje_Error = mensaje_Error)

@app.route("/logout")
def logoutfunction():
	global mensaje_Error
	mensaje_Error = " Successful logout"
	if not g.user:
		return redirect(url_for('login'))
	else:
		g.user.userConected_log_out()
	return render_template('error.html', mensaje_Error = mensaje_Error)


@app.route("/control")
def index():
	global mensaje_Error
	if not g.user:
		return redirect(url_for('login'))
	if not  g.user.itsTime():
		mensaje_Error = " Out of time "
		return redirect(url_for('error'))

	print('itstimeUser', g.user.itsTime())
	apagarCamara()
		# renderizamos la plantilla "index.html"
	return render_template('index.html', filename = filename, MENSAJE_CONSOLA = MENSAJE_CONSOLA)

#### Ruta para recibir archivo de projecto
@app.route("/upload", methods=['POST'])
def uploader():
 	global filename
 	if request.method == 'POST':
 		# obtenemos el archivo del input "archivo"
 		f = request.files['archivo']
 		filename = secure_filename(f.filename)
 		# Eliminamos el archivo actual si existe
 		if os.path.exists("./received_Files/BB_SYSTEM.sof"):
 			os.remove('./received_Files/BB_SYSTEM.sof')
 		# Guardamos el archivo en el directorio "Archivos PDF"
 		f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
 		# Retornamos una respuesta satisfactoria
 		print("Se ha guardado el archivo de nombre:", filename)

 	return redirect("/control")
 	
#### Ruta para verificar y cargar el codigo a la FPGA
@app.route("/verifyCode", methods=['POST'])
def verify():
	global MENSAJE_CONSOLA
	v = request.form['verificar_data']
	if v == 'true':
		COMANDO_UPLOAD_CODE_FPGA ='ps'
		#COMANDO_UPLOAD_CODE_FPGA = "quartus_pgm -m jtag -o 'p;./received_Files/BB_SYSTEM.sof"
		MENSAJE_CONSOLA = os.popen(COMANDO_UPLOAD_CODE_FPGA).read()
		print('MENSAJE_CONSOLA',MENSAJE_CONSOLA)
		iniciarSerial()
	return redirect("/control")


### Ruta para recibir la información del switch Camara, para así comenzar a obtener video
@app.route('/switchCamara', methods = ['POST'])
def switchC():
	estadoCamaraNuevo = request.form['CAMARA']
	print("la nueva accion de la CAMARA es : "  + estadoCamaraNuevo)
	if(estadoCamaraNuevo=='true'):
		prenderCamara()
	elif(estadoCamaraNuevo=='false'):
		apagarCamara()
	return ""


### Ruta para recibir la información de los swithches para la FPGA
@app.route('/switchFPGA', methods = ['POST'])
def switchsSeñales():
	global estadosSW
	estadoSW1 = request.form['SW1']
	if not estadoSW1 == '00':
		estadosSW[0] = estadoSW1
	estadoSW2 = request.form['SW2']
	if not estadoSW2 == '00':
		estadosSW[1] = estadoSW2
	print(estadosSW)
	enviarPorSerial(estadosSW)
	return ""



# Iniciamos la aplicación

if __name__ == "__main__":
	app.run(host='0.0.0.0',port = 8383, debug= True)