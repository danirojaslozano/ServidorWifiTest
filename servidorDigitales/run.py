# Importamos todo lo necesario
import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# instancia del objeto Flask
app = Flask(__name__)
# Carpeta de subida
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

# Funcion para apagar la camara
def prenderCamara():
	print('prender')
	#COMANDO_START_STREAMING ='obs --startstreaming'
	#ans = os.popen(COMANDO_START_STREAMING).read()
	#print(ans)

@app.route("/")
def index():
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

 	return redirect("/")
 	
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
	return redirect("/")


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