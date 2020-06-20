# Importamos todo lo necesario
import os
from flask import Flask, render_template, request, redirect, url_for,session,g
from werkzeug.utils import secure_filename
from datetime import datetime

### clase Usuario
class User:
	def __init__(self, id, username, password, start_Time, final_Time):
		self.id = id
		self.username = username
		self.password = password
		self.start_Time =  start_Time
		self.final_Time = final_Time

		def __repr__(self):
			return f'<User: {self.username}>'

	def itsTime(self):
		now = datetime.now().time()
		tiempoInicioDT = datetime.strptime(str(self.start_Time), "%H:%M:%S").time()
		tiempoFinalDT = datetime.strptime(str(self.final_Time), "%H:%M:%S").time()
		if now > tiempoInicioDT and now < tiempoFinalDT:
			return True
		return False


### leer usuarios, contraseñas y hotas de un archivo .csv
import pandas as pd
new_names = ['LOGIN', 'PASSWD', 'INICIO', 'FIN', 'INTENTOS']
df = pd.read_csv('SED-virtuallab.csv',sep=';',skiprows=1,names=new_names)

users = []
users.append(User(id=1, username='Daniela', password='password', start_Time="00:00:00", final_Time="23:59:00"))

for index, row in df.iterrows():
	users.append(User(id=index+2, username= row['LOGIN'], password=row['PASSWD'], start_Time=row['INICIO'], final_Time=row['FIN']))


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
			return redirect(url_for('index'))
		else:
			mensaje_Error = "Password incorrect"
			return redirect(url_for('error'))

	return render_template('login.html')

@app.route("/error")
def error():
	global mensaje_Error
	return render_template('error.html', mensaje_Error = mensaje_Error)

@app.route("/control")
def index():
	global mensaje_Error
	if not g.user:
		return redirect(url_for('login'))
	if not  g.user.itsTime():
		mensaje_Error = "Out of time"
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
	app.run(host='0.0.0.0',port = 8383)