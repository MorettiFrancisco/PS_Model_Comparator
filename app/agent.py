import os

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider

# Intentar obtener la API key de diferentes variables de entorno
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GCP_API_KEY", "NONE")


def create_ollama_model(model_name: str) -> OpenAIModel:
    """
    Crea un modelo de Ollama con el nombre especificado

    Args:
        model_name: Nombre del modelo de Ollama (ej: "gemma3:4b")

    Returns:
        OpenAIModel configurado para Ollama
    """
    return OpenAIModel(
        model_name,
        provider=OpenAIProvider(
            base_url="http://ollama:11434/v1", api_key="your-api-key"
        ),
    )


# Modelo por defecto para Ollama
ollama_model = create_ollama_model("gemma3:4b")

# Modelo de Gemini
gemini_model = GoogleModel(
    "gemini-1.5-flash", provider=GoogleProvider(api_key=GOOGLE_API_KEY)
)


image_agent_system_prompt = """
Eres un experto en analizar imagenes.
Tu tarea es extraer y resumir solo el contenido explícito y visible de una sola imagen.

Guías:
- Concéntrate en la idea principal o tema de la imagen.
- Usa un lenguaje claro y factual basado estrictamente en lo que aparece en la imagen.
- NO hagas suposiciones ni agregues conocimiento externo.
- NO especules ni interpretes significados implícitos.
Devuelve solo un resumen bien estructurado del contenido visible de la imagen, **en español**.
"""


class ImagenAgenteAnalizador:
    """
    Agente único para análisis de imágenes que puede usar Gemini o múltiples modelos de Ollama
    """

    def __init__(self):
        self.gemini_model = gemini_model
        self.system_prompt = image_agent_system_prompt
        self._ollama_agents = {}  # Cache de agentes de Ollama
        self._gemini_agent = None  # Cache del agente de Gemini

    def get_ollama_agent(self, model_name: str = "gemma3:4b") -> Agent:
        """
        Obtiene un agente de Ollama con el modelo especificado

        Args:
            model_name: Nombre del modelo de Ollama (ej: "gemma3:4b", "llama3:8b", "mistral:7b")

        Returns:
            Agent configurado con el modelo de Ollama especificado
        """
        if model_name not in self._ollama_agents:
            ollama_model = create_ollama_model(model_name)
            self._ollama_agents[model_name] = Agent(
                ollama_model,
                output_type=str,
                system_prompt=self.system_prompt,
            )
        return self._ollama_agents[model_name]

    def get_gemini_agent(self) -> Agent:
        """
        Obtiene el agente de Gemini

        Returns:
            Agent configurado con Gemini
        """
        if self._gemini_agent is None:
            self._gemini_agent = Agent(
                self.gemini_model,
                output_type=str,
                system_prompt=self.system_prompt,
            )
        return self._gemini_agent

    def get_agent(
        self, provider: str = "gemini", model_name: str | None = None
    ) -> Agent:
        """
        Obtiene el agente configurado según el proveedor y modelo especificado

        Args:
            provider: "gemini" o "ollama"
            model_name: Para Ollama, especifica el modelo (ej: "gemma3:4b", "llama3:8b")
                       Para Gemini, este parámetro se ignora

        Returns:
            Agent configurado con el proveedor y modelo solicitado
        """
        if provider.lower() == "ollama":
            if model_name is None:
                model_name = "gemma3:4b"  # Modelo por defecto
            return self.get_ollama_agent(model_name)
        elif provider.lower() == "gemini":
            return self.get_gemini_agent()
        else:
            raise ValueError("Provider debe ser 'gemini' o 'ollama'")


# Instancia global del agente analizador de imágenes
imagen_agente_analizador = ImagenAgenteAnalizador()

# Agentes individuales para compatibilidad hacia atrás
image_agent_ollama = imagen_agente_analizador.get_ollama_agent("gemma3:4b")
image_agent_gemini = imagen_agente_analizador.get_gemini_agent()
