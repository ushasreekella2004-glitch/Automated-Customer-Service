import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  Search as SearchIcon,
  Assignment as OrderIcon,
  LocalShipping as ShippingIcon,
  CheckCircle as DeliveredIcon,
  Cancel as CancelledIcon,
  Refresh as ReturnIcon
} from '@mui/icons-material';
import axios from 'axios';

const OrderStatus = ({ user }) => {
  const [orderId, setOrderId] = useState('');
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'delivered':
        return <DeliveredIcon color="success" />;
      case 'shipped':
      case 'in transit':
        return <ShippingIcon color="primary" />;
      case 'cancelled':
        return <CancelledIcon color="error" />;
      case 'returned':
      case 'return requested':
        return <ReturnIcon color="warning" />;
      default:
        return <OrderIcon color="action" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'delivered':
        return 'success';
      case 'shipped':
      case 'in transit':
        return 'primary';
      case 'cancelled':
        return 'error';
      case 'returned':
      case 'return requested':
        return 'warning';
      default:
        return 'default';
    }
  };

  const handleSearch = async () => {
    if (!orderId.trim()) return;

    setLoading(true);
    setError(null);
    setOrder(null);

    try {
      const response = await axios.get(`/api/orders/${orderId}`);
      setOrder(response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Order not found. Please check your order ID and try again.');
      } else {
        setError('An error occurred while fetching order details. Please try again.');
      }
      console.error('Order search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        Order Status Lookup
      </Typography>

      {/* Search Section */}
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Enter Order Information
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            fullWidth
            label="Order ID"
            value={orderId}
            onChange={(e) => setOrderId(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your order ID (e.g., 52768)"
            disabled={loading}
          />
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
            onClick={handleSearch}
            disabled={!orderId.trim() || loading}
            sx={{ minWidth: 120 }}
          >
            {loading ? 'Searching...' : 'Search'}
          </Button>
        </Box>
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Order Details */}
      {order && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
            Order Details
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    {getStatusIcon(order.order_status)}
                    <Box sx={{ ml: 1 }}>
                      Order Status
                    </Box>
                  </Typography>
                  <Chip
                    label={order.order_status}
                    color={getStatusColor(order.order_status)}
                    size="large"
                    sx={{ mb: 2 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    Order ID: {order.order_id}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Customer ID: {order.customer_id}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Product Information
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 1, fontWeight: 'bold' }}>
                    {order.product_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Quantity: {order.quantity}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Amount: ${order.order_amount}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Order Date: {new Date(order.order_date).toLocaleDateString()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {order.return_status && (
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ mt: 2 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      Return Information
                    </Typography>
                    <Chip
                      label={order.return_status}
                      color={getStatusColor(order.return_status)}
                      size="large"
                      sx={{ mb: 2 }}
                    />
                    {order.return_reason && (
                      <Typography variant="body2" color="text.secondary">
                        Reason: {order.return_reason}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            )}

            {order.notes && (
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ mt: 2 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      Additional Notes
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {order.notes}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        </Paper>
      )}

      {/* Help Section */}
      <Paper elevation={1} sx={{ p: 3, mt: 3, bgcolor: 'grey.50' }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Need Help?
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          If you can't find your order or need assistance, please contact our customer service team.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button variant="outlined" size="small">
            Contact Support
          </Button>
          <Button variant="outlined" size="small">
            Live Chat
          </Button>
          <Button variant="outlined" size="small">
            View All Orders
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default OrderStatus;
