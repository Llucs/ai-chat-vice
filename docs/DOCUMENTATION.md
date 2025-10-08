# AI Vice - Documentação Técnica

## Visão Geral

O **AI Vice** é um sistema de chat conversacional inteligente que permite aos usuários interagir com uma IA avançada em tempo real. O sistema é composto por um frontend React hospedado no GitHub Pages e um backend Flask com WebSocket hospedado no Railway.

## Arquitetura do Sistema

### Componentes Principais

| Componente | Tecnologia | Hospedagem | Função |
|------------|------------|------------|---------|
| Frontend | React + Vite | GitHub Pages | Interface do usuário |
| Backend | Flask + SocketIO | Railway | API e WebSocket |
| Banco de Dados | SQLite | Railway | Persistência de dados |
| IA | OpenAI API | - | Processamento de linguagem |

### Fluxo de Dados

1. **Usuário** envia mensagem através do frontend
2. **Frontend** transmite via WebSocket para o backend
3. **Backend** processa e salva mensagem no banco
4. **Serviço de IA** gera resposta usando OpenAI API
5. **Backend** salva resposta e envia via WebSocket
6. **Frontend** exibe resposta em tempo real

## Estrutura do Projeto

```
ai-chat-vice/
├── backend/
│   └── ai_vice_backend/
│       ├── src/
│       │   ├── models/          # Modelos de dados
│       │   ├── routes/          # Rotas da API
│       │   ├── services/        # Serviços de negócio
│       │   └── main.py          # Aplicação principal
│       ├── run_ai_vice.py       # Script de execução
│       └── requirements.txt     # Dependências Python
├── frontend/
│   └── ai-vice-frontend/
│       ├── src/
│       │   ├── components/      # Componentes React
│       │   └── App.jsx          # Componente principal
│       └── package.json         # Dependências Node.js
├── deployment/                  # Configurações de deploy
├── docs/                        # Documentação
└── .github/workflows/           # GitHub Actions
```

## Funcionalidades

### Chat em Tempo Real

- **WebSocket**: Comunicação bidirecional instantânea
- **Sessões**: Cada usuário tem uma sessão única isolada
- **Histórico**: Mensagens persistidas no banco de dados
- **Multi-usuário**: Suporte para múltiplas conversas simultâneas

### Processamento de IA

- **OpenAI Integration**: Uso do modelo GPT-4.1-mini
- **Contexto**: Mantém histórico da conversa para respostas contextuais
- **Análise de Arquivos**: Capacidade de analisar documentos enviados
- **Respostas Inteligentes**: Processamento avançado de linguagem natural

### Upload de Arquivos

- **Tipos Suportados**: Texto, código, documentos, imagens
- **Análise Automática**: IA analisa conteúdo e fornece insights
- **Armazenamento**: Arquivos salvos no servidor com URLs únicas
- **Download**: Usuários podem baixar arquivos enviados

## API Endpoints

### Sessões

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/chat/sessions` | Criar nova sessão |
| GET | `/api/chat/sessions/{id}/messages` | Obter mensagens |

### Upload

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/chat/sessions/{id}/upload` | Upload de arquivo |
| GET | `/uploads/{session_id}/{filename}` | Download de arquivo |

### Utilitários

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/health` | Health check |

## Eventos WebSocket

### Cliente → Servidor

- `connect`: Conectar à sessão
- `message`: Enviar mensagem
- `analyze_file`: Solicitar análise de arquivo

### Servidor → Cliente

- `connected`: Confirmação de conexão
- `message`: Nova mensagem (usuário ou IA)
- `error`: Erro de processamento

## Modelos de Dados

### Message

```python
{
    "id": "uuid",
    "session_id": "uuid",
    "user_id": "string",
    "content": "string",
    "message_type": "text|file",
    "sender": "user|ai",
    "timestamp": "datetime",
    "file_url": "string",
    "file_name": "string",
    "file_size": "integer"
}
```

### ChatSession

```python
{
    "id": "uuid",
    "user_id": "string",
    "created_at": "datetime",
    "last_activity": "datetime",
    "is_active": "boolean"
}
```

## Configuração de Desenvolvimento

### Backend

```bash
cd backend/ai_vice_backend
source venv/bin/activate
pip install -r requirements.txt
python run_ai_vice.py
```

### Frontend

```bash
cd frontend/ai-vice-frontend
pnpm install
pnpm run dev
```

### Variáveis de Ambiente

```env
OPENAI_API_KEY=sua_chave_aqui
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta
CORS_ORIGINS=http://localhost:3000
HOST=0.0.0.0
PORT=5000
DEBUG=True
```

## Deploy em Produção

### Frontend (GitHub Pages)

1. Push para branch `main`
2. GitHub Actions faz build automático
3. Deploy para `https://llucs.github.io/ai-chat-vice`

### Backend (Railway)

1. Conectar repositório no Railway
2. Configurar variáveis de ambiente
3. Deploy automático a cada push

## Monitoramento

### Logs do Sistema

- **Aplicação**: Logs salvos em `ai_vice.log`
- **Railway**: Logs disponíveis no painel
- **GitHub Actions**: Logs de build/deploy

### Métricas

- Número de sessões ativas
- Total de mensagens processadas
- Tempo de resposta da IA
- Status de conexão WebSocket

## Segurança

### Autenticação

- Sessões baseadas em UUID únicos
- Isolamento entre usuários
- Validação de entrada de dados

### CORS

- Configurado para permitir apenas domínios autorizados
- GitHub Pages e localhost para desenvolvimento

### Rate Limiting

- Implementado no nível da aplicação
- Prevenção de spam e abuso

## Troubleshooting

### Problemas Comuns

| Problema | Causa | Solução |
|----------|-------|---------|
| WebSocket não conecta | CORS mal configurado | Verificar CORS_ORIGINS |
| IA não responde | Chave OpenAI inválida | Verificar OPENAI_API_KEY |
| Upload falha | Permissões de arquivo | Verificar diretório uploads |
| Frontend não carrega | Build falhou | Verificar logs GitHub Actions |

### Debug

1. **Backend**: Verificar logs em `ai_vice.log`
2. **Frontend**: Usar Developer Tools do browser
3. **WebSocket**: Monitorar aba Network no DevTools
4. **API**: Testar endpoints com curl/Postman

## Contribuição

### Estrutura de Commits

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes

### Pull Requests

1. Fork do repositório
2. Branch para feature/fix
3. Commits descritivos
4. Testes passando
5. PR com descrição detalhada

## Licença

MIT License - veja [LICENSE](../LICENSE) para detalhes.
