<script setup>
import { ref } from 'vue'
import Swal from 'sweetalert2'

// Estados de la aplicación
const file = ref(null)
const isConverting = ref(false)
const progress = ref(0)
const fileInputRef = ref(null)

// Metadatos del libro
const bookTitle = ref('')
const bookAuthor = ref('') 

const handleFileUpload = (event) => {
  if (event.target.files && event.target.files[0]) {
    file.value = event.target.files[0]
    // Sugerir el nombre del archivo como título por defecto
    bookTitle.value = file.value.name.replace('.pdf', '')
  }
}

// Limpia todo para una nueva conversión
const resetApp = () => {
  file.value = null
  bookTitle.value = ''
  bookAuthor.value = ''
  progress.value = 0
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// Acción del botón de eliminar (X)
const removeFile = () => {
  resetApp()
}

const convertFile = async () => {
  if (!file.value) {
    Swal.fire({
      icon: 'warning',
      title: '¡Espera!',
      text: 'Necesitas seleccionar un archivo PDF primero.',
      confirmButtonColor: '#42b883'
    })
    return
  }

  isConverting.value = true
  progress.value = 0

  // Simulador de progreso visual
  const interval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += Math.random() * 15 
    }
  }, 500)

  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('title', bookTitle.value || file.value.name.replace('.pdf', ''))
  formData.append('author', bookAuthor.value || 'Anónimo')

  try {
    // URL de tu backend (ajustar si es local o producción)
    const response = await fetch('http://127.0.0.1:5000/api/convert', { 
      method: 'POST',
      body: formData,
    })

    if (!response.ok) throw new Error('Error en el servidor')

    progress.value = 100
    clearInterval(interval)

    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    
    const fileName = (bookTitle.value || 'libro').replace(/\s+/g, '_') + '.epub'
    link.setAttribute('download', fileName)
    
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    Swal.fire({
      icon: 'success',
      title: '¡Convertido!',
      text: 'Tu descarga ha comenzado.',
      timer: 2500,
      showConfirmButton: false
    })

    // Limpiamos la interfaz para el siguiente archivo
    setTimeout(() => {
        resetApp()
    }, 1000)

  } catch (error) {
    clearInterval(interval)
    console.error(error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo procesar el archivo. Revisa tu conexión o el formato del PDF.',
      confirmButtonColor: '#e74c3c'
    })
  } finally {
    isConverting.value = false
  }
}
</script>

<template>
  <div class="container">
    <h1>PDF a EPUB</h1>
    <p class="subtitle">Convierte tus PDFS a EPUB para leer ilegalmente.</p>

    <div class="card">
      <div class="input-group" v-if="!file">
        <input 
          ref="fileInputRef"
          type="file" 
          accept=".pdf" 
          @change="handleFileUpload" 
          class="file-input"
          id="pdf-upload"
        />
        <label for="pdf-upload" class="input-label">
          📂 Seleccionar PDF
        </label>
      </div>
      
      <div v-if="file" class="file-display">
        <div class="file-info">
          <span class="file-icon">📄</span>
          <span class="file-name">{{ file.name }}</span>
        </div>
        <button @click="removeFile" class="remove-btn" title="Eliminar archivo">✕</button>
      </div>

      <div class="metadata-inputs" v-if="file && !isConverting">
        <label class="field-label">Título del libro</label>
        <input v-model="bookTitle" type="text" placeholder="Ej: Don Quijote" class="text-input" />
        
        <label class="field-label">Autor</label>
        <input v-model="bookAuthor" type="text" placeholder="Ej: Miguel de Cervantes" class="text-input" />
      </div>

      <div v-if="isConverting" class="progress-section">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <p class="progress-text">Procesando: {{ Math.round(progress) }}%</p>
      </div>

      <button 
        @click="convertFile" 
        :disabled="!file || isConverting"
        class="convert-btn"
      >
        <span v-if="!isConverting">Convertir Ahora</span>
        <span v-else>Trabajando...</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.h1{
  font-size: 2.5rem;
  font-weight: 700;
  color: #ffffff;
}

.container {
  max-width: 500px;
  margin: 0 auto;
  padding: 3rem 1rem;
  text-align: center;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  color: #ffffff;
}

.subtitle {
  color: #6b7280;
  margin-bottom: 2rem;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.file-input { display: none; }

.input-label {
  display: block;
  padding: 20px;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  cursor: pointer;
  color: #4b5563;
  transition: all 0.2s ease;
  font-weight: 500;
}

.input-label:hover {
  border-color: #42b883;
  background-color: #f0fdf4;
  color: #166534;
}

.file-display {
  background-color: #f9fafb;
  padding: 12px 16px; 
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between; 
  animation: slideDown 0.3s ease;
  border: 1px solid #f3f4f6;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
}

.file-name {
  font-weight: 700;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 220px;
}

.remove-btn {
  background-color: #fee2e2; 
  color: #ef4444;
  border: none;
  width: 28px; height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
}

.remove-btn:hover { background-color: #ef4444; color: white; }

.metadata-inputs {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 8px;
  animation: fadeIn 0.4s ease;
}

.field-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #4b5563;
  margin-left: 4px;
}

.text-input {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  outline: none;
  transition: all 0.2s;
}

.text-input:focus {
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
}

/* Barra de Progreso Estilizada */
.progress-section {
  margin: 10px 0;
}

.progress-bar {
  background-color: #f3f4f6;
  border-radius: 20px;
  height: 10px;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(90deg, #42b883, #10b981);
  height: 100%;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.85rem;
  margin-top: 8px;
  font-weight: 700;
  color: #059669;
}

.convert-btn {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 16px;
  font-size: 1.1rem;
  font-weight: 700;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px -1px rgba(66, 184, 131, 0.4);
}

.convert-btn:hover:not(:disabled) {
  background-color: #34d399;
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(66, 184, 131, 0.3);
}

.convert-btn:disabled {
  background-color: #d1d5db;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
</style>