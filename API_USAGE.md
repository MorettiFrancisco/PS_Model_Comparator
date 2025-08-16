# PS Model Comparator API

## Endpoint Principal: `/compare-models`

### Descripción

Compara múltiples modelos de IA (Gemini y Ollama) analizando una imagen.

### Parámetros

1. **image** (file): Archivo de imagen (JPG, PNG, etc.)
2. **models** (string): JSON con configuraciones de modelos

### Ejemplo de configuración de modelos

```json
[
  {
    "provider": "gemini"
  },
  {
    "provider": "ollama",
    "model_name": "gemma3:4b"
  },
  {
    "provider": "ollama",
    "model_name": "qwen2.5vl:7b"
  }
]
```

### Modelos Disponibles

#### Gemini

- **gemini-1.5-flash**: Modelo con capacidades de texto y visión

#### Ollama (configurados en docker-compose.yml)

- **gemma3:4b**: Modelo con capacidades de visión y texto (4B parámetros)
- **qwen2.5vl:7b**: Modelo con capacidades de visión y texto (7B parámetros)

> **Nota**: Los modelos de Ollama se descargan automáticamente al iniciar el contenedor Docker.

### Respuesta

```json
{
  "results": [
    {
      "model_name": "gemini-1.5-flash",
      "provider": "gemini",
      "response": "Análisis de la imagen...",
      "execution_time": 2.34,
      "success": true,
      "error": null
    },
    {
      "model_name": "gemma3:4b",
      "provider": "ollama",
      "response": "Análisis de la imagen...",
      "execution_time": 3.12,
      "success": true,
      "error": null
    }
  ],
  "total_execution_time": 5.46,
  "image_info": {
    "format": "PNG",
    "mode": "RGB",
    "size": [800, 600],
    "width": 800,
    "height": 600
  }
}
```

## Otros Endpoints

### `/available-models` (GET)

Lista todos los modelos disponibles por proveedor.

### `/health` (GET)

Verificación de salud del servicio.

## Ejemplo de uso con curl

```bash
curl -X POST "http://localhost:8000/compare-models" \
  -F "image=@imagen.jpg" \
  -F 'models=[{"provider":"gemini"},{"provider":"ollama","model_name":"gemma3:4b"}]'
```

## Ejemplo de uso con Python

```python
import requests
import json

# Configuración de modelos
models_config = [
    {"provider": "gemini"},
    {"provider": "ollama", "model_name": "gemma3:4b"},
    {"provider": "ollama", "model_name": "qwen2.5vl:7b"}
]

# Hacer la petición
with open("imagen.jpg", "rb") as img_file:
    response = requests.post(
        "http://localhost:8000/compare-models",
        files={"image": img_file},
        data={"models": json.dumps(models_config)}
    )

# Procesar respuesta
if response.status_code == 200:
    results = response.json()
    for result in results["results"]:
        print(f"Modelo: {result['model_name']}")
        print(f"Tiempo: {result['execution_time']:.2f}s")
        print(f"Respuesta: {result['response'][:100]}...")
        print("-" * 50)
else:
    print(f"Error: {response.status_code} - {response.text}")
```
