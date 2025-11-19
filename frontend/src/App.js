import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material';

import ChatInterface from './components/ChatInterface';
import OrderStatus from './components/OrderStatus';
import ProductSearch from './components/ProductSearch';
import Analytics from './components/Analytics';
import Navigation from './components/Navigation';

const theme = createTheme({
  palette: {
    primary: {
      main: '#76B900', // NVIDIA Green
    },
    secondary: {
      main: '#000000', // NVIDIA Black
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

function App() {
  const [user, setUser] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    // Generate session ID
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
    
    // Initialize user (in production, this would come from authentication)
    setUser({
      id: 'demo_user',
      name: 'Demo User',
      email: 'demo@nvidia.com'
    });
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <AppBar position="static" elevation={0}>
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
                NVIDIA Customer Service
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                AI-Powered Assistant
              </Typography>
            </Toolbar>
          </AppBar>
          
          <Container maxWidth="lg" sx={{ flexGrow: 1, py: 3 }}>
            <Navigation />
            
            <Routes>
              <Route 
                path="/" 
                element={
                  <ChatInterface 
                    user={user} 
                    sessionId={sessionId} 
                  />
                } 
              />
              <Route 
                path="/orders" 
                element={<OrderStatus user={user} />} 
              />
              <Route 
                path="/products" 
                element={<ProductSearch />} 
              />
              <Route 
                path="/analytics" 
                element={<Analytics />} 
              />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
