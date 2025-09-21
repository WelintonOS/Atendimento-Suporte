# Sistema de Atendimento HUBGEO

Sistema completo de gestão de atendimentos para HUBGEO Equipamentos Topográficos, desenvolvido com Flask e Bootstrap.

## 📋 Funcionalidades

### 🔐 Sistema de Autenticação
- Login seguro com hash de senhas
- Controle de acesso por roles (Admin/Atendente)
- Sessões gerenciadas com Flask-Login

### 👥 Gestão de Usuários
- Criação e gerenciamento de usuários
- Diferentes níveis de acesso
- Ativação/desativação de contas

### 📞 Sistema de Atendimentos
- Registro completo de atendimentos
- Controle de tempo automático (início/fim)
- Suporte aos produtos: Emlid, Geomax, Posição, GTOPO
- Diferentes formas de contato: Email, WhatsApp, Presencial
- Histórico completo com logs de ações

### 📊 Dashboard e Relatórios
- Estatísticas em tempo real
- Gráficos interativos com Chart.js
- Métricas de atendimentos por produto
- Análise temporal de atendimentos

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask 2.3.3** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **Flask-Login** - Gerenciamento de sessões
- **PyMySQL** - Conector MySQL
- **Werkzeug** - Utilitários web

### Frontend
- **Bootstrap 5.3** - Framework CSS
- **Chart.js** - Gráficos interativos
- **Bootstrap Icons** - Ícones
- **JavaScript ES6** - Interatividade

### Banco de Dados
- **MySQL** - Banco principal hospedado na Railway

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Acesso ao banco MySQL (já configurado)

### Passo a Passo

1. **Clone ou extraia o projeto**
```bash
cd Atendimento-Suporte
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação**
```bash
python app.py
```

4. **Acesse o sistema**
- URL: http://localhost:5000
- Login padrão: admin@hubgeo.com
- Senha padrão: admin123

## 📁 Estrutura do Projeto

```
Atendimento-Suporte/
├── app.py                 # Aplicação principal Flask
├── models.py             # Modelos do banco de dados
├── auth.py               # Sistema de autenticação
├── requirements.txt      # Dependências Python
├── LogoHUB.png          # Logo da empresa
├── static/
│   ├── css/
│   │   └── style.css    # Estilos customizados
│   └── js/
│       └── main.js      # JavaScript principal
└── templates/
    ├── base.html        # Template base
    ├── login.html       # Tela de login
    ├── dashboard.html   # Dashboard principal
    ├── atendimentos.html # Lista de atendimentos
    ├── novo_atendimento.html # Criar atendimento
    ├── detalhes_atendimento.html # Detalhes do atendimento
    └── usuarios.html    # Gerenciar usuários
```

## 💾 Banco de Dados

### Tabelas Principais

#### usuarios
- Armazena informações dos usuários do sistema
- Controle de acesso e autenticação

#### atendimentos
- Registro completo dos atendimentos
- Relacionamento com usuários responsáveis
- Controle de tempo e status

#### logs_atendimento
- Histórico de ações nos atendimentos
- Auditoria completa do sistema

### Configuração do Banco
O sistema está configurado para usar o banco MySQL hospedado na Railway:
```
mysql://root:sIuTpZxKilayoTVOrFDnkOOqhYjAeoCe@ballast.proxy.rlwy.net:20008/railway
```

## 🎨 Design e Interface

### Cores da Empresa
- **Verde Principal**: #148f42
- **Preto**: #030303
- **Verde Hover**: #0f7235

### Características do Design
- Interface moderna e intuitiva
- Totalmente responsiva (mobile-first)
- Tema customizado com cores da HUBGEO
- Animações sutis e feedback visual
- Ícones consistentes do Bootstrap Icons

## 👤 Perfis de Usuário

### Administrador
- Acesso completo ao sistema
- Gestão de usuários
- Visualização de todos os atendimentos
- Acesso a todas as funcionalidades

### Atendente
- Criação e gestão de atendimentos
- Visualização do dashboard
- Acesso limitado às funcionalidades

## 📱 Funcionalidades Especiais

### Dashboard em Tempo Real
- Estatísticas atualizadas automaticamente
- Gráficos interativos
- Métricas de performance

### Sistema de Logs
- Auditoria completa de ações
- Histórico detalhado por atendimento
- Controle de tempo preciso

### Interface Responsiva
- Funciona em desktop, tablet e mobile
- Design otimizado para diferentes telas
- Navegação intuitiva

## 🔧 Configurações Avançadas

### Personalização
Para personalizar o sistema:

1. **Cores**: Edite as variáveis CSS em `static/css/style.css`
2. **Logo**: Substitua `LogoHUB.png` pela nova imagem
3. **Produtos**: Modifique as opções nos templates HTML

### Backup
O banco de dados MySQL na Railway possui backup automático. Para backup local:
```bash
# Use ferramentas como mysqldump ou interfaces gráficas
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de conexão com banco**
   - Verifique se tem acesso à internet
   - Confirme as credenciais do banco

2. **Erro de dependências**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Problemas de CSS/JS**
   - Limpe o cache do navegador
   - Verifique se os arquivos static estão sendo servidos

## 📞 Suporte

Para suporte técnico:
- Desenvolvido para HUBGEO Equipamentos Topográficos
- 30 anos de experiência no mercado
- Sistema customizado para as necessidades da empresa

## 🔒 Segurança

### Implementado
- Hash seguro de senhas com Werkzeug
- Validação de entrada de dados
- Controle de acesso baseado em roles
- Proteção contra SQL injection (SQLAlchemy)

### Recomendações
- Altere a SECRET_KEY em produção
- Use HTTPS em ambiente de produção
- Faça backups regulares
- Mantenha as dependências atualizadas

## 📈 Próximas Funcionalidades

Funcionalidades que podem ser implementadas:
- Notificações por email
- Integração com WhatsApp Business
- Relatórios em PDF
- API REST para integrações
- Sistema de tickets avançado

---

**HUBGEO Equipamentos Topográficos**
*30 Anos de Experiência*

Sistema desenvolvido com Flask, Bootstrap e MySQL para gestão completa de atendimentos.