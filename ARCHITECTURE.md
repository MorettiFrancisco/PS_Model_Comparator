# PS Model Comparator - Estructura Modular

## Arquitectura del Proyecto

El proyecto está organizado en módulos especializados para mantener un código limpio y mantenible:

### 📁 Estructura de Archivos

```text
app/
├── __init__.py              # Inicialización del módulo
├── main.py                  # 🚀 API endpoints principales
├── agent.py                 # 🤖 Configuración de agentes IA
├── models.py                # 📋 Modelos Pydantic (esquemas de datos)
├── image_utils.py           # 🖼️ Utilidades de procesamiento de imágenes
├── model_executor.py        # ⚡ Lógica de ejecución de modelos
├── model_config.py          # ⚙️ Configuración y datos de modelos
└── validation.py            # ✅ Validaciones de entrada
```

## 📖 Descripción de Módulos

### `main.py` - Endpoints API

- **Responsabilidad**: Solo contiene los endpoints de FastAPI
- **Funciones**:
  - `POST /compare-models`: Comparación de modelos
  - `GET /available-models`: Lista de modelos disponibles
  - `GET /health`: Verificación de salud

### `models.py` - Esquemas de Datos

- **Responsabilidad**: Definición de modelos Pydantic
- **Clases**:
  - `ModelConfig`: Configuración de modelo
  - `ModelResponse`: Respuesta de un modelo
  - `ComparisonResponse`: Respuesta completa de comparación

### `image_utils.py` - Procesamiento de Imágenes

- **Responsabilidad**: Manejo y procesamiento de imágenes
- **Funciones**:
  - `process_image()`: Procesar imagen y extraer metadata
  - `image_to_base64()`: Convertir imagen a base64
  - `validate_image_file()`: Validar tipo de archivo

### `model_executor.py` - Ejecución de Modelos

- **Responsabilidad**: Lógica de ejecución y comparación
- **Funciones**:
  - `execute_model()`: Ejecutar un modelo específico
  - `get_model_display_name()`: Obtener nombre de visualización
  - `get_model_prompt()`: Generar prompt según capacidades

### `model_config.py` - Configuración de Modelos

- **Responsabilidad**: Información sobre modelos disponibles
- **Funciones**:
  - `get_available_models()`: Lista de modelos disponibles
  - `get_model_capabilities()`: Capacidades de un modelo
  - `has_vision_capability()`: Verificar capacidades de visión

### `validation.py` - Validaciones

- **Responsabilidad**: Validación de entrada y configuración
- **Funciones**:
  - `parse_models_config()`: Parsear configuración JSON
  - `validate_models_for_comparison()`: Validar configuración

### `agent.py` - Agentes IA

- **Responsabilidad**: Configuración y manejo de agentes
- **Clases**:
  - `ImagenAgenteAnalizador`: Agente principal con soporte multi-modelo

## 🔄 Flujo de Datos

```text
HTTP Request → main.py → validation.py → image_utils.py → model_executor.py → agent.py → Response
                ↓
            model_config.py (configuración)
```

## 🎯 Ventajas de esta Estructura

1. **Separación de Responsabilidades**: Cada módulo tiene una función específica
2. **Mantenibilidad**: Fácil localizar y modificar funcionalidades
3. **Testabilidad**: Cada módulo se puede probar independientemente
4. **Reutilización**: Funciones disponibles para otros módulos
5. **Escalabilidad**: Fácil agregar nuevos modelos o funcionalidades

## 🚀 Cómo Agregar Nuevos Modelos

1. **Actualizar `model_config.py`**: Agregar modelo a la lista
2. **Modificar `model_executor.py`**: Agregar lógica específica si es necesario
3. **Actualizar `agent.py`**: Configurar el nuevo agente si es requerido

## 🧪 Testing

Cada módulo puede ser probado independientemente:

```bash
# Probar utilidades de imagen
python -m pytest tests/test_image_utils.py

# Probar ejecución de modelos
python -m pytest tests/test_model_executor.py

# Probar validaciones
python -m pytest tests/test_validation.py
```
