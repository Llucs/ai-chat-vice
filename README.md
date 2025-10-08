# AI Vice - Assistente de IA Conversacional

Um sistema de chat inteligente com interface web moderna e minimalista, onde usuários podem conversar com uma IA avançada que responde em tempo real, envia arquivos e gerencia múltiplas conversas simultaneamente.

## 🚀 Características

- **Interface Minimalista**: Design fluido e responsivo com foco na experiência do usuário
- **Comunicação em Tempo Real**: WebSocket para mensagens instantâneas
- **IA Avançada**: Integração com modelos de linguagem de última geração
- **Suporte a Arquivos**: Envio e recebimento de documentos, imagens e outros arquivos
- **Multi-usuário**: Suporte para múltiplas conversas simultâneas
- **Responsivo**: Funciona perfeitamente em desktop, tablet e mobile

## 🛠️ Tecnologias

### Backend
- **Flask**: Framework web Python
- **Flask-SocketIO**: Comunicação WebSocket em tempo real
- **OpenAI API**: Integração com modelos de IA
- **SQLite**: Banco de dados para persistência

### Frontend
- **React**: Biblioteca JavaScript para interface
- **Socket.IO Client**: Cliente WebSocket
- **Tailwind CSS**: Framework CSS utilitário
- **Lucide Icons**: Ícones modernos

## 📁 Estrutura do Projeto

```
ai-chat-vice/
├── backend/                 # Servidor Flask
│   ├── app.py              # Aplicação principal
│   ├── models.py           # Modelos de dados
│   ├── ai_service.py       # Serviço de IA
│   └── requirements.txt    # Dependências Python
├── frontend/               # Aplicação React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── hooks/          # Hooks customizados
│   │   └── utils/          # Utilitários
│   ├── public/
│   └── package.json
├── docs/                   # Documentação
└── deployment/             # Configurações de deploy
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- npm ou yarn

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 🌐 Deploy

O projeto está configurado para deploy automático em plataformas como Vercel (frontend) e Railway/Heroku (backend).

## 📝 Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia as diretrizes de contribuição antes de submeter pull requests.

---

**AI Vice** - Conversas inteligentes, experiência excepcional.
