# AI Vice - Assistente de IA Conversacional

Um sistema de chat inteligente com interface web moderna e minimalista, onde usuários podem conversar com uma IA avançada que responde em tempo real, envia arquivos e gerencia múltiplas conversas simultaneamente.

## 🚀 Características

- **Interface Minimalista**: Design fluido e responsivo com foco na experiência do usuário
- **Comunicação em Tempo Real**: WebSocket para mensagens instantâneas
- **IA Avançada**: Integração com modelos de linguagem de última geração (GPT-4.1-mini)
- **Suporte a Arquivos**: Envio e recebimento de documentos, imagens e outros arquivos
- **Multi-usuário**: Suporte para múltiplas conversas simultâneas
- **Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- **Análise Inteligente**: IA analisa arquivos enviados e fornece insights

## 🛠️ Tecnologias

### Backend
- **Flask**: Framework web Python
- **Flask-SocketIO**: Comunicação WebSocket em tempo real
- **OpenAI API**: Integração com modelos de IA (GPT-4.1-mini)
- **SQLite**: Banco de dados para persistência
- **Flask-CORS**: Suporte para Cross-Origin Resource Sharing

### Frontend
- **React**: Biblioteca JavaScript para interface
- **Vite**: Build tool moderna e rápida
- **Socket.IO Client**: Cliente WebSocket
- **Tailwind CSS**: Framework CSS utilitário
- **shadcn/ui**: Componentes de interface modernos
- **Lucide Icons**: Ícones modernos
- **Framer Motion**: Animações fluidas

## 📁 Estrutura do Projeto

```
ai-chat-vice/
├── backend/                 # Servidor Flask
│   └── ai_vice_backend/
│       ├── src/
│       │   ├── models/      # Modelos de dados (Message, ChatSession)
│       │   ├── routes/      # Rotas da API (chat, upload)
│       │   ├── services/    # Serviços (IA, integração Manus)
│       │   └── main.py      # Aplicação principal Flask
│       ├── run_ai_vice.py   # Script principal de execução
│       └── requirements.txt # Dependências Python
├── frontend/               # Aplicação React
│   └── ai-vice-frontend/
│       ├── src/
│       │   ├── components/  # Componentes React
│       │   │   └── ChatInterface.jsx
│       │   ├── App.jsx      # Componente principal
│       │   └── main.jsx     # Entry point
│       └── package.json     # Dependências Node.js
├── docs/                   # Documentação técnica
├── deployment/             # Configurações de deploy
└── .github/workflows/      # GitHub Actions para CI/CD
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- pnpm (recomendado) ou npm
- Chave da API OpenAI

### Backend

1. **Navegar para o diretório do backend:**
   ```bash
   cd backend/ai_vice_backend
   ```

2. **Ativar ambiente virtual:**
   ```bash
   source venv/bin/activate
   ```

3. **Configurar variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Editar .env com sua chave OpenAI
   ```

4. **Executar o servidor:**
   ```bash
   python run_ai_vice.py
   ```

### Frontend

1. **Navegar para o diretório do frontend:**
   ```bash
   cd frontend/ai-vice-frontend
   ```

2. **Instalar dependências:**
   ```bash
   pnpm install
   ```

3. **Executar em modo desenvolvimento:**
   ```bash
   pnpm run dev
   ```

4. **Acessar:** http://localhost:3000

## 🌐 Deploy

O projeto está configurado para deploy automático:

### Frontend - GitHub Pages
- **URL**: https://llucs.github.io/ai-chat-vice
- **Deploy**: Automático via GitHub Actions ao fazer push na branch `main`
- **Configuração**: `.github/workflows/deploy-frontend.yml`

### Backend - Railway
- **Configuração**: Ver `deployment/railway-setup.md`
- **Variáveis necessárias**:
  - `OPENAI_API_KEY`: Sua chave da API OpenAI
  - `SECRET_KEY`: Chave secreta para Flask
  - `CORS_ORIGINS`: https://llucs.github.io

## 🤖 Como Funciona a IA

O AI Vice utiliza uma integração direta com a API OpenAI para processar mensagens:

1. **Recepção**: Mensagens chegam via WebSocket
2. **Processamento**: IA analisa contexto da conversa
3. **Resposta**: Gera resposta contextual usando GPT-4.1-mini
4. **Entrega**: Resposta enviada em tempo real via WebSocket

### Funcionalidades da IA

- **Conversas Contextuais**: Mantém histórico para respostas relevantes
- **Análise de Arquivos**: Processa documentos, códigos e imagens
- **Multi-idioma**: Responde em português brasileiro por padrão
- **Tempo Real**: Respostas instantâneas via WebSocket

## 📊 API Endpoints

### Chat
- `POST /api/chat/sessions` - Criar nova sessão
- `GET /api/chat/sessions/{id}/messages` - Obter mensagens
- `POST /api/chat/sessions/{id}/upload` - Upload de arquivo

### Utilitários
- `GET /api/health` - Health check
- `GET /uploads/{session_id}/{filename}` - Download de arquivo

### WebSocket Events
- `connect` - Conectar à sessão
- `message` - Enviar/receber mensagem
- `analyze_file` - Analisar arquivo

## 🔧 Configuração

### Variáveis de Ambiente

```env
# Backend (.env)
OPENAI_API_KEY=sua_chave_openai
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta
CORS_ORIGINS=https://llucs.github.io,http://localhost:3000
HOST=0.0.0.0
PORT=5000
DEBUG=True
```

### Desenvolvimento Local

1. **Backend**: http://localhost:5000
2. **Frontend**: http://localhost:3000
3. **WebSocket**: ws://localhost:5000

### Produção

1. **Frontend**: https://llucs.github.io/ai-chat-vice
2. **Backend**: https://sua-url.railway.app
3. **WebSocket**: wss://sua-url.railway.app

## 📚 Documentação

- **Documentação Técnica**: [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)
- **Setup Railway**: [deployment/railway-setup.md](deployment/railway-setup.md)
- **API Reference**: Ver documentação técnica

## 🐛 Troubleshooting

### Problemas Comuns

| Problema | Solução |
|----------|---------|
| WebSocket não conecta | Verificar CORS_ORIGINS |
| IA não responde | Verificar OPENAI_API_KEY |
| Upload falha | Verificar permissões de diretório |
| Frontend não carrega | Verificar logs GitHub Actions |

### Debug

1. **Backend**: Verificar logs em `ai_vice.log`
2. **Frontend**: Developer Tools do browser
3. **WebSocket**: Aba Network no DevTools

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Estrutura de Commits

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração

## 📝 Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🎯 Roadmap

- [ ] Suporte a mais tipos de arquivo
- [ ] Integração com mais modelos de IA
- [ ] Sistema de autenticação
- [ ] Temas personalizáveis
- [ ] Exportação de conversas
- [ ] API pública

---

**AI Vice** - Conversas inteligentes, experiência excepcional.

Desenvolvido com ❤️ usando React, Flask e OpenAI.
