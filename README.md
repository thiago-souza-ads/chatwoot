# Plataforma SaaS Multicanal - Documentação de Execução

## Visão Geral

Esta documentação fornece instruções para configuração, execução e deploy da Plataforma SaaS Multicanal, uma solução completa para comunicação empresarial com CRM integrado, suporte a múltiplos canais (WhatsApp via Evolution API) e gestão multiempresa.

## Estrutura do Projeto

```
saas_platform/
├── backend/               # API FastAPI
│   ├── app/               # Código principal
│   │   ├── api/           # Endpoints da API
│   │   ├── core/          # Configurações e segurança
│   │   ├── crud/          # Operações de banco de dados
│   │   ├── db/            # Configuração do banco de dados
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── schemas/       # Schemas Pydantic
│   │   └── services/      # Serviços (WebSocket, etc.)
│   ├── .env               # Variáveis de ambiente
│   └── requirements.txt   # Dependências Python
└── frontend/              # Aplicação React
    ├── public/            # Arquivos estáticos
    ├── src/               # Código fonte
    │   ├── components/    # Componentes React
    │   ├── contexts/      # Contextos (Auth, etc.)
    │   ├── hooks/         # Hooks personalizados
    │   ├── pages/         # Páginas da aplicação
    │   └── services/      # Serviços de API
    └── package.json       # Dependências JavaScript
```

## Requisitos

### Backend
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+

### Frontend
- Node.js 16+
- npm 8+ ou yarn 1.22+

## Configuração do Ambiente

### Backend

1. **Configurar variáveis de ambiente**

   Copie o arquivo `.env.example` para `.env` e configure as variáveis:

   ```
   # Banco de dados
   DATABASE_URL=mysql+pymysql://user:password@localhost:3306/saas_platform
   
   # Segurança
   SECRET_KEY=sua_chave_secreta_aqui
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   
   # Configurações da aplicação
   PROJECT_NAME=SaaS Multicanal
   BACKEND_CORS_ORIGINS=["http://localhost:3000"]
   ```

2. **Criar ambiente virtual e instalar dependências**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Inicializar o banco de dados**

   ```bash
   python initial_data.py
   ```

### Frontend

1. **Instalar dependências**

   ```bash
   cd frontend
   npm install  # ou yarn install
   ```

2. **Configurar variáveis de ambiente**

   Crie um arquivo `.env` na raiz do frontend:

   ```
   REACT_APP_API_URL=http://localhost:8000/api/v1
   ```

## Execução Local

### Backend

```bash
cd backend
source venv/bin/activate  # No Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm start  # ou yarn start
```

Acesse a aplicação em `http://localhost:3000`

## Deploy em Produção

### Backend

1. **Containerização com Docker**

   ```dockerfile
   # Dockerfile para o backend
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Kubernetes (exemplo básico)**

   ```yaml
   # backend-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: saas-backend
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: saas-backend
     template:
       metadata:
         labels:
           app: saas-backend
       spec:
         containers:
         - name: saas-backend
           image: saas-backend:latest
           ports:
           - containerPort: 8000
           env:
           - name: DATABASE_URL
             valueFrom:
               secretKeyRef:
                 name: saas-secrets
                 key: database-url
           - name: SECRET_KEY
             valueFrom:
               secretKeyRef:
                 name: saas-secrets
                 key: secret-key
   ```

### Frontend

1. **Build de produção**

   ```bash
   cd frontend
   npm run build  # ou yarn build
   ```

2. **Servir com Nginx**

   ```dockerfile
   # Dockerfile para o frontend
   FROM nginx:alpine
   
   COPY build/ /usr/share/nginx/html
   COPY nginx.conf /etc/nginx/conf.d/default.conf
   
   EXPOSE 80
   
   CMD ["nginx", "-g", "daemon off;"]
   ```

3. **Kubernetes (exemplo básico)**

   ```yaml
   # frontend-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: saas-frontend
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: saas-frontend
     template:
       metadata:
         labels:
           app: saas-frontend
       spec:
         containers:
         - name: saas-frontend
           image: saas-frontend:latest
           ports:
           - containerPort: 80
   ```

## Observabilidade

A plataforma inclui configurações básicas de observabilidade:

- **Logs**: Logs estruturados em JSON via FastAPI
- **Health Checks**: Endpoint `/health` para verificação de status
- **Métricas**: Integração com Prometheus (pós-MVP)

## Segurança

- Autenticação via JWT
- Isolamento de dados por empresa_id
- HTTPS obrigatório em produção
- Rate limiting por IP, token e empresa_id

## Suporte e Contato

Para suporte técnico ou dúvidas sobre a plataforma, entre em contato com a equipe de desenvolvimento.

---

**Nota**: Esta documentação é um guia inicial. Consulte a documentação de arquitetura completa para detalhes sobre o design e funcionalidades da plataforma.
