import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Typography
} from '@mui/material';
import {
  Chat as ChatIcon,
  Assignment as OrderIcon,
  Inventory as ProductIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const getCurrentTab = () => {
    switch (location.pathname) {
      case '/':
        return 0;
      case '/orders':
        return 1;
      case '/products':
        return 2;
      case '/analytics':
        return 3;
      default:
        return 0;
    }
  };

  const handleTabChange = (event, newValue) => {
    switch (newValue) {
      case 0:
        navigate('/');
        break;
      case 1:
        navigate('/orders');
        break;
      case 2:
        navigate('/products');
        break;
      case 3:
        navigate('/analytics');
        break;
      default:
        navigate('/');
    }
  };

  return (
    <Paper elevation={1} sx={{ mb: 3 }}>
      <Box sx={{ px: 2, py: 1 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
          Customer Service Dashboard
        </Typography>
        <Tabs
          value={getCurrentTab()}
          onChange={handleTabChange}
          variant="fullWidth"
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab
            icon={<ChatIcon />}
            label="Chat Assistant"
            iconPosition="start"
          />
          <Tab
            icon={<OrderIcon />}
            label="Order Status"
            iconPosition="start"
          />
          <Tab
            icon={<ProductIcon />}
            label="Product Search"
            iconPosition="start"
          />
          <Tab
            icon={<AnalyticsIcon />}
            label="Analytics"
            iconPosition="start"
          />
        </Tabs>
      </Box>
    </Paper>
  );
};

export default Navigation;
