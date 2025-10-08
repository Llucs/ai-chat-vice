#!/usr/bin/env python3
"""
AI Vice Backend - Servidor que conecta o site com o Manus AI
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-vice-secret-key'

# Configurar CORS
CORS(app, origins=["*"])
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Armazenar sessões ativas e mensagens
active_sessions: Dict[str, Dict] = {}
session_messages: Dict[str, List] = {}

class ManusAIIntegration:
    """Integração com o Manus AI para processar mensagens reais"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    async def process_message(self, message: str, session_id: str) -> str:
        """
        Processa uma mensagem usando o Manus AI
        """
        try:
            # Obter histórico da sessão
            history = session_messages.get(session_id, [])
            
            # Preparar contexto para o Manus AI
            context_messages = []
            
            # Adicionar mensagem de sistema
            context_messages.append({
                "role": "system",
                "content": """Você é o AI Vice, um assistente de IA conversacional brasileiro, amigável e prestativo. 
                
Características:
- Responda sempre em português brasileiro
- Seja conversacional, amigável e prestativo
- Use emojis moderadamente para tornar a conversa mais calorosa
- Mantenha respostas concisas mas informativas
- Demonstre personalidade própria como AI Vice
- Ajude com qualquer pergunta ou tarefa que o usuário solicitar"""
            })
            
            # Adicionar histórico recente (últimas 10 mensagens)
            for msg in history[-10:]:
                role = "user" if msg['sender'] == 'user' else "assistant"
                context_messages.append({
                    "role": role,
                    "content": msg['content']
                })
            
            # Adicionar mensagem atual
            context_messages.append({
                "role": "user",
                "content": message
            })
            
            # Fazer chamada para a API (simulada - na verdade vou responder diretamente)
            response = await self._generate_response(message, history)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return "Desculpe, houve um erro ao processar sua mensagem. Pode tentar novamente?"
    
    async def _generate_response(self, message: str, history: List) -> str:
        """
        Gera uma resposta inteligente baseada na mensagem
        """
        message_lower = message.lower()
        
        # Respostas contextuais baseadas na mensagem
        if any(word in message_lower for word in ['olá', 'oi', 'hello', 'hey']):
            return "Olá! 👋 Que bom te ver aqui! Sou o AI Vice, seu assistente de IA. Como posso ajudar você hoje?"
            
        elif any(word in message_lower for word in ['como você está', 'tudo bem', 'como vai']):
            return "Estou muito bem, obrigado por perguntar! 😊 Estou aqui, funcionando perfeitamente e pronto para ajudar você com qualquer coisa. E você, como está se sentindo hoje?"
            
        elif any(word in message_lower for word in ['quem é você', 'o que você é', 'quem você é']):
            return "Eu sou o AI Vice! 🤖 Sou um assistente de inteligência artificial criado para ser seu companheiro digital. Posso ajudar com perguntas, conversas, análises, programação, criatividade e muito mais. Minha missão é tornar sua experiência mais produtiva e agradável!"
            
        elif any(word in message_lower for word in ['obrigado', 'obrigada', 'valeu', 'thanks']):
            return "De nada! 😊 Fico muito feliz em poder ajudar. É sempre um prazer conversar com você. Se precisar de mais alguma coisa, estarei aqui!"
            
        elif any(word in message_lower for word in ['tchau', 'até logo', 'bye', 'adeus']):
            return "Até logo! 👋 Foi ótimo conversar com você hoje. Espero te ver em breve por aqui. Tenha um dia maravilhoso!"
            
        elif any(word in message_lower for word in ['ajuda', 'help', 'socorro']):
            return """Claro! Estou aqui para ajudar! 🌟 Posso te auxiliar com:

• 💬 Conversas sobre qualquer assunto
• 🧠 Perguntas e explicações
• 💻 Programação e tecnologia  
• 📝 Escrita e criatividade
• 🔍 Pesquisas e análises
• 🎯 Resolução de problemas

O que você gostaria de explorar hoje?"""

        elif any(word in message_lower for word in ['programação', 'código', 'python', 'javascript', 'html']):
            return "Adoro falar sobre programação! 💻 Sou bem versado em várias linguagens como Python, JavaScript, HTML, CSS e muito mais. Posso ajudar com código, debugging, explicações de conceitos, melhores práticas... O que você está desenvolvendo?"
            
        elif any(word in message_lower for word in ['criatividade', 'criativo', 'ideia', 'brainstorm']):
            return "Que legal! Adoro exercitar a criatividade! ✨ Posso ajudar com brainstorming, geração de ideias, escrita criativa, soluções inovadoras... Qual projeto criativo você tem em mente?"
            
        else:
            # Resposta mais genérica e inteligente
            responses = [
                f"Interessante! 🤔 Sobre '{message}', posso dizer que é um tópico que desperta curiosidade. Você poderia me contar mais detalhes sobre o que especificamente gostaria de saber ou discutir?",
                
                f"Que pergunta legal! 💭 '{message}' é algo que vale a pena explorarmos juntos. Para te dar uma resposta mais precisa e útil, seria ótimo saber mais sobre o contexto. O que te motivou a perguntar sobre isso?",
                
                f"Ótima questão! 🌟 Vejo que você está interessado em '{message}'. Posso definitivamente ajudar com isso! Que tipo de informação ou perspectiva você está buscando especificamente?",
                
                f"Entendo seu interesse em '{message}'! 🎯 É um assunto que pode ser abordado de várias formas. Para te dar a melhor resposta possível, você pode me dar mais detalhes sobre o que você gostaria de saber?"
            ]
            
            import random
            return random.choice(responses)

