// Sistema de Atendimento HUBGEO - JavaScript Principal
// Desenvolvido para integração com Flask/Bootstrap

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initializeTooltips();
    initializeAlerts();
    initializeCharts();
    initializeFormValidation();
    initializeSearch();

    console.log('Sistema HUBGEO carregado com sucesso!');
});

// Inicializar tooltips do Bootstrap
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Auto-dismiss de alertas após 5 segundos
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
}

// Inicializar gráficos (usado no dashboard)
function initializeCharts() {
    // Configurações globais do Chart.js
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#6c757d';

        // Tema das cores
        Chart.defaults.backgroundColor = 'rgba(20, 143, 66, 0.1)';
        Chart.defaults.borderColor = '#148f42';
    }
}

// Validação de formulários
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');

    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Sistema de busca
function initializeSearch() {
    const searchInputs = document.querySelectorAll('[data-search]');

    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const targetSelector = this.dataset.search;
            const targets = document.querySelectorAll(targetSelector);

            targets.forEach(function(target) {
                const text = target.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    target.style.display = '';
                } else {
                    target.style.display = 'none';
                }
            });
        });
    });
}

// Utilidades para formatação
const Utils = {
    // Formatar telefone brasileiro
    formatPhone: function(phone) {
        if (!phone) return '';
        const numbers = phone.replace(/\D/g, '');
        if (numbers.length === 11) {
            return numbers.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
        } else if (numbers.length === 10) {
            return numbers.replace(/^(\d{2})(\d{4})(\d{4})$/, '($1) $2-$3');
        }
        return phone;
    },

    // Formatar data brasileira
    formatDate: function(date) {
        if (!date) return '';
        return new Date(date).toLocaleDateString('pt-BR');
    },

    // Formatar data e hora brasileira
    formatDateTime: function(datetime) {
        if (!datetime) return '';
        return new Date(datetime).toLocaleString('pt-BR');
    },

    // Validar email
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // Mostrar loading em botão
    showButtonLoading: function(button, loadingText = 'Carregando...') {
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `<i class="bi bi-hourglass-split"></i> ${loadingText}`;
        button.disabled = true;
    },

    // Esconder loading em botão
    hideButtonLoading: function(button) {
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            button.disabled = false;
        }
    },

    // Mostrar notificação toast
    showToast: function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();

        const toastElement = document.createElement('div');
        toastElement.className = `toast align-items-center text-white bg-${type} border-0`;
        toastElement.setAttribute('role', 'alert');
        toastElement.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toastElement);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Remover elemento após esconder
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    },

    // Criar container de toast se não existir
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    },

    // Copiar texto para clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(function() {
                Utils.showToast('Texto copiado para a área de transferência!', 'success');
            });
        } else {
            // Fallback para navegadores mais antigos
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                Utils.showToast('Texto copiado para a área de transferência!', 'success');
            } catch (err) {
                Utils.showToast('Erro ao copiar texto.', 'danger');
            }
            document.body.removeChild(textArea);
        }
    },

    // Debounce para otimizar buscas
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction() {
            const context = this;
            const args = arguments;
            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    }
};

// Sistema de confirmação para ações perigosas
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Máscaras de input comuns
function applyInputMasks() {
    // Máscara de telefone
    const phoneInputs = document.querySelectorAll('[data-mask="phone"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            this.value = Utils.formatPhone(this.value);
        });
    });

    // Máscara de CEP
    const cepInputs = document.querySelectorAll('[data-mask="cep"]');
    cepInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length <= 8) {
                value = value.replace(/^(\d{5})(\d)/, '$1-$2');
                this.value = value;
            }
        });
    });
}

// Aplicar máscaras quando página carrega
document.addEventListener('DOMContentLoaded', applyInputMasks);

// Sistema de auto-save para formulários (opcional)
function enableAutoSave(formSelector, saveEndpoint) {
    const form = document.querySelector(formSelector);
    if (!form) return;

    const inputs = form.querySelectorAll('input, textarea, select');

    inputs.forEach(function(input) {
        input.addEventListener('blur', Utils.debounce(function() {
            // Implementar auto-save se necessário
            console.log('Auto-save triggered for:', input.name);
        }, 1000));
    });
}

