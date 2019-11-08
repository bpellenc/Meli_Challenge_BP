from flask import Flask, request, render_template, Response, make_response, redirect, url_for, jsonify
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import httplib2, os

### OBJETO DE APLICACION DE FLASK
app = Flask(__name__)


### CREAR CARPETA DE ARCHIVOS LOCALES, SI NO EXISTE
if not os.path.exists(os.path.join(os.getcwd(), 'files')):
    os.mkdir('files')


### ESTA REGLA RELACIONA CUALQUIER ERROR 404 CON LA PLANTILLA 'error404.html'
@app.errorhandler(404)
def not_found(e):
    return render_template('error404.html'), 404


### FUNCION PRINCIPAL QUE INTENTA AUTENTICAR DE NO ESTARLO
@app.route('/', methods=['GET'])
def index():

    ### GET CREDENTIALS DEVUELVE FALSE O UN OBJETO DE CREDENCIAL
    credentials = get_credentials()
    if credentials == False:
        return redirect(url_for('oauth2callback'))
    elif credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))
    else:
        #print("Authenticated") USADO PARA LOGGING
        return render_template("index.html");

### REGLA PARA DOCUMENTACIÓN
@app.route('/docs')
def docs():
    return render_template('docs.html')


### PUNTOS DE ACCESO DE LA API REST - Ambos verifican si se está autenticado antes de realizar su función. (Si no no podrían realizarla).

### ESTA FUNCION FUE USADA AL DESARROLLAR PARA PROBAR EL FUNCIONAMIENTO
### AHORA SE LA COMENTA

# @app.route('/search')
# def search():

#     ### ESTAS TRES LINEAS AUTORIZAN LA CONEXION Y GENERAN UN OBJETO DE LA API DE GOOGLE QUE NOS PERMITE INTERACTUAR CON LA CUENTA
#     credentials = get_credentials()
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('drive', 'v3', http=http)

#     #print(service.files().list().execute()) USADO PARA LOGGING

#     return make_response('', 200)

@app.route('/search-in-doc/<id>', methods=['GET'])
def search_in_doc(id):

    # COMPROBAR SI ESTAMOS AUTENTICADOS

    if get_credentials():

        # OBTENER PALABRA CLAVE Y VERIFICAR QUE EXISTE, DE NO SER ASI, ARROJAR ERROR

        search_string = request.args.get('word')
        if search_string == None:
            resp = make_response("HTTP/1.1 400 POR FAVOR INCLUYA UNA PALABRA A BUSCAR", 400)
            return resp



        else:

            ### ESTAS TRES LINEAS AUTORIZAN LA CONEXION Y GENERAN UN OBJETO DE LA API DE GOOGLE QUE NOS PERMITE INTERACTUAR CON LA CUENTA

            credentials = get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('drive', 'v3', http=http)

            ### SE ENVUELVE LAS OPERACIONES DE BUSQUEDA EN UNA ESTRUCTURA DE CONTROL DE EXCEPCIONES PARA MANEJAR LOS ERRORES QUE SURJAN

            try:

                ### ESTA VARIBLE SIRVE PARA FILTRAR LA QUERY USANDO EL FORMATO PROPORCIONADO POR GOOOGLE

                querystring = "fullText contains '{}'".format(request.args.get('word'))

                ### BUSCAMOS TODOS LOS ARCHIVOS QUE CONTENGAN LA PALABRA QUE QUEREMOS FILTRAR

                list_request = service.files().list(q = querystring).execute()


                ### VEMOS SI EN ESOS ARCHIVOS EXISTE ALGUNO QUE TENGA LA ID QUE NOS FUE PROPORCIONADA

                found = False

                for file in list_request['files']:
                    if file['id'] == id:
                        found = True

                ### CODIGO CASI EXPLÍCITO

                if found:
                    return make_response('HTTP/1.1 200 PALABRA ENCONTRADA', 200)
                else:
                    return make_response('HTTP/1.1 404 PALABRA NO ENCONTRADA', 404)

            except Exception as e:
                ### AQUI PUEDE SUCEDER QUE HAYA ALGUN OTRO ERROR NO TENIDO EN CUENTA Y QUE ESO SE REPORTE COMO UN ARCHIVO NO ENCONTRADO, PERO LAS PROBABILIDADES SON MUY BAJAS
                #print(e) USADO PARA LOGGING
                return make_response('HTTP/1.1 404 ARCHIVO NO ENCONTRADO', 404)


    else:

        ### EN CASO DE NO ESTAR AUTORIZADO

        return make_response('Para obtener acceso a su cuenta de Drive y habilitar la API diríjase al índice de la página.', 401)


### CREAR NUEVO ARCHIVO

