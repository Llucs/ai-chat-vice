import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from src.models.user import db
from src.models.message import Message, ChatSession
from src.routes.user import user_bp
from src.routes.chat import chat_bp, handle_connect, handle_disconnect, handle_message, handle_file_analysis
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar CORS para permitir conexões do GitHub Pages
cors_origins = os.getenv('CORS_ORIGINS', 'https://llucs.github.io').split(',')
CORS(app, origins=cors_origins)

# Inicializar SocketIO
socketio = SocketIO(app, cors_allowed_origins=cors_origins, async_mode='threading')

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api/chat')

# Inicializar banco de dados
db.init_app(app)
with app.app_context():
    db.create_all()

# Eventos WebSocket
@socketio.on('connect')
def on_connect(auth):
    logger.info("Cliente conectado")
    handle_connect(auth)

@socketio.on('disconnect')
def on_disconnect():
    logger.info("Cliente desconectado")
    handle_disconnect()

@socketio.on('message')
def on_message(data):
    logger.info(f"Mensagem recebida: {data}")
    socketio.start_background_task(handle_message, data)

@socketio.on('analyze_file')
def on_analyze_file(data):
    logger.info(f"Análise de arquivo solicitada: {data}")
    socketio.start_background_task(handle_file_analysis, data)

# Rota para servir arquivos estáticos (frontend)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "Backend API está funcionando! Frontend será servido pelo GitHub Pages.", 200

# Rota para servir uploads
@app.route('/uploads/<session_id>/<filename>')
def serve_upload(session_id, filename):
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', session_id)
    return send_from_directory(upload_dir, filename)

# Rota de health check
@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'service': 'AI Vice Backend'}

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Iniciando servidor em {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)
