import os
import asyncio
from openai import OpenAI
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4.1-mini"  # Usando o modelo disponível no ambiente
        
    async def generate_response(self, messages: List[Dict[str, str]], session_id: str) -> str:
        """
        Gera uma resposta da IA baseada no histórico de mensagens
        """
        try:
            # Preparar mensagens para a API
            formatted_messages = self._format_messages_for_api(messages)
            
            # Adicionar contexto do sistema
            system_message = {
                "role": "system",
                "content": """Você é o AI Vice, um assistente de IA conversacional inteligente e prestativo. 
                Você está integrado a um sistema de chat em tempo real onde pode:
                - Responder perguntas de forma clara e útil
                - Ajudar com tarefas diversas
                - Manter conversas naturais e envolventes
                - Fornecer informações precisas e atualizadas
                
                Seja sempre cordial, profissional e mantenha um tom amigável. 
                Responda em português brasileiro, a menos que solicitado de outra forma.
                Mantenha suas respostas concisas mas informativas."""
            }
            
            api_messages = [system_message] + formatted_messages
            
            # Fazer chamada para a API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                max_tokens=1000,
                temperature=0.7,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta da IA: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente em alguns instantes."
    
    def _format_messages_for_api(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Formata mensagens do banco de dados para o formato da API OpenAI
        """
        formatted = []
        
        for msg in messages[-10:]:  # Pegar apenas as últimas 10 mensagens para contexto
            role = "user" if msg.get('sender') == 'user' else "assistant"
            content = msg.get('content', '')
            
            # Se for uma mensagem com arquivo, incluir informação sobre o arquivo
            if msg.get('message_type') == 'file' and msg.get('file_name'):
                content = f"[Arquivo enviado: {msg.get('file_name')}] {content}"
            
            formatted.append({
                "role": role,
                "content": content
            })
        
        return formatted
    
    async def analyze_file(self, file_path: str, file_name: str) -> str:
        """
        Analisa um arquivo enviado pelo usuário
        """
        try:
            file_extension = os.path.splitext(file_name)[1].lower()
            
            if file_extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']:
                # Ler arquivo de texto
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um assistente que analisa arquivos. Forneça um resumo útil e insights sobre o conteúdo do arquivo."
                        },
                        {
                            "role": "user",
                            "content": f"Analise este arquivo ({file_name}):\n\n{content[:4000]}"  # Limitar tamanho
                        }
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                
                return response.choices[0].message.content
            
            else:
                return f"Recebi o arquivo '{file_name}'. Este tipo de arquivo ({file_extension}) não pode ser analisado automaticamente, mas foi salvo com sucesso."
                
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo: {str(e)}")
            return f"Recebi o arquivo '{file_name}', mas ocorreu um erro ao analisá-lo. O arquivo foi salvo com sucesso."
    
    def get_welcome_message(self) -> str:
        """
        Retorna uma mensagem de boas-vindas
        """
        return """👋 Olá! Eu sou o **AI Vice**, seu assistente de IA conversacional.

Estou aqui para ajudar você com:
• Responder perguntas sobre qualquer assunto
• Analisar documentos e arquivos que você enviar
• Ajudar com tarefas de programação, escrita e pesquisa
• Manter conversas naturais e informativas

Como posso ajudar você hoje?"""
