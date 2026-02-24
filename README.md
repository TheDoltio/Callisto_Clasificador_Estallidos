# Clasificador de Estallidos e-Callisto México

Este proyecto es una herramienta de descarga, selección y clasificación manual
de espectros dinámicos de las estaciones e-Callisto ubicadas en México.

Está pensado para facilitar la organización de eventos tipo II, III, IV y otros
registros relevantes dentro del flujo de trabajo local antes de enviarlos a
respaldo o a procesamiento posterior.


## ¿Qué hace?

El script principal automatiza:

- Creación y carga de entorno virtual
- Descarga de datos desde las estaciones mexicanas
- Clasificación manual mediante interfaz gráfica
- Respaldo opcional mediante rsync


## Modos de ejecución

Al iniciar, el programa muestra un menú con tres modos:

1) Seleccionar periodo, descargar y clasificar
   Ejecuta el selector de fechas (date_sel.py), descarga los archivos
   y abre el clasificador.

2) Seguir descargando y clasificar
   Omite el selector de fechas y continúa descargando desde la lista
   existente (wget_list.txt), luego abre el clasificador.

3) Solamente clasificar
   No descarga nada. Solo abre el clasificador con los archivos
   disponibles en raw_data.


## Clasificación

El clasificador muestra espectros dinámicos y permite etiquetar cada archivo
mediante botones:

- Tipo II
- Tipo III
- Tipo IV
- Otros
- Ruido

Al seleccionar una categoría, el archivo se mueve automáticamente a:

clas_data/Tipo_II

clas_data/Tipo_III

clas_data/Tipo_IV

clas_data/Otros

clas_data/Ruido

Esto permite mantener organizada la base de datos local antes de procesamiento
posterior.


## Respaldo

Al finalizar la clasificación, el programa solicita una ruta de respaldo.

Ejemplo:
```bash
usuario@cluster:/home/usuario/callisto_backup/
```
Si se proporciona una ruta válida, se ejecuta:
```bash
rsync -avz --progress ../clas_data/ DESTINO
```
Si no se proporciona ruta, el respaldo se omite.


## Instalación

Clona el repositorio:
```bash
git clone https://github.com/TheDoltio/Callisto_Clasificador_Estallidos/
cd Callisto_Clasificador_Estallidos
chmod +x clasificador
```
En caso necesario:
```bash
chmod +x clasificador
chmod +x src/date_sel.py
chmod +x src/clasificador.py
```

## Ejecución

Desde la carpeta raíz del proyecto:
```bash
./clasificador
```
El script:

- Crea el entorno virtual si no existe
- Instala dependencias necesarias
- Muestra el menú de modos
- Ejecuta el flujo correspondiente


## Dependencias

Se instalan automáticamente dentro del entorno virtual:

- numpy
- matplotlib
- astropy
- scipy

En sistemas Linux puede ser necesario instalar:
```bash
sudo apt install python3-tk
```
para el funcionamiento de la interfaz gráfica.

La estructura actual permite extender el proyecto fácilmente
(atajos de teclado, conteo de progreso, deshacer clasificación,
integración directa con clúster, etc.).