@app.route('/file', methods=['POST'])
def file():

    # COMPROBAR SI ESTAMOS AUTENTICADOS

    if get_credentials():

        # CUBRIR EL CASO EN EL QUE NO ESTÉN LOS DATOS NECESARIOS EN LA SOLICITUD POST

        if 'titulo' not in request.form or 'descripcion' not in request.form:
            return make_response('HTTP/1.1 400 PARÁMETROS INCORRECTOS', 400)

        # CREAR EL ARCHIVO

        else:

            ### ESTAS TRES LINEAS AUTORIZAN LA CONEXION Y GENERAN UN OBJETO DE LA API DE GOOGLE QUE NOS PERMITE INTERACTUAR CON LA CUENTA

            credentials = get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('drive', 'v3', http=http)

            ### SE ENVUELVE LA CREACION EN UNA ESTRUCTURA DE CONTROL DE EXCEPCIONES PARA MANEJAR LOS ERRORES QUE SURJAN

            try:

                ### SOLICITAMOS UNA NUEVA ID PARA EL ARCHIVO NUEVO
                newid = service.files().generateIds(count = 1, space= 'drive').execute()
                #print(newid['ids'][0]) USADO PARA LOGGING

                ### CREAMOS LOS METADATOS DE NUESTRO ARCHIVO
                newfilebody = {
                    'name': request.form['titulo'],
                    'id': newid['ids'][0],
                    'mimeType': 'text/plain'
                }

                ### ESTAS TRES LINEAS CREAN EL RESPALDO FÍSICO DEL ARCHIVO A SUBIR CON SU NOMBRE Y CONTENIDO Y LO GUARDAN EN LA CARPETA files
                newfiledata = open('files/{} - {}.txt'.format(request.form['titulo'], newid['ids'][0]), 'w')
                newfiledata.write(request.form['descripcion'])
                newfiledata.close()

                ### SE DECLARA EL TIPO DE FORMATO DE CUERPO DE ARCHIVO COMPATIBLE CON LA API DE GOOGLE

                media = MediaFileUpload('files/{} - {}.txt'.format(request.form['titulo'], newid['ids'][0]), mimetype = 'application/vnd.google-apps.document')

                ### SE DECLARA Y CREA EL ARCHIVO

                newfile = service.files().create(body = newfilebody, media_body = media).execute()

                ### ESTA ESTRUCTURA SE CREA PARA INFORMAR AL USUARIO DE LA CREACION EXITOSA DEL ARCHIVO

                filedata = {
                    'id': newid['ids'][0],
                    'titulo': request.form['titulo'],
                    'descripcion': request.form['descripcion']
                }

                ### SE RESPONDE LA PETICION

                return make_response("HTTP/1.1 200 NUEVO ARCHIVO CREADO\n{}".format(filedata, 200))


            except Exception as e:

                #print(e) USADO PARA LOGGING
                return make_response('HTTP/1.1 500 ERROR EN LA CONEXIÓN', 500)
    else:
        ### EN CASO DE NO ESTAR AUTORIZADO
        return make_response('Para obtener acceso a su cuenta de Drive y habilitar la API diríjase al índice de la página.', 401)

### FUNCIONES DE AUTENTICACIÓN DE OAUTH - Tomadas de https://www.prahladyeri.com/blog/2016/12/how-to-create-google-drive-app-python-flask.html


### ESTA FUNCION ES LA ENCARGADA DE OBTENER Y VALIDAR, SI EXISTEN, LAS CREDENCIALES ACTUALES DE SESION CON LA API DE GOOGLE DRIVE
def get_credentials():

    ### ESTAS TRES LINEAS DE CODIGO USAN EL ARCHIVO JSON SI EXISTE
    credential_path = 'credentials.json'
    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        #print('Credentials not found') USADO PARA LOGGING
        return False
    else:
        #print('Credentials fetched succesfully') USADO PARA LOGGING
        return credentials

### ESTA VISTA ES LA ENCARGADA DE REALIZAR Y DERIVAR EL PROCESO DE AUTORIZACION A GOOGLE DRIVE. EL USUARIO VERÁ UNA VENTANA EMERGENTE EN LA QUE DEBERÁ LOGUEARSE.

@app.route('/oauth2callback')
def oauth2callback():

    flow = client.flow_from_clientsecrets('client_id.json', scope='https://www.googleapis.com/auth/drive', redirect_uri = url_for('oauth2callback', _external = True))
    flow.params['include_granted_scopes'] = 'true'

    ### SI NO ESTÁ EL TOKEN DE VALIDACION EN LOS PARAMETROS DE LA SOLICITUD, MOSTRAR VENTANA EMERGENTE

    if 'code' not in request.args:

        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)


    else:

        ### SI ESTÁ UTILIZARLO PARA REALIZAR LA CONEXION Y GUARDARLO EN EL ARCHIVO LOCAL credentials.json

        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)

        open('credentials.json', 'w').write(credentials.to_json())

        return redirect(url_for('index'))


### ESTO ASEGURA EJECUTAR EL SERVIDOR SOLO SI ES EL SCRIPT PRINCIPAL (NO ES LLAMADO COMO MÓDULO)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000) # CAMBIAR EL NUMERO DE PUERTO DE SER NECESARIO
