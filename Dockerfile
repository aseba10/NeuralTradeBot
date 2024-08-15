# Usa la imagen oficial de Apache Airflow con Python 3.10
FROM apache/airflow:2.8.2-python3.10

# Define el directorio de trabajo dentro del contenedor
WORKDIR /opt/airflow

# Copia solamente el archivo requirements.txt al directorio de trabajo actual
COPY requirements.txt .

# Instala las dependencias adicionales especificadas en el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade urllib3


# Copia el resto de los archivos necesarios para tu proyecto de Airflow
COPY . .
