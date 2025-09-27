/**
 * MedicoIA Frontend - JavaScript Principal
 * Sistema de diagnóstico médico asistido por IA
 */

class MedicoIA {
    constructor() {
        // Get backend URL from meta tag or use default
        this.apiBase = this.getBackendUrl();
        this.currentConversationId = null;
        this.currentImage = null;
        this.welcomeCleared = false;
        this.init();
    }

    getBackendUrl() {
        // Try to get from meta tag or use default
        const metaBackend = document.querySelector('meta[name="backend-url"]');
        return metaBackend ? metaBackend.getAttribute('content') : 'http://localhost:5000';
    }

    init() {
        this.setupEventListeners();
        this.setupImageUpload();
        this.setupCharacterCounter();
        this.autoResizeTextarea();
        
        // Inicializar primera carga
        setTimeout(() => {
            this.loadHistory();
        }, 1000);
    }

    setupEventListeners() {
        // Chat form
        const chatForm = document.getElementById('chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }

        // Character counter
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('input', this.updateCharacterCount);
            messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // Analyze image button
        const analyzeBtn = document.getElementById('analyze-image-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeImage());
        }
    }

    setupImageUpload() {
        const imageInput = document.getElementById('image-input');
        const dropZone = document.getElementById('image-drop-zone');

        // Click to upload
        dropZone.addEventListener('click', () => imageInput.click());

        // File input change
        imageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) this.handleImageUpload(file);
        });

        // Drag and drop
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-medical-400', 'bg-medical-50');
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-medical-400', 'bg-medical-50');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-medical-400', 'bg-medical-50');
            
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                this.handleImageUpload(file);
            }
        });
    }

    setupCharacterCounter() {
        const messageInput = document.getElementById('message-input');
        const charCount = document.getElementById('char-count');
        
        if (messageInput && charCount) {
            messageInput.addEventListener('input', () => {
                const count = messageInput.value.length;
                charCount.textContent = count;
                
                if (count > 800) {
                    charCount.classList.add('text-warning-600');
                } else if (count > 950) {
                    charCount.classList.add('text-danger-600');
                } else {
                    charCount.classList.remove('text-warning-600', 'text-danger-600');
                }
            });
        }
    }

    autoResizeTextarea() {
        const textarea = document.getElementById('message-input');
        if (textarea) {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
        }
    }


    handleImageUpload(file) {
        // Validar tipo de archivo
        if (!file.type.startsWith('image/')) {
            this.showNotification('Por favor, selecciona un archivo de imagen válido', 'error');
            return;
        }

        // Validar tamaño (10MB)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showNotification('La imagen es demasiado grande. Máximo 10MB.', 'error');
            return;
        }

        // Mostrar preview
        const reader = new FileReader();
        reader.onload = (e) => {
            const dropZoneContent = document.getElementById('drop-zone-content');
            const imagePreview = document.getElementById('image-preview');
            const previewImg = document.getElementById('preview-img');
            const imageName = document.getElementById('image-name');
            const analyzeBtn = document.getElementById('analyze-image-btn');

            previewImg.src = e.target.result;
            imageName.textContent = file.name;
            
            dropZoneContent.classList.add('hidden');
            imagePreview.classList.remove('hidden');
            analyzeBtn.disabled = false;
            
            this.currentImage = file;
            this.showNotification('Imagen cargada correctamente', 'success');
        };

        reader.readAsDataURL(file);
    }

    removeImage() {
        const dropZoneContent = document.getElementById('drop-zone-content');
        const imagePreview = document.getElementById('image-preview');
        const analyzeBtn = document.getElementById('analyze-image-btn');
        const imageInput = document.getElementById('image-input');

        dropZoneContent.classList.remove('hidden');
        imagePreview.classList.add('hidden');
        analyzeBtn.disabled = true;
        imageInput.value = '';
        
        this.currentImage = null;
    }

    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();

        if (!message) {
            this.showNotification('Por favor, escribe un mensaje', 'warning');
            return;
        }

        const sendBtn = document.getElementById('send-btn');
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Procesando...';

        // Limpiar mensaje de bienvenida si existe
        this.clearWelcomeMessage();
        
        // Agregar mensaje del usuario al chat
        this.addMessageToChat('user', message);
        messageInput.value = '';
        this.updateCharacterCount();

        try {
            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.addMessageToChat('assistant', result.diagnosis || result.response, result);

            if (result.conversation_id) {
                this.currentConversationId = result.conversation_id;
            }

        } catch (error) {
            console.error('Error:', error);
            let errorMessage = 'Lo siento, ocurrió un error al procesar tu mensaje.';
            
            if (error.message.includes('Failed to fetch')) {
                errorMessage = '⚠️ No se puede conectar con el backend. Asegúrate de que esté ejecutándose en http://localhost:5000';
            } else if (error.message.includes('HTTP error')) {
                errorMessage = `Error del servidor: ${error.message}`;
            }
            
            this.addMessageToChat('assistant', errorMessage);
            this.showNotification('Error al enviar el mensaje', 'error');
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i>Diagnosticar';
        }
    }

    async analyzeImage() {
        if (!this.currentImage) {
            this.showNotification('Por favor, selecciona una imagen primero', 'warning');
            return;
        }

        const messageInput = document.getElementById('message-input');
        const description = messageInput.value.trim() || 'Analizar imagen médica';
        
        const analyzeBtn = document.getElementById('analyze-image-btn');
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Analizando...';

        this.showLoading(true);

        // Limpiar mensaje de bienvenida si existe
        this.clearWelcomeMessage();
        
        // Agregar mensaje del usuario al chat
        this.addMessageToChat('user', `🖼️ **Imagen médica enviada**\n\n**Descripción:** ${description}`, null, true);
        messageInput.value = '';

        try {
            const formData = new FormData();
            formData.append('image', this.currentImage);
            formData.append('message', description);

            const response = await fetch(`${this.apiBase}/analyze-image`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.addMessageToChat('assistant', result.diagnosis || result.response, result, false, true);

            if (result.conversation_id) {
                this.currentConversationId = result.conversation_id;
            }

            // Limpiar imagen después del análisis
            this.removeImage();

        } catch (error) {
            console.error('Error:', error);
            let errorMessage = 'Lo siento, ocurrió un error al analizar la imagen.';
            
            if (error.message.includes('Failed to fetch')) {
                errorMessage = '⚠️ No se puede conectar con el backend para analizar la imagen. Verifica que esté ejecutándose en http://localhost:5000';
            } else if (error.message.includes('HTTP error')) {
                errorMessage = `Error del servidor al analizar imagen: ${error.message}`;
            }
            
            this.addMessageToChat('assistant', errorMessage);
            this.showNotification('Error al analizar la imagen', 'error');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-microscope mr-2"></i>Analizar Imagen';
            this.showLoading(false);
        }
    }

    addMessageToChat(role, content, fullResponse = null, hasImage = false, isImageAnalysis = false) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        
        const isUser = role === 'user';
        const alignClass = isUser ? 'justify-end' : 'justify-start';
        const bgClass = isUser ? 'bg-medical-500 text-white' : 'bg-white border border-gray-200';
        const roundedClass = isUser ? 'rounded-2xl rounded-br-sm' : 'rounded-2xl rounded-bl-sm';
        const avatar = isUser ? 
            '<div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white"><i class="fas fa-user-md"></i></div>' :
            '<div class="w-10 h-10 bg-medical-500 rounded-full flex items-center justify-center text-white"><i class="fas fa-robot"></i></div>';

        let confidenceHtml = '';
        let recommendationsHtml = '';

        // Generar HTML de confianza si es respuesta del asistente
        if (fullResponse && !isUser && fullResponse.confidence) {
            const confidence = Math.round(fullResponse.confidence * 100);
            const confidenceColor = confidence >= 80 ? 'success' : confidence >= 60 ? 'warning' : 'danger';
            const confidenceIcon = confidence >= 80 ? 'check-circle' : confidence >= 60 ? 'exclamation-triangle' : 'times-circle';
            
            confidenceHtml = `
                <div class="mt-3 p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-700">Nivel de Confianza</span>
                        <div class="flex items-center">
                            <i class="fas fa-${confidenceIcon} text-${confidenceColor}-500 mr-1"></i>
                            <span class="text-sm font-bold text-${confidenceColor}-600">${confidence}%</span>
                        </div>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill bg-${confidenceColor}-500" style="width: ${confidence}%"></div>
                    </div>
                </div>
            `;
        }

        // Generar HTML de recomendaciones
        if (fullResponse && fullResponse.recommendations && fullResponse.recommendations.length > 0) {
            recommendationsHtml = `
                <div class="mt-3 p-3 bg-blue-50 rounded-lg">
                    <h4 class="text-sm font-medium text-blue-900 mb-2">
                        <i class="fas fa-pills mr-2"></i>Recomendaciones:
                    </h4>
                    <ul class="space-y-1">
                        ${fullResponse.recommendations.map(rec => `<li class="text-sm text-blue-800">• ${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Icono especial para análisis de imagen
        const analysisIcon = isImageAnalysis ? '<i class="fas fa-microscope text-medical-500 mr-2"></i>' : '';

        const time = new Date().toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        messageDiv.className = `flex ${alignClass} space-x-3 animate-slide-up`;
        messageDiv.innerHTML = `
            ${!isUser ? avatar : ''}
            <div class="message-bubble ${bgClass} ${roundedClass} p-4 shadow-md max-w-xl">
                <div class="text-sm">
                    ${isUser ? '' : `<div class="font-medium text-medical-600 mb-1">${analysisIcon}Asistente Médico</div>`}
                    <div class="message-content whitespace-pre-wrap">${content}</div>
                    ${confidenceHtml}
                    ${recommendationsHtml}
                    ${!isUser && fullResponse ? `
                        <div class="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <p class="text-xs text-yellow-800">
                                <i class="fas fa-exclamation-triangle mr-1"></i>
                                <strong>Importante:</strong> Este diagnóstico debe ser validado por un profesional médico.
                            </p>
                        </div>
                    ` : ''}
                </div>
                <div class="text-xs ${isUser ? 'text-blue-100' : 'text-gray-500'} mt-2">${time}</div>
            </div>
            ${isUser ? avatar : ''}
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async loadHistory() {
        const historyContent = document.getElementById('history-content');
        
        historyContent.innerHTML = `
            <div class="text-center py-12">
                <div class="text-red-400 text-6xl mb-4">
                    <i class="fas fa-plug"></i>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Backend no conectado</h3>
                <p class="text-gray-600">
                    El historial requiere que el backend esté ejecutándose.<br>
                    Inicia el servidor backend en <code class="bg-gray-100 px-2 py-1 rounded">http://localhost:5000</code>
                </p>
            </div>
        `;
    }


    clearChat() {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = '';
        
        // Restaurar mensaje de bienvenida
        setTimeout(() => {
            chatMessages.innerHTML = `
                <div class="flex items-start space-x-3 animate-fade-in">
                    <div class="flex-shrink-0">
                        <div class="w-10 h-10 bg-medical-500 rounded-full flex items-center justify-center text-white">
                            <i class="fas fa-robot"></i>
                        </div>
                    </div>
                    <div class="message-bubble bg-white rounded-2xl rounded-tl-sm p-4 shadow-md border border-gray-200">
                        <div class="text-sm text-gray-900">
                            <div class="font-medium text-medical-600 mb-2">¡Hola! Soy tu asistente médico inteligente</div>
                            <p>Puedes:</p>
                            <ul class="list-disc list-inside mt-2 space-y-1 text-gray-700">
                                <li><strong>Describir síntomas</strong> del paciente en texto libre</li>
                                <li><strong>Subir imágenes médicas</strong> (rayos X, resonancias, etc.)</li>
                                <li><strong>Consultar el historial</strong> de diagnósticos anteriores</li>
                            </ul>
                            <div class="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                                <p class="text-xs text-yellow-800">
                                    <i class="fas fa-exclamation-triangle mr-1"></i>
                                    <strong>Importante:</strong> Este es un sistema de asistencia que debe ser validado por un profesional médico.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            this.welcomeCleared = false;
        }, 300);
        
        this.currentConversationId = null;
        this.showNotification('Chat limpiado', 'success');
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (show) {
            overlay.classList.remove('hidden');
            overlay.classList.add('flex');
        } else {
            overlay.classList.add('hidden');
            overlay.classList.remove('flex');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const icons = {
            success: 'check-circle',
            error: 'times-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        const colors = {
            success: 'success',
            error: 'danger',
            warning: 'warning',
            info: 'medical'
        };

        notification.className = `fixed top-4 right-4 z-50 bg-white border-l-4 border-${colors[type]}-500 rounded-lg shadow-lg p-4 max-w-sm animate-slide-up`;
        notification.innerHTML = `
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <i class="fas fa-${icons[type]} text-${colors[type]}-500"></i>
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium text-gray-900">${message}</p>
                </div>
                <div class="ml-auto pl-3">
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" 
                            class="text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(notification);

        // Remover automáticamente después de 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    updateCharacterCount() {
        const messageInput = document.getElementById('message-input');
        const charCount = document.getElementById('char-count');
        
        if (messageInput && charCount) {
            charCount.textContent = messageInput.value.length;
        }
    }

    clearWelcomeMessage() {
        const chatMessages = document.getElementById('chat-messages');
        // Buscar cualquier mensaje con la clase específica de bienvenida
        const welcomeMessages = chatMessages.querySelectorAll('.animate-fade-in');
        
        if (welcomeMessages.length > 0 && !this.welcomeCleared) {
            welcomeMessages.forEach(msg => msg.remove());
            this.welcomeCleared = true;
        }
    }
}

// Funciones globales
function showTab(tabName) {
    console.log('Switching to tab:', tabName);
    
    // Ocultar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });
    
    // Remover clase activa de todos los botones y limpiar estilos inline
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.classList.remove('border-white', 'text-white');
        btn.classList.add('border-transparent', 'text-teal-100');
        // Limpiar cualquier estilo inline que pueda interferir
        btn.style.removeProperty('border-bottom-color');
        btn.style.removeProperty('border-bottom-width');
        btn.style.removeProperty('border-bottom-style');
        btn.style.removeProperty('color');
    });
    
    // Mostrar tab seleccionado
    const targetTab = document.getElementById(`${tabName}-tab`);
    if (targetTab) {
        targetTab.classList.remove('hidden');
        console.log('Showing tab:', targetTab);
    } else {
        console.error('Tab not found:', `${tabName}-tab`);
    }
    
    // Activar botón correspondiente
    const activeBtn = document.querySelector(`[onclick="showTab('${tabName}')"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
        activeBtn.classList.remove('border-transparent', 'text-teal-100');
        activeBtn.classList.add('border-white', 'text-white');
        console.log('Activated button:', activeBtn);
    } else {
        console.error('Button not found for tab:', tabName);
    }
    
    // Cargar contenido específico si es necesario
    if (tabName === 'history') {
        medicoia.loadHistory();
    }
}

function clearChat() {
    medicoia.clearChat();
}

function removeImage() {
    medicoia.removeImage();
}

function loadHistory() {
    medicoia.loadHistory();
}

// Inicializar aplicación
const medicoia = new MedicoIA();

// Inicializar el estado correcto de los tabs al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Asegurar que el tab de diagnóstico esté activo por defecto
    showTab('chat');
});