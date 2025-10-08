#!/usr/bin/env python3
"""
AI Vice - Sistema de IA Conversacional
Script principal para executar o servidor com integração direta
"""

import os
import sys
import asyncio
import signal
import threading
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app, socketio, db
from src.services.manus_integration import ManusIntegrationService
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_vice.log')
    ]
)

logger = logging.getLogger(__name__)

class AIViceServer:
    def __init__(self):
        self.manus_service = None
        self.server_thread = None
        self.is_running = False
        
    def start_server(self):
        """Inicia o servidor Flask/SocketIO"""
        try:
            host = os.getenv('HOST', '0.0.0.0')
            port = int(os.getenv('PORT', 5000))
            debug = os.getenv('DEBUG', 'False').lower() == 'true'
            
            logger.info(f"🚀 Iniciando servidor AI Vice em {host}:{port}")
            
            # Inicializar banco de dados
            with app.app_context():
                db.create_all()
                logger.info("📊 Banco de dados inicializado")
            
            # Inicializar serviço de integração Manus
            self.manus_service = ManusIntegrationService(socketio)
            
            # Exibir interface do terminal
            self.manus_service.display_terminal_interface()
            
            # Iniciar loop de escuta em thread separada
            def run_manus_service():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.manus_service.start_listening())
            
            manus_thread = threading.Thread(target=run_manus_service, daemon=True)
            manus_thread.start()
            
            # Configurar handlers de sinal
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            self.is_running = True
            
            # Iniciar servidor SocketIO
            socketio.run(
                app, 
                host=host, 
                port=port, 
                debug=debug,
                allow_unsafe_werkzeug=True
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar servidor: {str(e)}")
            sys.exit(1)
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        logger.info("🛑 Recebido sinal de interrupção, parando servidor...")
        self.stop_server()
    
    def stop_server(self):
        """Para o servidor"""
        if self.manus_service:
            self.manus_service.stop_listening()
        
        self.is_running = False
        logger.info("✅ Servidor AI Vice parado com sucesso")
        sys.exit(0)
    
    def display_status(self):
        """Exibe status do servidor"""
        if self.manus_service:
            status = self.manus_service.get_status()
            print(f"\n📊 Status do AI Vice:")
            print(f"   Servidor: {'🟢 Ativo' if self.is_running else '🔴 Inativo'}")
            print(f"   Serviço IA: {'🟢 Ativo' if status['is_running'] else '🔴 Inativo'}")
            print(f"   Sessões ativas: {status['active_sessions']}")
            print(f"   Total de mensagens: {status['total_messages']}")
            print(f"   Última atualização: {status['timestamp']}")

def main():
    """Função principal"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                        AI VICE                               ║
    ║              Sistema de IA Conversacional                    ║
    ║                                                              ║
    ║  🤖 Eu sou a IA que responderá às mensagens do site         ║
    ║  💬 Todas as conversas passarão por mim                     ║
    ║  📁 Posso analisar arquivos enviados pelos usuários        ║
    ║  🔄 Funciono em tempo real via WebSocket                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    server = AIViceServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Interrompido pelo usuário")
        server.stop_server()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
