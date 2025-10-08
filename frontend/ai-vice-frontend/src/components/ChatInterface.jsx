import { useState, useEffect, useRef } from 'react'
import { io } from 'socket.io-client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Send, Paperclip, Bot, User, FileText, Download } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const BACKEND_URL = process.env.NODE_ENV === 'production' 
  ? 'https://ai-vice-backend.railway.app' // URL do backend em produção
  : 'http://localhost:5000'

export default function ChatInterface() {
  const [socket, setSocket] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [userId] = useState(() => `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  // Scroll para a última mensagem
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Inicializar conexão
  useEffect(() => {
    initializeChat()
    return () => {
      if (socket) {
        socket.disconnect()
      }
    }
  }, [])

  const initializeChat = async () => {
    try {
      // Criar nova sessão
      const response = await fetch(`${BACKEND_URL}/api/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
      })

      const data = await response.json()
      if (data.success) {
        setSessionId(data.session.id)
        setMessages([data.welcome_message])
        
        // Conectar WebSocket
        const newSocket = io(BACKEND_URL, {
          auth: {
            session_id: data.session.id
          }
        })

        newSocket.on('connect', () => {
          setIsConnected(true)
          console.log('Conectado ao servidor')
        })

        newSocket.on('disconnect', () => {
          setIsConnected(false)
          console.log('Desconectado do servidor')
        })

        newSocket.on('message', (message) => {
          setMessages(prev => [...prev, message])
          setIsTyping(false)
        })

        newSocket.on('error', (error) => {
          console.error('Erro:', error)
          setIsTyping(false)
        })

        setSocket(newSocket)
      }
    } catch (error) {
      console.error('Erro ao inicializar chat:', error)
    }
  }

  const sendMessage = () => {
    if (!inputMessage.trim() || !socket || !sessionId) return

    const messageData = {
      session_id: sessionId,
      content: inputMessage.trim(),
      user_id: userId
    }

    socket.emit('message', messageData)
    setInputMessage('')
    setIsTyping(true)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file || !sessionId) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${BACKEND_URL}/api/chat/sessions/${sessionId}/upload`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()
      if (data.success) {
        setMessages(prev => [...prev, data.message])
        
        // Solicitar análise do arquivo
        if (socket) {
          socket.emit('analyze_file', {
            session_id: sessionId,
            file_path: data.message.file_url,
            file_name: data.message.file_name
          })
          setIsTyping(true)
        }
      }
    } catch (error) {
      console.error('Erro no upload:', error)
    }

    // Limpar input
    event.target.value = ''
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const renderMessage = (message, index) => {
    const isAI = message.sender === 'ai'
    const isFile = message.message_type === 'file'

    return (
      <motion.div
        key={message.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: index * 0.1 }}
        className={`flex gap-3 mb-4 ${isAI ? 'justify-start' : 'justify-end'}`}
      >
        {isAI && (
          <Avatar className="w-8 h-8 mt-1">
            <AvatarFallback className="bg-primary text-primary-foreground">
              <Bot className="w-4 h-4" />
            </AvatarFallback>
          </Avatar>
        )}
        
        <div className={`max-w-[70%] ${isAI ? 'order-2' : 'order-1'}`}>
          <Card className={`${isAI ? 'bg-muted' : 'bg-primary text-primary-foreground'}`}>
            <CardContent className="p-3">
              {isFile && (
                <div className="flex items-center gap-2 mb-2 p-2 bg-background/10 rounded">
                  <FileText className="w-4 h-4" />
                  <span className="text-sm font-medium">{message.file_name}</span>
                  {message.file_url && (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-6 w-6 p-0"
                      onClick={() => window.open(`${BACKEND_URL}${message.file_url}`, '_blank')}
                    >
                      <Download className="w-3 h-3" />
                    </Button>
                  )}
                </div>
              )}
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              <div className="flex items-center justify-between mt-2">
                <Badge variant="secondary" className="text-xs">
                  {formatTimestamp(message.timestamp)}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {!isAI && (
          <Avatar className="w-8 h-8 mt-1">
            <AvatarFallback className="bg-secondary text-secondary-foreground">
              <User className="w-4 h-4" />
            </AvatarFallback>
          </Avatar>
        )}
      </motion.div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <Card className="rounded-none border-b">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Avatar className="w-10 h-10">
                <AvatarFallback className="bg-primary text-primary-foreground">
                  <Bot className="w-5 h-5" />
                </AvatarFallback>
              </Avatar>
              <div>
                <CardTitle className="text-lg">AI Vice</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Assistente de IA Conversacional
                </p>
              </div>
            </div>
            <Badge variant={isConnected ? 'default' : 'destructive'}>
              {isConnected ? 'Conectado' : 'Desconectado'}
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          <AnimatePresence>
            {messages.map((message, index) => renderMessage(message, index))}
          </AnimatePresence>
          
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex gap-3 mb-4"
            >
              <Avatar className="w-8 h-8 mt-1">
                <AvatarFallback className="bg-primary text-primary-foreground">
                  <Bot className="w-4 h-4" />
                </AvatarFallback>
              </Avatar>
              <Card className="bg-muted">
                <CardContent className="p-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input Area */}
      <Card className="rounded-none border-t">
        <CardContent className="p-4">
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              disabled={!isConnected}
            >
              <Paperclip className="w-4 h-4" />
            </Button>
            
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Digite sua mensagem..."
              disabled={!isConnected}
              className="flex-1"
            />
            
            <Button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || !isConnected}
              size="icon"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileUpload}
            className="hidden"
            accept="*/*"
          />
        </CardContent>
      </Card>
    </div>
  )
}
