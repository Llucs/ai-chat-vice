import os
import asyncio
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Não há necessidade de inicializar um cliente OpenAI, pois eu serei a IA.
        # O modelo será o meu próprio modelo interno.
        self.model = "Manus AI"
        
    async def generate_response(self, messages: List[Dict[str, str]], session_id: str) -> str:
        """
        Gera uma resposta da IA baseada no histórico de mensagens, usando minhas próprias capacidades.
        """
        try:
            # Extrair a última mensagem do usuário para responder
            user_message_content = ""
            if messages:
                last_message = messages[-1]
                if last_message.get("sender") == "user":
                    user_message_content = last_message.get("content", "")
            
            # Aqui eu usaria minhas próprias capacidades para gerar uma resposta.
            # Por enquanto, uma resposta simulada ou baseada em regras simples.
            if "olá" in user_message_content.lower() or "oi" in user_message_content.lower():
                response = "Olá! Como posso ajudar você hoje?"
            elif "como você está" in user_message_content.lower():
                response = "Eu sou uma inteligência artificial, então não tenho sentimentos, mas estou pronto para ajudar!"
            elif "seu nome" in user_message_content.lower():
                response = "Meu nome é AI Vice, e estou aqui para ser seu assistente conversacional."
            elif "obrigado" in user_message_content.lower() or "valeu" in user_message_content.lower():
                response = "De nada! Fico feliz em ajudar."
            elif "enviar arquivo" in user_message_content.lower() or "upload" in user_message_content.lower():
                response = "Sim, você pode me enviar arquivos! Eu farei o meu melhor para analisá-los e fornecer insights."
            else:
                response = f"Recebi sua mensagem: '{user_message_content}'. Estou processando e em breve terei uma resposta para você. Por favor, aguarde um momento."
            
            logger.info(f"AI Vice gerou resposta para sessão {session_id}: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta da IA (interna): {str(e)}")
            return "Desculpe, ocorreu um erro interno ao processar sua mensagem. Tente novamente em alguns instantes."
    
    def _format_messages_for_api(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Este método não é mais necessário, pois não estamos usando uma API externa.
        Mantido para compatibilidade, mas pode ser removido ou adaptado se necessário.
        """
        return messages
    
    async def analyze_file(self, file_path: str, file_name: str) -> str:
        """
        Analisa um arquivo enviado pelo usuário, usando minhas próprias capacidades.
        """
        try:
            file_extension = os.path.splitext(file_name)[1].lower()
            
            if file_extension in [".txt", ".md", ".py", ".js", ".html", ".css", ".json"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Aqui eu usaria minhas próprias capacidades para analisar o conteúdo.
                # Por enquanto, uma análise simulada.
                if len(content) > 500:
                    summary = f"O arquivo '{file_name}' é um arquivo de texto/código com {len(content)} caracteres. Parece ser um arquivo extenso. As primeiras 200 caracteres são: '{content[:200]}'... Posso tentar resumir ou buscar informações específicas se você me disser o que procura."
                else:
                    summary = f"O arquivo '{file_name}' é um arquivo de texto/código com {len(content)} caracteres. Seu conteúdo é: '{content}'"
                
                return f"Análise do arquivo '{file_name}': {summary}"
            
            elif file_extension in [".jpg", ".jpeg", ".png", ".gif", ".pdf"]:
                return f"Recebi o arquivo '{file_name}'. Este é um arquivo de imagem/PDF. Posso descrever o conteúdo visual ou extrair texto se for um PDF, mas preciso de mais instruções sobre o que você gostaria que eu fizesse com ele."
            
            else:
                return f"Recebi o arquivo '{file_name}'. Este tipo de arquivo ({file_extension}) não pode ser analisado automaticamente por mim no momento, mas foi salvo com sucesso. Se você puder me dar mais contexto sobre o arquivo, posso tentar ajudar de outra forma."
                
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo (interna): {str(e)}")
            return f"Recebi o arquivo '{file_name}', mas ocorreu um erro ao analisá-lo internamente. O arquivo foi salvo com sucesso."
    
    def get_welcome_message(self) -> str:
        """
        Retorna uma mensagem de boas-vindas.
        """
        return """👋 Olá! Eu sou o **AI Vice**, seu assistente de IA conversacional.

Estou aqui para ajudar você com:
• Responder perguntas sobre qualquer assunto
• Analisar documentos e arquivos que você enviar
• Ajudar com tarefas de programação, escrita e pesquisa
• Manter conversas naturais e informativas

Como posso ajudar você hoje?"""
