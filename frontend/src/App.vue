<script setup>
import { ref } from 'vue'
import Swal from 'sweetalert2' // Importamos la librería

const file = ref(null)
const isConverting = ref(false)

const handleFileUpload = (event) => {
  file.value = event.target.files[0]
}

const convertFile = async () => {
  // 1. Validación visual
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

  // 2. Alerta de carga (Loading)
  let loadingPopup = Swal.fire({
    title: 'Convirtiendo...',
    text: 'Estamos procesando tu archivo, por favor espera.',
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading()
    }
  })

  const formData = new FormData()
  formData.append('file', file.value)

  try {
    // NOTA: Cambiaremos esta URL en el paso siguiente
    const response = await fetch('http://127.0.0.1:5000/api/convert', { 
      method: 'POST',
      body: formData,
    })

    if (!response.ok) throw new Error('Error en el servidor')

    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    const fileName = file.value.name.replace('.pdf', '.epub')
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    // 3. Alerta de Éxito
    Swal.fire({
      icon: 'success',
      title: '¡Listo!',
      text: 'Tu archivo EPUB se ha descargado correctamente.',
      confirmButtonColor: '#42b883'
    })

  } catch (error) {
    console.error(error)
    // 4. Alerta de Error
    Swal.fire({
      icon: 'error',
      title: 'Oops...',
      text: 'Algo salió mal al convertir el archivo. Intenta de nuevo.',
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
    <p>Convierte tus documentos para leerlos cómodamente.</p>

    <div class="card">
      <input 
        type="file" 
        accept=".pdf" 
        @change="handleFileUpload" 
        class="file-input"
      />
      
      <button 
        @click="convertFile" 
        :disabled="!file || isConverting"
        class="convert-btn"
      >
        {{ isConverting ? 'Procesando...' : 'Convertir a EPUB' }}
      </button>

      <p v-if="statusMessage" :class="{ error: isError, success: !isError }" class="message">
        {{ statusMessage }}
      </p>
    </div>
  </div>
</template>

<style scoped>
/* Tus estilos se quedan igual */
.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
  font-family: sans-serif;
}
.card {
  background: #f9f9f9;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  margin-top: 2rem;
}
.file-input {
  display: block;
  margin: 0 auto 1.5rem;
  padding: 10px;
  border: 1px dashed #ccc;
  width: 100%;
  box-sizing: border-box;
}
.convert-btn {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}
.convert-btn:hover:not(:disabled) {
  background-color: #33a06f;
}
.convert-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.message {
  margin-top: 1rem;
  font-weight: 500;
}
.error { color: #e74c3c; }
.success { color: #2ecc71; }
</style>