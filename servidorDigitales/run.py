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


@app.route("/upload", methods=['POST'])
def uploader():
 	global filename
 	if request.method == 'POST':
 	# obtenemos el archivo del input "archivo"
 		f = request.files['archivo']
 		filename = secure_filename(f.filename)
 		# Guardamos el archivo en el directorio "Archivos PDF"
 		f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
 		# Retornamos una respuesta satisfactoria
 		print("Se ha guardado el archivo de nombre:", filename)

 	return redirect("/")
 	

@app.route("/verifyCode", methods=['POST'])
def verify():
	global MENSAJE_CONSOLA
	v = request.form['verificar_data']
	if v == 'true':
		print('entre')
		COMANDO_UPLOAD_CODE_FPGA = "ps"
		MENSAJE_CONSOLA = os.popen(COMANDO_UPLOAD_CODE_FPGA).read()
		print('MENSAJE_CONSOLA',MENSAJE_CONSOLA)
	return redirect("/")


# Iniciamos la aplicación

if __name__ == "__main__":
	app.run(host='0.0.0.0',port = 8383)