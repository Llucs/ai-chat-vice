#!/usr/bin/env python3
"""
AI Vice - Sistema de IA Conversacional
Script principal para executar o servidor Flask/SocketIO
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app, socketio
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

def main():
    """Função principal"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                        AI VICE                               ║
    ║              Sistema de IA Conversacional                    ║
    ║                                                              ║
    ║  🤖 Integração direta com OpenAI GPT-4.1-mini              ║
    ║  💬 Comunicação em tempo real via WebSocket                 ║
    ║  📁 Análise inteligente de arquivos                         ║
    ║  🔄 Suporte a múltiplos usuários simultâneos               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        logger.info(f"🚀 Iniciando servidor AI Vice em {host}:{port}")
        logger.info("🤖 IA OpenAI GPT-4.1-mini configurada e pronta")
        logger.info("📡 WebSocket habilitado para comunicação em tempo real")
        
        # Iniciar servidor SocketIO
        socketio.run(
            app, 
            host=host, 
            port=port, 
            debug=debug,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
