# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requerimientos
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la aplicación manteniendo la estructura
COPY . /app

# Expone el puerto que la aplicación utilizará
EXPOSE 8000

# Comando para ejecutar la aplicación usando el módulo app
CMD ["python", "run.py"]