import os
import asyncio
from typing import List, Dict, Any, Optional
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        """
        Inicializa o serviço de IA com integração real à OpenAI API.
        """
        self.client = OpenAI()  # API key e base URL já configuradas nas variáveis de ambiente
        self.model = "gpt-4.1-mini"  # Modelo disponível no ambiente
        
    async def generate_response(self, messages: List[Dict[str, str]], session_id: str) -> str:
        """
        Gera uma resposta da IA baseada no histórico de mensagens usando a OpenAI API.
        """
        try:
            # Formatar mensagens para a API
            formatted_messages = self._format_messages_for_api(messages)
            
            # Adicionar mensagem de sistema para definir o comportamento da IA
            system_message = {
                "role": "system",
                "content": """Você é o AI Vice, um assistente de IA conversacional inteligente e prestativo. 
                
Características:
- Responda sempre em português brasileiro
- Seja amigável, profissional e útil
- Forneça respostas detalhadas e informativas
- Quando analisar arquivos, seja específico e detalhado
- Mantenha o contexto da conversa
- Se não souber algo, seja honesto sobre suas limitações
- Use formatação markdown quando apropriado para melhor legibilidade

Seu objetivo é ajudar os usuários com suas perguntas, análise de documentos e tarefas diversas."""
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
            
            ai_response = response.choices[0].message.content
            logger.info(f"OpenAI API gerou resposta para sessão {session_id}: {ai_response[:100]}...")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta da IA via OpenAI API: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente em alguns instantes."
    
    def _format_messages_for_api(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Formata mensagens do banco de dados para o formato esperado pela OpenAI API.
        """
        formatted = []
        
        for msg in messages:
            role = "assistant" if msg.get("sender") == "ai" else "user"
            content = msg.get("content", "")
            
            # Adicionar informações sobre arquivos se presente
            if msg.get("message_type") == "file" and msg.get("file_name"):
                content = f"[Arquivo enviado: {msg.get('file_name')}] {content}"
            
            formatted.append({
                "role": role,
                "content": content
            })
        
        return formatted
    
    async def analyze_file(self, file_path: str, file_name: str) -> str:
        """
        Analisa um arquivo enviado pelo usuário usando a OpenAI API.
        """
        try:
            file_extension = os.path.splitext(file_name)[1].lower()
            
            # Ler conteúdo do arquivo se for texto
            if file_extension in [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml", ".csv"]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Tentar com encoding latin-1 se UTF-8 falhar
                    with open(file_path, "r", encoding="latin-1") as f:
                        content = f.read()
                
                # Limitar o tamanho do conteúdo para não exceder limites da API
                if len(content) > 8000:
                    content = content[:8000] + "\n\n[Conteúdo truncado devido ao tamanho...]"
                
                # Criar prompt para análise
                analysis_prompt = f"""Analise o seguinte arquivo:

Nome do arquivo: {file_name}
Tipo: {file_extension}
Conteúdo:
```
{content}
```

Por favor, forneça uma análise detalhada incluindo:
1. Resumo do conteúdo
2. Estrutura e organização
3. Pontos principais ou funcionalidades (se aplicável)
4. Qualidade do código (se for um arquivo de programação)
5. Sugestões de melhoria (se apropriado)
6. Qualquer observação relevante"""

                # Fazer chamada para a API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um especialista em análise de arquivos e documentos. Forneça análises detalhadas e úteis em português brasileiro."
                        },
                        {
                            "role": "user",
                            "content": analysis_prompt
                        }
                    ],
                    max_tokens=1500,
                    temperature=0.3
                )
                
                return response.choices[0].message.content
            
            elif file_extension in [".jpg", ".jpeg", ".png", ".gif"]:
                return f"""📸 **Análise de Imagem: {file_name}**

Recebi sua imagem! Infelizmente, no momento não posso processar o conteúdo visual de imagens diretamente, mas posso ajudar você de outras formas:

• Se você descrever o que há na imagem, posso fornecer informações relacionadas
• Posso ajudar com edição de imagens, formatos, compressão, etc.
• Se for um screenshot de código ou texto, você pode digitar o conteúdo que eu analiso

Como posso ajudar você com esta imagem?"""
            
            elif file_extension == ".pdf":
                return f"""📄 **Análise de PDF: {file_name}**

Recebi seu arquivo PDF! Para uma análise mais detalhada, eu precisaria extrair o texto do documento. No momento, posso ajudar você:

• Se você copiar e colar partes específicas do texto, posso analisá-las
• Posso fornecer informações sobre PDFs em geral
• Posso ajudar com conversão de formatos, compressão, etc.

Você poderia compartilhar o conteúdo textual que gostaria que eu analisasse?"""
            
            else:
                return f"""📁 **Arquivo Recebido: {file_name}**

Recebi seu arquivo com extensão `{file_extension}`. Este tipo de arquivo não pode ser analisado automaticamente no momento, mas posso ajudar você:

• Se você descrever o conteúdo ou propósito do arquivo, posso fornecer orientações
• Posso ajudar com informações sobre este tipo de arquivo
• Se for possível converter para um formato de texto, posso analisar o conteúdo

Como posso ajudar você com este arquivo?"""
                
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo via OpenAI API: {str(e)}")
            return f"""❌ **Erro na Análise**

Recebi o arquivo `{file_name}`, mas ocorreu um erro durante a análise. O arquivo foi salvo com sucesso.

Você pode tentar:
• Reenviar o arquivo
• Descrever o conteúdo manualmente para que eu possa ajudar
• Verificar se o arquivo não está corrompido

Como posso ajudar você de outra forma?"""
    
    def get_welcome_message(self) -> str:
        """
        Retorna uma mensagem de boas-vindas personalizada.
        """
        return """👋 **Olá! Eu sou o AI Vice!**

Sou seu assistente de IA conversacional, powered by **GPT-4.1-mini**. Estou aqui para ajudar você com:

🤖 **Conversas Inteligentes**
• Responder perguntas sobre qualquer assunto
• Explicar conceitos complexos de forma simples
• Ajudar com pesquisas e análises

📁 **Análise de Arquivos**
• Analisar códigos, documentos e textos
• Revisar e sugerir melhorias
• Explicar estruturas e funcionalidades

💡 **Assistência Técnica**
• Programação e desenvolvimento
• Escrita e redação
• Resolução de problemas

✨ **Como usar:**
• Digite suas perguntas normalmente
• Use o botão 📎 para enviar arquivos
• Mantenha a conversa fluindo naturalmente

**Como posso ajudar você hoje?** 🚀"""