// Atualização automática de timestamps relativos
function updateRelativeTime() {
    const timeElements = document.querySelectorAll('[data-time]');

    timeElements.forEach(function(element) {
        const timestamp = new Date(element.dataset.time);
        const now = new Date();
        const diff = now - timestamp;

        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        let relativeTime;
        if (minutes < 1) {
            relativeTime = 'agora mesmo';
        } else if (minutes < 60) {
            relativeTime = `${minutes} minuto${minutes > 1 ? 's' : ''} atrás`;
        } else if (hours < 24) {
            relativeTime = `${hours} hora${hours > 1 ? 's' : ''} atrás`;
        } else {
            relativeTime = `${days} dia${days > 1 ? 's' : ''} atrás`;
        }

        element.textContent = relativeTime;
    });
}

// Atualizar timestamps a cada minuto
setInterval(updateRelativeTime, 60000);

// Interceptar formulários AJAX (se necessário)
function setupAjaxForms() {
    const ajaxForms = document.querySelectorAll('[data-ajax="true"]');

    ajaxForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');

            Utils.showButtonLoading(submitBtn);

            fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                Utils.hideButtonLoading(submitBtn);

                if (data.success) {
                    Utils.showToast(data.message || 'Operação realizada com sucesso!', 'success');
                    if (data.redirect) {
                        setTimeout(() => window.location.href = data.redirect, 1000);
                    }
                } else {
                    Utils.showToast(data.message || 'Erro ao processar solicitação.', 'danger');
                }
            })
            .catch(error => {
                Utils.hideButtonLoading(submitBtn);
                Utils.showToast('Erro de conexão. Tente novamente.', 'danger');
                console.error('Erro:', error);
            });
        });
    });
}

// Verificar conexão de rede
function checkNetworkStatus() {
    window.addEventListener('online', function() {
        Utils.showToast('Conexão reestabelecida!', 'success');
    });

    window.addEventListener('offline', function() {
        Utils.showToast('Sem conexão com a internet.', 'warning');
    });
}

// Inicializar verificação de rede
checkNetworkStatus();

// Sistema de Notificações
const NotificationSystem = {
    init: function() {
        this.loadNotifications();
        this.setupEventListeners();

        // Atualizar notificações a cada 30 segundos
        setInterval(() => this.loadNotifications(), 30000);
    },

    loadNotifications: function() {
        fetch('/api/notificacoes')
            .then(response => response.json())
            .then(data => {
                this.updateNotificationUI(data);
            })
            .catch(error => {
                console.error('Erro ao carregar notificações:', error);
            });
    },

    updateNotificationUI: function(data) {
        const contador = document.getElementById('contadorNotificacoes');
        const lista = document.getElementById('listaNotificacoes');

        if (data.total_nao_lidas > 0) {
            contador.textContent = data.total_nao_lidas;
            contador.style.display = 'block';
        } else {
            contador.style.display = 'none';
        }

        // Limpar lista atual
        lista.innerHTML = '';

        if (data.notificacoes.length === 0) {
            lista.innerHTML = '<li><span class="dropdown-item-text text-muted">Nenhuma notificação</span></li>';
        } else {
            data.notificacoes.forEach(notif => {
                const item = document.createElement('li');
                item.innerHTML = `
                    <a class="dropdown-item notification-item" href="#" onclick="NotificationSystem.markAsRead(${notif.id}, ${notif.atendimento_id})">
                        <div class="d-flex w-100 justify-content-between">
                            <strong class="mb-1">${notif.titulo}</strong>
                            <small>${notif.data_criacao}</small>
                        </div>
                        <p class="mb-1 text-muted">${notif.mensagem}</p>
                        <small class="text-primary">Clique para ver o atendimento</small>
                    </a>
                `;
                lista.appendChild(item);
            });
        }
    },

    markAsRead: function(notificationId, atendimentoId) {
        fetch(`/notificacoes/${notificationId}/marcar-lida`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirecionar para o atendimento
                window.location.href = `/atendimentos/${atendimentoId}`;
            }
        })
        .catch(error => {
            console.error('Erro ao marcar notificação como lida:', error);
        });
    },

    setupEventListeners: function() {
        // Atualizar notificações quando dropdown é aberto
        const dropdown = document.getElementById('notificacoesDropdown');
        if (dropdown) {
            dropdown.addEventListener('click', () => {
                setTimeout(() => this.loadNotifications(), 100);
            });
        }
    }
};

// Inicializar sistema de notificações quando página carrega
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('notificacoesDropdown')) {
        NotificationSystem.init();
    }
});

// Exportar funções úteis globalmente
window.HubGeo = {
    Utils: Utils,
    confirmAction: confirmAction,
    enableAutoSave: enableAutoSave,
    NotificationSystem: NotificationSystem
};