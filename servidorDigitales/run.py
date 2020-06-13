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

@app.route("/")
def index():
		# renderiamos la plantilla "index.html"
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
 		if path.exists("./received_Files/BB_SYSTEM.sof"):
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
	return redirect("/")


### Ruta para recibir la información del switch Camara, para así comenzar a obtener video
@app.route('/switchCamara', methods = ['POST'])
def switchMLC():
	estadoCamaraNuevo = request.form['CAMARA']
	print("la nueva accion de la CAMARA es : "  + estadoCamaraNuevo)
	if(estadoCamaraNuevo=='true'):
		print('prender')
		#COMANDO_START_STREAMING ='obs --startstreaming'
		#ans = os.popen(COMANDO_START_STREAMING).read()
		#print(ans)
	elif(estadoCamaraNuevo=='false'):
		print('apagar')
		#COMANDO_SHUT_DOWN_STREAMING ='killall obs'
		#ans = os.popen(COMANDO_SHUT_DOWN_STREAMING).read()
		#print(ans)
	return ""



# Iniciamos la aplicación

if __name__ == "__main__":
	app.run(host='0.0.0.0',port = 8383)