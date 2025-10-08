# Deploy do Backend no Railway

Este guia explica como fazer o deploy do backend AI Vice no Railway.

## Pré-requisitos

1. Conta no [Railway](https://railway.app)
2. Repositório GitHub configurado
3. Chave da API OpenAI

## Passos para Deploy

### 1. Conectar Repositório

1. Acesse [Railway](https://railway.app) e faça login
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha o repositório `ai-chat-vice`

### 2. Configurar Variáveis de Ambiente

No painel do Railway, vá para a aba "Variables" e adicione:

```env
OPENAI_API_KEY=sua_chave_openai_aqui
FLASK_ENV=production
SECRET_KEY=sua_chave_secreta_aqui
CORS_ORIGINS=https://llucs.github.io
HOST=0.0.0.0
PORT=5000
DEBUG=False
```

### 3. Configurar Build

1. Na aba "Settings", configure:
   - **Root Directory**: `backend/ai_vice_backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run_ai_vice.py`

### 4. Deploy

1. Clique em "Deploy"
2. Aguarde o build completar
3. Anote a URL gerada (ex: `https://ai-vice-backend.railway.app`)

### 5. Atualizar Frontend

Após o deploy, atualize a URL do backend no arquivo `frontend/ai-vice-frontend/src/components/ChatInterface.jsx`:

```javascript
const BACKEND_URL = process.env.NODE_ENV === 'production' 
  ? 'https://sua-url-railway.railway.app' // Substitua pela URL real
  : 'http://localhost:5000'
```

## Verificação

1. Acesse a URL do Railway
2. Verifique se retorna: "Backend API está funcionando!"
3. Teste a rota de health: `https://sua-url.railway.app/api/health`

## Logs

Para visualizar logs em tempo real:
1. No painel Railway, vá para "Deployments"
2. Clique no deployment ativo
3. Visualize os logs na aba "Logs"

## Troubleshooting

### Erro de Build
- Verifique se o `requirements.txt` está atualizado
- Confirme se o Root Directory está correto

### Erro de Conexão
- Verifique as variáveis de ambiente
- Confirme se a chave OpenAI é válida
- Verifique se o CORS está configurado corretamente

### WebSocket não funciona
- Confirme se o Railway suporta WebSocket (suporta por padrão)
- Verifique se a URL no frontend está correta
- Teste a conexão diretamente via browser developer tools
