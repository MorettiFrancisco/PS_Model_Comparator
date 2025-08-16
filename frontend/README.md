# Frontend - Model Comparator

Frontend desarrollado en Vue.js 3 para comparar modelos de IA.

## Características

- 🖼️ **Carga de imágenes**: Drag & drop o selección manual
- 🤖 **Selección de modelos**: Soporte para Gemini y Ollama
- ⚡ **Comparación en tiempo real**: Ejecuta múltiples modelos simultáneamente
- 📊 **Resultados detallados**: Muestra respuestas y métricas de rendimiento
- 🎨 **Interfaz moderna**: Diseño responsive y atractivo

## Requisitos

- Node.js 16+
- Backend de Model Comparator ejecutándose en puerto 8000

## Instalación

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## Producción

```bash
npm run build
npm run preview
```

## Uso

1. **Cargar imagen**: Arrastra una imagen o haz clic en el área de carga
2. **Seleccionar modelos**: Elige al menos 2 modelos (Gemini u Ollama)
3. **Comparar**: Haz clic en "Comparar Modelos" y espera los resultados
4. **Ver resultados**: Revisa las respuestas y métricas de cada modelo

## API Backend

El frontend se conecta automáticamente al backend en `http://localhost:8000/api`

Endpoints utilizados:

- `GET /available-models`: Lista de modelos disponibles
- `POST /compare-models`: Comparación de modelos con imagen
