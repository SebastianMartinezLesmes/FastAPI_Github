# GitHub-Elk

```Dashboard``` para monitoreamiento de datos relevantes a la organización.

## Descripción

Desarrollo de un dashboard en la suite ```ELK``` (Elasticsearch, Backend / Logstash, Kibana) 
que visualice de manera eficiente y efectiva el uso de GitHub por parte de la organización. Este dashboard extraerá datos específicos utilizando la API de GitHub y los 
presentará en Kibana para análisis y monitoreo.

## Prerrequisitos 📋
 
Antes de comenzar, asegúrate de tener instalado lo siguiente:

- [Docker](https://docs.docker.com/desktop/install/windows-install/)
- Docker compose
- [ElasticSearch](https://www.elastic.co/es/downloads/past-releases/elasticsearch-7-17-18)
- [Kibana](https://www.elastic.co/es/downloads/past-releases/kibana-7-17-18)
- [Python](https://www.python.org/downloads/release/python-3117/)

## Instalación 🔧
Una guía paso a paso sobre cómo configurar el entorno de desarrollo e instalar todas las dependencias.

### Clonación del Repositorio 🔄
Para obtener una copia del proyecto en tu máquina local, necesitarás clonar el repositorio de GitHub. Asegúrate de tener Git instalado en tu sistema antes de proceder. Si no lo tienes, puedes descargarlo e instalarlo desde aquí.

Abre una terminal y ejecuta el siguiente comando:

```
git clone https://github.com/tu-usuario/metricas-github-elk.git
```

### Creación del entorno virtual
```python
python -m venv nombre_del_entorno
``` 
### Entrar en el entorno virtual
```
nombre_del_entorno\Scripts\activate
```
### Instalar dependencias
```
pip install -r requeriments.txt
```
### Para visualizar las dependencias de este proyecto, consulta el archivo requirements.txt con las siguientes líneas en la terminal
```
pip freeze requeriments.txt
```
```
pip list
```
### Salir del entorno virtual
```
deactivate
```
### Ejecutar servidor local (Generación de cache)
```
uvicorn main:app --reload
```
### Ejecutar servidor local 
```
set PYTHONDONTWRITEBYTECODE=1 && uvicorn main:app --reload
```
## Ejecutando las Pruebas (LOCAL) ⚙️

Para probar este proyecto localmente, necesitas configurar y ejecutar Elasticsearch y Kibana, además de levantar el servidor FastAPI. 

### Usando Docker 

Puedes construir y ejecutar tu proyecto utilizando ```docker compose up```. Esto creará los contenedores necesarios para Elasticsearch, Kibana y tu aplicación FastAPI, facilitando la gestión de las dependencias y la configuración.

Para ello, asegúrate de tener ```Docker``` y ```Docker Compose``` instalados en tu máquina, y luego ejecuta:

```docker
docker compose up --build -d
``` 
Este comando construirá y levantará todos los servicios:
-   Elasticsearch. 
-   Kibana. 
-   FastAPI.

### Levantamiento local (OPCIONAL)

Primero, debes tener Elasticsearch y Kibana instalados y ejecutándose en tu máquina. Puedes descargarlos directamente desde sus sitios oficiales:
 
- [Elasticsearch](https://www.elastic.co/es/downloads/past-releases/elasticsearch-7-17-18)
 
- [Kibana](https://www.elastic.co/es/downloads/past-releases/kibana-7-17-18)

Con Elasticsearch y Kibana ejecutándose, el siguiente paso es levantar el servidor FastAPI. Esto permitirá que la aplicación backend se comunique con Elasticsearch y envíe los datos para ser visualizados en Kibana.

1. Configura las variables de entorno: Antes de iniciar el servidor, puedes configurar las variables de entorno necesarias para la aplicación.

2. Levantar el servidor FastAPI: Ejecuta el siguiente comando en tu terminal:

```python
set PYTHONDONTWRITEBYTECODE=1 && uvicorn main:app --reload
``` 

Este comando establece la variable PYTHONDONTWRITEBYTECODE para evitar la generación de archivos .pyc

### ARQUITECTURA BACKEND 🔩

El proyecto GitHub-Elk utiliza una arquitectura modular. A continuación, se describe la función de cada uno de los directorios y archivos principales:

#### Estructura de Carpetas del Proyecto

- `app/` - Directorio principal que contiene la lógica del backend y los elementos necesarios para la ejecución de la aplicación.
  - `api/` - Contiene los controladores que gestionan las solicitudes y respuestas de la API, organizados por recursos como commits, usuarios y repositorios.
    - `routes/` - Define las rutas de la API que se corresponden con las diferentes operaciones de la aplicación, como la obtención de commits, manejo de usuarios y gestión de repositorios.
  - `schema/` - Define los esquemas de datos y modelos utilizados en la aplicación, lo que facilita la validación y serialización de datos para las respuestas y peticiones de la API.
  - `services/` - Contiene la lógica de negocio y los servicios de la aplicación que interactúan con las llamadas a la api externas.
- `docs/` - Documentación técnica y guías de uso para el proyecto.
- `elasticsearch/` - Configuración para ElasticSearch.
- `kibana/` - Configuración para Kibana.
- `.env` - Archivo que almacena las variables de entorno necesarias para la configuración del proyecto.
- `.gitignore` - Lista de archivos y directorios que Git ignorará.
- `config` - Almacenamiento de variables de entorno GLOBALES.
- `docker-compose` - Archivo de configuración para Docker Compose que define los servicios, redes y volúmenes necesarios para ejecutar la aplicación en contenedores.
- `Dockerfile` - Imagen de Docker para la aplicación, especificando los pasos y las dependencias necesarias.
- `main` - Archivo principal que inicia la aplicación FastAPI.
- `requirements` - Lista de todas las dependencias externas del proyecto que se deben instalar para que la aplicación funcione correctamente.
- `wait-for-es` - Script de shell utilizado para controlar el inicio de la aplicación hasta que Elasticsearch esté disponible.


### ARQUITECTURA PROYECTO 🔩

**1. GitHub API:**
La API de GitHub es el punto de partida, donde se obtiene la información. Este servicio interactúa con GitHub para buscar información relevante a la organización ```Grupo ASD```, probablemente relacionados con repositorios, commits, issues, o cualquier dato que GitHub expone a través de su API.

**2. FastAPI Backend:**
El backend de FastAPI consume la API de GitHub. Significa que hace llamadas a la API de GitHub y procesa la información recibida.
Este backend es responsable de realizar operaciones adicionales con los datos, como la autenticación, la lógica de negocio, transformaciones de datos, y finalmente servir esa información a los clientes tales como ElasticSearch y Kibana.
También actúa como un intermediario entre la API de GitHub y Elasticsearch, enviando datos a Elasticsearch para su indexación.

**3. Elasticsearch:**
Elasticsearch recibe datos del backend de FastAPI. Su función principal es indexar y almacenar grandes volúmenes de datos para permitir una búsqueda rápida y eficiente.

**4. Kibana:**
Kibana nos facilitara un servicio de visualización que se conecta a Elasticsearch.
Solicita datos a Elasticsearch, los cuales pueden ser el resultado de búsquedas o agregaciones complejas.
Una vez que recibe los datos de Elasticsearch, Kibana los utiliza para crear visualizaciones como gráficos, tablas y mapas, los cuales ayudan a los usuarios a interpretar y analizar los datos de una manera más amigable y comprensible.

**5. Docker:**
Docker proporciona un entorno de contenedorización para el backend de FastAPI, Elasticsearch y Kibana.
Cada servicio (FastAPI, Elasticsearch y Kibana) opera dentro de su propio contenedor de Docker, lo que asegura la consistencia del entorno y facilita el despliegue y la escalabilidad de los servicios.
Los contenedores de Docker proporcionan aislamiento, gestionan las dependencias y permiten que
cada servicio se ejecute en su propio entorno virtual sin interferir con los demás.

![ARQUITECTURA](docs\img\ARQUITECTURA.png)

## Construido Con 🛠️

- [Python](https://docs.python.org/3.11/) - Lenguaje de programación elegido por su simplicidad y potencia, utilizado para escribir la lógica de backend.
- [FastAPI](https://fastapi.tiangolo.com/es/) - El moderno framework web de alta performance para construir APIs con Python 3.7+.
- [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html) - Motor de búsqueda y análisis distribuido que ofrece capacidades de búsqueda en texto completo, utilizado como la base de datos para almacenar y buscar datos.
- [Kibana](https://www.elastic.co/guide/en/kibana/current/index.html) - Herramienta de visualización de datos para Elasticsearch, usada para visualizar y gestionar datos de manera gráfica en el dashboard.
- [Docker](https://docs.docker.com/) - Plataforma de contenedores utilizada para empaquetar y ejecutar la aplicación y sus servicios asociados de manera aislada y consistente en cualquier entorno.


