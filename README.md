# Documentación de la API

Se desarrollo esta API para un desafio propuesto por MercadoLibre y expone una REST API que permite interactuar con una cuenta de Google Drive ofreciendo dos funciones: buscar texto contenido en un archivo y crear un archivo nuevo.

## Instalación
Prerrequisitos

1.Tener Python 3.7 instalado y su administrador de paquetes [pip](https://pip.pypa.io/en/stable/)

# Pasos

1.Clonar el repositorio: https://github.com/bpellenc/Meli_Challenge_BP

2.Ejecutar el comando pip install -r requirements.txt dentro de la carpeta del servidor.

3.Para ejecutar el servidor utilizar el comando python main.py.

4.Para acceder a la API, desde cualquier navegador ingresar a localhost:5000. En caso de conflicto de puertos, se debe modificar manualmente al final del archivo main.py, el parámetro llamado port

# Uso de la API
## Buscar una palabra en un documento - GET
A esta función se accede mediante el endpoint /search-in-doc/:id, en donde :id represanta el código de identificación del archivo en Google Drive.

## Parámetros:
word: una cadena de texto que será buscada en el archivo

## Posibles respuestas HTTP:
* HTTP/1.1 200 SE ENCONTRÓ: La palabra especificada fue hallada en el archivo
* HTTP/1.1 400 POR FAVOR INCLUYA UNA PALABRA A BUSCAR: No se coloco parametro de busqueda
* HTTP/1.1 404 PALABRA NO ENCONTRADA: Palabra no encontrada en el archivo
* HTTP/1.1 404 ARCHIVO NO ENCONTRADO: No se encontro ningun archivo asociado al codigo de identificaciòn provisto
* HTTP/1.1 401 Para obtener acceso a su cuenta de Drive y habilitar la API diríjase al índice de la página: Este error es causado cuando la autorización para acceder a la cuenta caduca o no fue realizada aún, lo cual se soluciona accediendo al índice.

# Crear un nuevo archivo - POST
A esta función se accede mediante el endpoint /file y sirve para crear un nuevo archivo. De cada archivo creado en Google Drive se guarda una copia local en la carpeta files, dentro de la carpeta en donde sea ejecutado el servidor.

## Parámetros:
Los parámetros deberan estar alojados en los datos de formulario de la solicitud

* titulo: El título o nombre del nuevo archivo
* descripcion: El contenido del nuevo archivo

## Posibles respuestas HTTP:
* HTTP/1.1 400 PARÁMETROS INCORRECTOS: No existen los parametros titulo o descripcion en la solicitud POST.
* HTTP/1.1 200 NUEVO ARCHIVO CREADO
{'id':id, 'titulo': titulo, 'descripcion': descripcion }
Indica la creación exitosa del archivo y devuelve sus datos principales.
* HTTP/1.1 401 Para obtener acceso a su cuenta de Drive y habilitar la API diríjase al índice de la página: Este error es causado cuando la autorización para acceder a la cuenta caduca o no fue realizada aún, lo cual se soluciona accediendo al índice.
* HTTP/1.1 500 ERROR EN LA CONEXIÓN: Indica un error en la conexion con la API de Google Drive, puede ser causado al caducir la autorización de acceso, lo cual se soluciona accediendo al índice.

# Funciones utilizadas en el desarrollo
## Vistas
Las vistas son las funciones que están relacionadas directamente con una URL del servidor, o en el caso de los error handlers, con un error.

## not_found
Esta vista es la encargada de presentar una interfaz amigable al usuario en caso de que este introduzca una URL inválida. Se relaciona con la plantilla error404.html

## index
Esta vista es la encargada de mostrar la página principal al usuario y de redireccionarlo en caso de que no esté activa ninguna cuenta de Google Drive, para lo cual redirecciona a la vista oauth2callback

## docs
Esta vista es la encargada de mostrar la documentación, que es esta misma página. Se relaciona con la plantila docs.html

## search_in_doc
Esta vista es la encargada de realizar la función de buscar en un documento y toma un parametro string que utilizará como id al momento de buscar. Maneja los posibles errores que pueden surgir, informando mediante el código de respuesta HTTP y un mensaje corto.

## file
Esta vista es la encargada de realizar la función de crear un nuevo documento. Maneja los posibles errores que pueden surgir, informando mediante el código de respuesta HTTP y un mensaje corto.

## oauth2callback
Esta vista es una de las mas importantes y es la encargada de derivar el proceso de confirmacion de uso de Google Drive a Google. Para ello utiliza el id de cliente de API proporcionado por google y creado específicamente para este proyecto. Si la confirmación es exitosa, Google devuelve un código que servira como token de autorización para las llamadas que se realizarán a la API. Este token es guardado en el archivo local credentials.json

# Otros
## get_credentials
Esta función es utilizada para obtener el archivo local que contiene las credenciales de acceso a la cuenta de Google Drive del usuario y validar las mismas. Es usada extensivamente en el programa para comprobar si está autorizado el acceso a la cuenta de Google Drive.
