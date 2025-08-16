<template>
  <div class="app-container">
    <div class="main-card">
      <header class="header">
        <h1>🤖 PS Model Comparator</h1>
        <p>Compara modelos de IA analizando imágenes</p>
      </header>

      <ModelComparator />
    </div>
  </div>
</template>

<script>
import ModelComparator from "./components/ModelComparator.vue";

export default {
  name: "App",
  components: {
    ModelComparator,
  },
};
</script>

<style scoped>
.app-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.main-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  min-height: 600px;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.header p {
  font-size: 1.1rem;
  opacity: 0.9;
}
</style>
