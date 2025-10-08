import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from src.models.message import db, Message, ChatSession
from src.services.ai_service import AIService

logger = logging.getLogger(__name__)

class ManusIntegrationService:
    """
    Serviço de integração direta com Manus para processar mensagens em tempo real
    """
    
    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
        self.ai_service = AIService()
        self.is_running = False
        self.active_sessions = {}
        
    async def start_listening(self):
        """
        Inicia o serviço de escuta para mensagens dos usuários
        """
        self.is_running = True
        logger.info("🤖 AI Vice iniciado - Aguardando mensagens dos usuários...")
        
        while self.is_running:
            try:
                # Verificar por novas mensagens não processadas
                await self._process_pending_messages()
                await asyncio.sleep(1)  # Verificar a cada segundo
                
            except Exception as e:
                logger.error(f"Erro no loop principal: {str(e)}")
                await asyncio.sleep(5)
    
    async def _process_pending_messages(self):
        """
        Processa mensagens pendentes de resposta
        """
        try:
            # Buscar mensagens de usuários que ainda não foram respondidas
            pending_messages = self._get_pending_user_messages()
            
            for message in pending_messages:
                await self._process_user_message(message)
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagens pendentes: {str(e)}")
    
    def _get_pending_user_messages(self):
        """
        Busca mensagens de usuários que precisam de resposta
        """
        try:
            # Buscar mensagens de usuários dos últimos 5 minutos que não têm resposta da IA
            recent_time = datetime.utcnow().replace(second=0, microsecond=0)
            
            # Query para encontrar mensagens de usuário sem resposta subsequente da IA
            user_messages = db.session.query(Message).filter(
                Message.sender == 'user',
                Message.timestamp >= recent_time.replace(minute=recent_time.minute - 5)
            ).order_by(Message.timestamp.desc()).all()
            
            pending = []
            for msg in user_messages:
                # Verificar se já existe uma resposta da IA para esta mensagem
                ai_response = db.session.query(Message).filter(
                    Message.session_id == msg.session_id,
                    Message.sender == 'ai',
                    Message.timestamp > msg.timestamp
                ).first()
                
                if not ai_response:
                    pending.append(msg)
            
            return pending
            
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens pendentes: {str(e)}")
            return []
    
    async def _process_user_message(self, message: Message):
        """
        Processa uma mensagem individual do usuário
        """
        try:
            session_id = message.session_id
            
            # Log da mensagem recebida
            logger.info(f"📨 Nova mensagem de {message.user_id or 'usuário anônimo'}: {message.content[:100]}...")
            
            # Obter histórico da conversa
            conversation_history = self._get_conversation_history(session_id)
            
            # Gerar resposta da IA
            logger.info("🧠 Processando resposta...")
            ai_response = await self.ai_service.generate_response(conversation_history, session_id)
            
            # Salvar resposta no banco
            ai_message = Message(
                session_id=session_id,
                content=ai_response,
                sender='ai',
                message_type='text'
            )
            db.session.add(ai_message)
            
            # Atualizar última atividade da sessão
            session = ChatSession.query.get(session_id)
            if session:
                session.last_activity = datetime.utcnow()
            
            db.session.commit()
            
            # Emitir resposta via WebSocket
            self.socketio.emit('message', ai_message.to_dict(), room=session_id)
            
            # Log da resposta enviada
            logger.info(f"✅ Resposta enviada para sessão {session_id}: {ai_response[:100]}...")
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem do usuário: {str(e)}")
    
    def _get_conversation_history(self, session_id: str) -> list:
        """
        Obtém o histórico da conversa para contexto
        """
        try:
            messages = Message.query.filter_by(session_id=session_id)\
                                  .order_by(Message.timestamp.desc())\
                                  .limit(20).all()
            
            return [msg.to_dict() for msg in reversed(messages)]
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {str(e)}")
            return []
    
    async def handle_file_message(self, message: Message):
        """
        Processa mensagens com arquivos
        """
        try:
            if message.file_url and message.file_name:
                logger.info(f"📎 Analisando arquivo: {message.file_name}")
                
                # Construir caminho completo do arquivo
                file_path = f"/home/ubuntu/ai-chat-vice/backend/ai_vice_backend/src{message.file_url}"
                
                # Analisar arquivo
                analysis = await self.ai_service.analyze_file(file_path, message.file_name)
                
                # Salvar análise
                ai_message = Message(
                    session_id=message.session_id,
                    content=analysis,
                    sender='ai',
                    message_type='text'
                )
                db.session.add(ai_message)
                db.session.commit()
                
                # Emitir análise
                self.socketio.emit('message', ai_message.to_dict(), room=message.session_id)
                
                logger.info(f"📋 Análise de arquivo enviada para sessão {message.session_id}")
                
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo: {str(e)}")
    
    def stop_listening(self):
        """
        Para o serviço de escuta
        """
        self.is_running = False
        logger.info("🛑 Serviço AI Vice parado")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retorna status do serviço
        """
        active_sessions_count = len(self.active_sessions)
        total_sessions = ChatSession.query.filter_by(is_active=True).count()
        total_messages = Message.query.count()
        
        return {
            'is_running': self.is_running,
            'active_sessions': active_sessions_count,
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def display_terminal_interface(self):
        """
        Exibe interface no terminal para monitoramento
        """
        print("\n" + "="*60)
        print("🤖 AI VICE - SISTEMA DE IA CONVERSACIONAL")
        print("="*60)
        print("Status: ATIVO - Aguardando mensagens...")
        print("Pressione Ctrl+C para parar o serviço")
        print("="*60)
        
        # Exibir estatísticas em tempo real
        status = self.get_status()
        print(f"📊 Sessões ativas: {status['active_sessions']}")
        print(f"💬 Total de mensagens: {status['total_messages']}")
        print(f"🕒 Última atualização: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        print("Logs em tempo real:")
        print("-"*60)
