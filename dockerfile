# Usa una imagen base de Python
FROM python:3.11-slim

# Instalar uv - el instalador de paquetes ultrarrápido
RUN pip install --no-cache-dir uv

# Establece el directorio de trabajo
WORKDIR /app

# Copia SOLO los archivos de dependencias primero (mejor cache)
COPY requirements.txt pyproject.toml uv.lock* ./

# Instala las dependencias con uv (mucho más rápido)
RUN uv pip install --system --no-cache -r requirements.txt

# Copia el resto del código DESPUÉS de instalar dependencias
# Esto permite que Docker use cache si solo cambia el código
COPY . /app

# Expone el puerto que la aplicación utilizará
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "run.py"]