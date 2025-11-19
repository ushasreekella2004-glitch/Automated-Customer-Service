import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Button,
  CircularProgress,
  Divider,
  Alert
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import axios from 'axios';

const ChatInterface = ({ user, sessionId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    setMessages([
      {
        id: 1,
        text: "Hello! I'm your NVIDIA customer service assistant. How can I help you today?",
        sender: 'bot',
        timestamp: new Date(),
        suggestedActions: [
          "Check Order Status",
          "Product Information", 
          "Return Request",
          "Store Hours"
        ]
      }
    ]);
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/chat', {
        message: inputMessage,
        customer_id: user?.id,
        session_id: sessionId
      });

      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date(),
        intent: response.data.intent,
        confidence: response.data.confidence,
        suggestedActions: response.data.suggested_actions || []
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      setError('Sorry, I encountered an error. Please try again.');
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedAction = (action) => {
    setInputMessage(action);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        text: "Hello! I'm your NVIDIA customer service assistant. How can I help you today?",
        sender: 'bot',
        timestamp: new Date(),
        suggestedActions: [
          "Check Order Status",
          "Product Information", 
          "Return Request",
          "Store Hours"
        ]
      }
    ]);
    setError(null);
  };

  return (
    <Box sx={{ height: '80vh', display: 'flex', flexDirection: 'column' }}>
      <Paper 
        elevation={3} 
        sx={{ 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column',
          overflow: 'hidden'
        }}
      >
        {/* Chat Header */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              Customer Service Chat
            </Typography>
            <Button
              startIcon={<RefreshIcon />}
              onClick={clearChat}
              size="small"
              variant="outlined"
            >
              Clear Chat
            </Button>
          </Box>
        </Box>

        {/* Messages Area */}
        <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
          <List sx={{ pb: 0 }}>
            {messages.map((message) => (
              <ListItem key={message.id} sx={{ alignItems: 'flex-start', px: 0 }}>
                <ListItemAvatar>
                  <Avatar sx={{ 
                    bgcolor: message.sender === 'bot' ? 'primary.main' : 'secondary.main',
                    width: 40,
                    height: 40
                  }}>
                    {message.sender === 'bot' ? <BotIcon /> : <PersonIcon />}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          mb: 1,
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word'
                        }}
                      >
                        {message.text}
                      </Typography>
                      {message.intent && (
                        <Chip 
                          label={`Intent: ${message.intent}`}
                          size="small"
                          variant="outlined"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      )}
                      {message.confidence && (
                        <Chip 
                          label={`Confidence: ${(message.confidence * 100).toFixed(1)}%`}
                          size="small"
                          variant="outlined"
                          color={message.confidence > 0.8 ? 'success' : 'warning'}
                          sx={{ mb: 1 }}
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
            {isLoading && (
              <ListItem sx={{ alignItems: 'center', px: 0 }}>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    <BotIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      <Typography variant="body2" color="text.secondary">
                        AI is thinking...
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            )}
            <div ref={messagesEndRef} />
          </List>
        </Box>

        {/* Suggested Actions */}
        {messages.length > 0 && messages[messages.length - 1].suggestedActions && (
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
              Suggested Actions:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {messages[messages.length - 1].suggestedActions.map((action, index) => (
                <Chip
                  key={index}
                  label={action}
                  onClick={() => handleSuggestedAction(action)}
                  variant="outlined"
                  clickable
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Error Display */}
        {error && (
          <Box sx={{ p: 2 }}>
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </Box>
        )}

        {/* Input Area */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              disabled={isLoading}
              variant="outlined"
              size="small"
            />
            <IconButton
              color="primary"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              sx={{ alignSelf: 'flex-end' }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatInterface;
