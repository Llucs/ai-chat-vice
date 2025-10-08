from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
from src.models.message import db, Message, ChatSession
from src.services.ai_service import AIService
from datetime import datetime
import uuid
import os
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)
ai_service = AIService()

# Armazenar sessões ativas
active_sessions = {}

@chat_bp.route('/sessions', methods=['POST'])
def create_session():
    """Criar nova sessão de chat"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', f"user_{uuid.uuid4().hex[:8]}")
        
        session = ChatSession(user_id=user_id)
        db.session.add(session)
        db.session.commit()
        
        # Adicionar mensagem de boas-vindas
        welcome_msg = Message(
            session_id=session.id,
            user_id=user_id,
            content=ai_service.get_welcome_message(),
            sender='ai',
            message_type='text'
        )
        db.session.add(welcome_msg)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'welcome_message': welcome_msg.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar sessão: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/sessions/<session_id>/messages', methods=['GET'])
def get_messages(session_id):
    """Obter mensagens de uma sessão"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        messages = Message.query.filter_by(session_id=session_id)\
                               .order_by(Message.timestamp.desc())\
                               .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'messages': [msg.to_dict() for msg in reversed(messages.items)],
            'has_more': messages.has_next,
            'total': messages.total
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter mensagens: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/sessions/<session_id>/upload', methods=['POST'])
def upload_file(session_id):
    """Upload de arquivo para uma sessão"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nome do arquivo vazio'}), 400
        
        # Criar diretório de uploads se não existir
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', session_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Salvar arquivo
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Salvar informações no banco
        file_msg = Message(
            session_id=session_id,
            content=f"Arquivo enviado: {file.filename}",
            sender='user',
            message_type='file',
            file_url=f"/uploads/{session_id}/{filename}",
            file_name=file.filename,
            file_size=os.path.getsize(file_path)
        )
        db.session.add(file_msg)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': file_msg.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Eventos WebSocket
def handle_connect(auth):
    """Usuário conectado"""
    session_id = auth.get('session_id') if auth else None
    if session_id:
        join_room(session_id)
        active_sessions[request.sid] = session_id
        emit('connected', {'status': 'connected', 'session_id': session_id})
        logger.info(f"Cliente conectado à sessão {session_id}")

def handle_disconnect():
    """Usuário desconectado"""
    session_id = active_sessions.pop(request.sid, None)
    if session_id:
        leave_room(session_id)
        logger.info(f"Cliente desconectado da sessão {session_id}")

async def handle_message(data):
    """Processar mensagem do usuário"""
    try:
        session_id = data.get('session_id')
        content = data.get('content', '').strip()
        user_id = data.get('user_id')
        
        if not session_id or not content:
            emit('error', {'message': 'Dados inválidos'})
            return
        
        # Salvar mensagem do usuário
        user_msg = Message(
            session_id=session_id,
            user_id=user_id,
            content=content,
            sender='user',
            message_type='text'
        )
        db.session.add(user_msg)
        db.session.commit()
        
        # Emitir mensagem do usuário para todos na sala
        emit('message', user_msg.to_dict(), room=session_id)
        
        # Obter histórico de mensagens
        recent_messages = Message.query.filter_by(session_id=session_id)\
                                     .order_by(Message.timestamp.desc())\
                                     .limit(10).all()
        
        messages_for_ai = [msg.to_dict() for msg in reversed(recent_messages)]
        
        # Gerar resposta da IA
        ai_response = await ai_service.generate_response(messages_for_ai, session_id)
        
        # Salvar resposta da IA
        ai_msg = Message(
            session_id=session_id,
            content=ai_response,
            sender='ai',
            message_type='text'
        )
        db.session.add(ai_msg)
        
        # Atualizar última atividade da sessão
        session = ChatSession.query.get(session_id)
        if session:
            session.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        # Emitir resposta da IA
        emit('message', ai_msg.to_dict(), room=session_id)
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        emit('error', {'message': 'Erro ao processar mensagem'})

async def handle_file_analysis(data):
    """Analisar arquivo enviado"""
    try:
        session_id = data.get('session_id')
        file_path = data.get('file_path')
        file_name = data.get('file_name')
        
        if not all([session_id, file_path, file_name]):
            emit('error', {'message': 'Dados do arquivo inválidos'})
            return
        
        # Analisar arquivo com IA
        analysis = await ai_service.analyze_file(file_path, file_name)
        
        # Salvar análise como mensagem da IA
        ai_msg = Message(
            session_id=session_id,
            content=analysis,
            sender='ai',
            message_type='text'
        )
        db.session.add(ai_msg)
        db.session.commit()
        
        # Emitir análise
        emit('message', ai_msg.to_dict(), room=session_id)
        
    except Exception as e:
        logger.error(f"Erro ao analisar arquivo: {str(e)}")
        emit('error', {'message': 'Erro ao analisar arquivo'})