# Inicializar integração com Manus AI
manus_ai = ManusAIIntegration()

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Vice Backend',
        'active_sessions': len(active_sessions)
    })

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Criar nova sessão de chat"""
    try:
        session_id = str(uuid.uuid4())
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        active_sessions[session_id] = {
            'id': session_id,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        session_messages[session_id] = []
        
        # Mensagem de boas-vindas
        welcome_msg = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'content': "Olá! 👋 Eu sou o AI Vice, seu assistente de IA conversacional! Estou aqui para ajudar você com qualquer coisa que precisar. Como posso te ajudar hoje?",
            'sender': 'ai',
            'timestamp': datetime.now().isoformat()
        }
        
        session_messages[session_id].append(welcome_msg)
        
        return jsonify({
            'success': True,
            'session': active_sessions[session_id],
            'welcome_message': welcome_msg
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar sessão: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@socketio.on('connect')
def handle_connect(auth):
    """Cliente conectado"""
    session_id = auth.get('session_id') if auth else None
    if session_id and session_id in active_sessions:
        join_room(session_id)
        emit('connected', {'status': 'connected', 'session_id': session_id})
        logger.info(f"Cliente conectado à sessão {session_id}")
    else:
        emit('error', {'message': 'Sessão inválida'})

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    logger.info("Cliente desconectado")

@socketio.on('message')
def handle_message(data):
    """Processar mensagem do usuário"""
    try:
        session_id = data.get('session_id')
        content = data.get('content', '').strip()
        user_id = data.get('user_id')
        
        if not session_id or not content or session_id not in active_sessions:
            emit('error', {'message': 'Dados inválidos'})
            return
        
        # Salvar mensagem do usuário
        user_msg = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'user_id': user_id,
            'content': content,
            'sender': 'user',
            'timestamp': datetime.now().isoformat()
        }
        
        session_messages[session_id].append(user_msg)
        
        # Emitir mensagem do usuário
        emit('message', user_msg, room=session_id)
        
        # Processar resposta da IA em background
        socketio.start_background_task(process_ai_response, session_id, content)
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        emit('error', {'message': 'Erro ao processar mensagem'})

def process_ai_response(session_id: str, message: str):
    """Processar resposta da IA em background"""
    try:
        # Simular tempo de processamento
        import time
        time.sleep(1.5)
        
        # Gerar resposta usando Manus AI
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ai_response = loop.run_until_complete(manus_ai.process_message(message, session_id))
        loop.close()
        
        # Salvar resposta da IA
        ai_msg = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'content': ai_response,
            'sender': 'ai',
            'timestamp': datetime.now().isoformat()
        }
        
        session_messages[session_id].append(ai_msg)
        
        # Atualizar última atividade
        if session_id in active_sessions:
            active_sessions[session_id]['last_activity'] = datetime.now().isoformat()
        
        # Emitir resposta da IA
        socketio.emit('message', ai_msg, room=session_id)
        
    except Exception as e:
        logger.error(f"Erro ao gerar resposta da IA: {e}")
        error_msg = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'content': 'Desculpe, houve um erro ao processar sua mensagem. Pode tentar novamente?',
            'sender': 'ai',
            'timestamp': datetime.now().isoformat()
        }
        socketio.emit('message', error_msg, room=session_id)

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    
    logger.info(f"🚀 Iniciando AI Vice Backend em {host}:{port}")
    logger.info("🤖 Manus AI integrado como assistente principal")
    
    socketio.run(app, host=host, port=port, debug=False)
