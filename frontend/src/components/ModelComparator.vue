<template>
  <div class="model-comparator">
    <!-- Sección de carga de imagen -->
    <div class="upload-section">
      <h2>📷 Cargar Imagen</h2>
      <div
        class="upload-area"
        :class="{ 'drag-over': isDragOver }"
        @drop="handleDrop"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
      >
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          @change="handleFileSelect"
          style="display: none"
        />

        <div
          v-if="!selectedImage"
          class="upload-placeholder"
          @click="$refs.fileInput.click()"
        >
          <div class="upload-icon">📁</div>
          <p>Haz clic o arrastra una imagen aquí</p>
          <p class="upload-hint">Formatos soportados: JPG, PNG, GIF</p>
        </div>

        <div v-else class="image-preview">
          <img :src="imagePreview" alt="Imagen seleccionada" />
          <button @click="removeImage" class="remove-btn">✕</button>
        </div>
      </div>
    </div>

    <!-- Sección de selección de modelos -->
    <div class="models-section">
      <h2>🤖 Seleccionar Modelos</h2>
      <div class="models-grid">
        <div
          class="model-selector"
          v-for="(model, index) in selectedModels"
          :key="index"
        >
          <div class="model-header">
            <span>Modelo {{ index + 1 }}</span>
            <button
              v-if="selectedModels.length > 2"
              @click="removeModel(index)"
              class="remove-model-btn"
            >
              ✕
            </button>
          </div>

          <div class="provider-selector">
            <label>Proveedor:</label>
            <select v-model="model.provider" @change="onProviderChange(index)">
              <option value="">Seleccionar proveedor</option>
              <option
                v-for="provider in availableProviders"
                :key="provider"
                :value="provider"
              >
                {{ getProviderDisplayName(provider) }}
              </option>
            </select>
          </div>

          <div class="model-selector-dropdown" v-if="model.provider">
            <label>Modelo:</label>
            <select v-model="model.model_name">
              <option value="">Seleccionar modelo</option>
              <option
                v-for="modelName in getModelsForProvider(model.provider)"
                :key="modelName"
                :value="modelName"
              >
                {{ modelName }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <button
        @click="addModel"
        class="add-model-btn"
        :disabled="selectedModels.length >= 5"
      >
        + Agregar Modelo
      </button>
    </div>

    <!-- Botón de comparación -->
    <div class="compare-section">
      <button
        @click="compareModels"
        :disabled="!canCompare"
        :class="{ loading: isLoading }"
        class="compare-btn"
      >
        <span v-if="!isLoading">🚀 Comparar Modelos</span>
        <span v-else>⏳ Procesando...</span>
      </button>
    </div>

    <!-- Resultados -->
    <div v-if="results" class="results-section">
      <h2>📊 Resultados</h2>

      <!-- Métricas de comparación -->
      <div v-if="results.summary" class="comparison-summary">
        <div class="winner-announcement">
          <h3>🏆 Ganador: {{ results.summary.winner }}</h3>
          <p class="recommendation">
            {{ results.summary.recommendation }}
          </p>
        </div>

        <div class="metrics-grid">
          <div class="metric-card">
            <span class="metric-icon">⚡</span>
            <div>
              <h4>Más Rápido</h4>
              <p>{{ results.summary.fastest_model }}</p>
            </div>
          </div>

          <div class="metric-card">
            <span class="metric-icon">📝</span>
            <div>
              <h4>Más Detallado</h4>
              <p>{{ results.summary.most_detailed_model }}</p>
            </div>
          </div>

          <div class="metric-card">
            <span class="metric-icon">⭐</span>
            <div>
              <h4>Mayor Calidad</h4>
              <p>{{ results.summary.highest_quality_model }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="results-grid">
        <div
          v-for="result in results.results"
          :key="result.model_name"
          class="result-card"
        >
          <div class="result-header">
            <h3>{{ result.model_name }}</h3>
            <span class="provider-badge">{{ result.provider }}</span>
            <span class="time-badge"
              >{{ result.execution_time.toFixed(2) }}s</span
            >
            <span
              v-if="getModelMetrics(result.model_name)"
              class="score-badge"
              :class="
                getScoreClass(getModelMetrics(result.model_name).overall_score)
              "
            >
              {{
                getModelMetrics(result.model_name).overall_score.toFixed(1)
              }}/10
            </span>
          </div>

          <!-- Métricas del modelo -->
          <div v-if="getModelMetrics(result.model_name)" class="model-metrics">
            <div class="metrics-row">
              <span
                class="metric-item"
                :class="{
                  active: getModelMetrics(result.model_name).uses_english,
                }"
              >
                🇺🇸 English
              </span>
              <span
                class="metric-item"
                :class="{
                  active: getModelMetrics(result.model_name).well_structured,
                }"
              >
                📋 Estructurado
              </span>
              <span
                class="metric-item"
                :class="{
                  active: getModelMetrics(result.model_name)
                    .has_detailed_description,
                }"
              >
                📖 Detallado
              </span>
            </div>
            <div class="metrics-stats">
              <span class="stat"
                >{{
                  getModelMetrics(result.model_name).word_count
                }}
                palabras</span
              >
              <span class="stat"
                >Calidad:
                {{
                  getModelMetrics(result.model_name).quality_score.toFixed(1)
                }}/10</span
              >
            </div>

            <!-- Métricas Multimodales -->
            <div class="multimodal-metrics">
              <h4 class="metrics-title">🔍 Análisis Multimodal</h4>
              <div class="multimodal-grid">
                <div class="multimodal-metric">
                  <span class="metric-label">ITM Score:</span>
                  <span
                    class="metric-value"
                    :class="
                      getItmScoreClass(
                        getModelMetrics(result.model_name).itm_score
                      )
                    "
                  >
                    {{
                      getModelMetrics(result.model_name).itm_score.toFixed(3)
                    }}
                  </span>
                </div>
              </div>

              <!-- Solo ITM Score para multimodal -->
              <div class="multimodal-metric">
                <div class="metric-header">
                  <span class="metric-label">🔗 ITM Score</span>
                  <span class="metric-description">Image-Text Matching</span>
                </div>
                <div class="metric-details">
                  <span class="metric-value detailed">
                    {{
                      getModelMetrics(result.model_name).itm_score.toFixed(3)
                    }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="result-content">
            <div v-if="result.success" class="success-result">
              <p>{{ result.response }}</p>
            </div>
            <div v-else class="error-result">
              <p>❌ Error: {{ result.error }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="summary">
        <p>
          <strong>Tiempo total:</strong>
          {{ results.total_execution_time.toFixed(2) }} segundos
        </p>
        <p>
          <strong>Imagen:</strong> {{ results.image_info.format }} -
          {{ results.image_info.width }}x{{ results.image_info.height }} px
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ModelComparator",
  data() {
    return {
      selectedImage: null,
      imagePreview: null,
      isDragOver: false,
      selectedModels: [
        { provider: "", model_name: "" },
        { provider: "", model_name: "" },
      ],
      availableModels: {},
      availableProviders: [],
      isLoading: false,
      results: null,
    };
  },
  computed: {
    canCompare() {
      return (
        this.selectedImage &&
        this.selectedModels.length >= 2 &&
        this.selectedModels.every(
          (model) =>
            model.provider && (model.provider === "gemini" || model.model_name)
        )
      );
    },
  },
  async mounted() {
    await this.loadAvailableModels();
  },
  methods: {
    async loadAvailableModels() {
      try {
        const response = await axios.get("/api/available-models");
        this.availableModels = response.data;
        this.availableProviders = Object.keys(this.availableModels);
      } catch (error) {
        console.error("Error cargando modelos:", error);
        alert("Error al cargar los modelos disponibles");
      }
    },

    getProviderDisplayName(provider) {
      const names = {
        gemini: "🧠 Gemini (Google)",
        ollama: "🦙 Ollama (Local)",
      };
      return names[provider] || provider;
    },

    getModelsForProvider(provider) {
      return this.availableModels[provider]?.models || [];
    },

    onProviderChange(index) {
      // Limpiar modelo seleccionado cuando cambia el proveedor
      this.selectedModels[index].model_name = "";
    },

    addModel() {
      if (this.selectedModels.length < 5) {
        this.selectedModels.push({ provider: "", model_name: "" });
      }
    },

    removeModel(index) {
      if (this.selectedModels.length > 2) {
        this.selectedModels.splice(index, 1);
      }
    },

    handleDragOver(e) {
      e.preventDefault();
      this.isDragOver = true;
    },

    handleDragLeave(e) {
      e.preventDefault();
      this.isDragOver = false;
    },

    handleDrop(e) {
      e.preventDefault();
      this.isDragOver = false;
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.processFile(files[0]);
      }
    },

    handleFileSelect(e) {
      const file = e.target.files[0];
      if (file) {
        this.processFile(file);
      }
    },

    processFile(file) {
      if (!file.type.startsWith("image/")) {
        alert("Por favor selecciona un archivo de imagen válido");
        return;
      }

      this.selectedImage = file;

      // Crear preview
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
    },

    removeImage() {
      this.selectedImage = null;
      this.imagePreview = null;
      this.results = null;
      this.$refs.fileInput.value = "";
    },

    getModelMetrics(modelName) {
      if (!this.results?.summary?.metrics_summary) return null;
      return this.results.summary.metrics_summary.find(
        (m) => m.model_name === modelName
      );
    },

    getScoreClass(score) {
      if (score >= 8) return "score-excellent";
      if (score >= 6) return "score-good";
      if (score >= 4) return "score-fair";
      return "score-poor";
    },

    getItmScoreClass(score) {
      // ITM score es una probabilidad (0-1), donde valores más altos indican mejor matching
      if (score >= 0.8) return "score-excellent";
      if (score >= 0.6) return "score-good";
      if (score >= 0.4) return "score-fair";
      return "score-poor";
    },

    async compareModels() {
      if (!this.canCompare) return;

      this.isLoading = true;
      this.results = null;

      try {
        const formData = new FormData();
        formData.append("image", this.selectedImage);

        // Preparar configuración de modelos como JSON (formato original)
        const modelsConfig = this.selectedModels
          .filter(
            (model) =>
              model.provider &&
              (model.provider === "gemini" || model.model_name)
          )
          .map((model) => {
            if (model.provider === "gemini") {
              return { provider: "gemini" }; // Gemini no necesita model_name
            } else {
              return {
                provider: model.provider,
                model_name: model.model_name,
              };
            }
          });

        formData.append("models", JSON.stringify(modelsConfig));

        const response = await axios.post("/api/compare-models", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        this.results = response.data;
      } catch (error) {
        console.error("Error en comparación:", error);
        if (error.response) {
          alert(`Error: ${error.response.data.detail || "Error del servidor"}`);
        } else {
          alert(
            "Error de conexión. Asegúrate de que el servidor esté funcionando."
          );
        }
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>
.model-comparator {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.upload-section,
.models-section,
.compare-section,
.results-section {
  margin-bottom: 2rem;
}

h2 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.upload-area {
  border: 3px dashed #ddd;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.upload-area.drag-over {
  border-color: #667eea;
  background-color: #f8f9ff;
}

.upload-placeholder {
  color: #666;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-hint {
  font-size: 0.9rem;
  color: #999;
}

.image-preview {
  position: relative;
  display: inline-block;
}

.image-preview img {
  max-width: 300px;
  max-height: 200px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.remove-btn,
.remove-model-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 12px;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.model-selector {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
  border: 2px solid #e9ecef;
  position: relative;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-weight: bold;
  color: #495057;
}

.provider-selector,
.model-selector-dropdown {
  margin-bottom: 1rem;
}

.provider-selector label,
.model-selector-dropdown label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  background: white;
}

.add-model-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.add-model-btn:hover:not(:disabled) {
  background: #218838;
}

.add-model-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.compare-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 10px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
  display: block;
}

.compare-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.compare-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
}

.compare-btn.loading {
  background: #ffc107;
  color: #212529;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.result-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.result-header h3 {
  margin: 0;
  color: #333;
  flex: 1;
}

.provider-badge {
  background: #667eea;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.time-badge {
  background: #28a745;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.success-result p {
  color: #333;
  line-height: 1.6;
  margin: 0;
}

.error-result p {
  color: #dc3545;
  margin: 0;
}

.summary {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.summary p {
  margin: 0.5rem 0;
  color: #495057;
}

/* Estilos para métricas */
.comparison-summary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 15px;
  margin-bottom: 2rem;
}

.winner-announcement {
  text-align: center;
  margin-bottom: 2rem;
}

.winner-announcement h3 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
}

.recommendation {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metric-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.metric-icon {
  font-size: 2rem;
}

.metric-card h4 {
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

.metric-card p {
  margin: 0;
  font-weight: bold;
  font-size: 1rem;
}

.score-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.score-excellent {
  background: #28a745;
  color: white;
}

.score-good {
  background: #17a2b8;
  color: white;
}

.score-fair {
  background: #ffc107;
  color: #212529;
}

.score-poor {
  background: #dc3545;
  color: white;
}

.model-metrics {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.metrics-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.metric-item {
  background: #e9ecef;
  color: #6c757d;
  padding: 0.25rem 0.5rem;
  border-radius: 15px;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.metric-item.active {
  background: #28a745;
  color: white;
}

.metrics-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.stat {
  font-weight: 500;
}

/* Estilos para métricas multimodales */
.multimodal-metrics {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #6c5ce7;
}

.metrics-title {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  color: #6c5ce7;
  font-weight: 600;
}

.multimodal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.multimodal-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.metric-label {
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 500;
}

.metric-value {
  font-weight: 600;
  font-size: 0.85rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.metric-value.score-excellent {
  background: #d4edda;
  color: #155724;
}

.metric-value.score-good {
  background: #cce7ff;
  color: #004085;
}

.metric-value.score-fair {
  background: #fff3cd;
  color: #856404;
}

.metric-value.score-poor {
  background: #f8d7da;
  color: #721c24;
}
</style>
