import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  Chat as ChatIcon,
  Assignment as OrderIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Star as StarIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import axios from 'axios';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const response = await axios.get('/api/analytics');
      setAnalytics(response.data);
    } catch (err) {
      setError('Failed to load analytics data. Please try again.');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon, color = 'primary', subtitle }) => (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{ color: `${color}.main`, mr: 2 }}>
            {icon}
          </Box>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  const ProgressBar = ({ label, value, max, color = 'primary' }) => (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2">{label}</Typography>
        <Typography variant="body2" color="text.secondary">
          {value}/{max}
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={(value / max) * 100}
        color={color}
        sx={{ height: 8, borderRadius: 4 }}
      />
    </Box>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        System Analytics
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Requests"
            value={analytics?.total_requests || 0}
            icon={<ChatIcon sx={{ fontSize: 40 }} />}
            color="primary"
            subtitle="All time"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Successful Responses"
            value={analytics?.successful_responses || 0}
            icon={<ThumbUpIcon sx={{ fontSize: 40 }} />}
            color="success"
            subtitle={`${((analytics?.successful_responses || 0) / (analytics?.total_requests || 1) * 100).toFixed(1)}% success rate`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Response Time"
            value={`${analytics?.average_response_time || 0}s`}
            icon={<ScheduleIcon sx={{ fontSize: 40 }} />}
            color="info"
            subtitle="Response time"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Customer Satisfaction"
            value={`${analytics?.customer_satisfaction || 0}/5.0`}
            icon={<StarIcon sx={{ fontSize: 40 }} />}
            color="warning"
            subtitle="Average rating"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Intent Distribution */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
              Intent Distribution
            </Typography>
            {analytics?.intent_distribution ? (
              Object.entries(analytics.intent_distribution).map(([intent, count]) => (
                <ProgressBar
                  key={intent}
                  label={intent.replace('_', ' ').toUpperCase()}
                  value={count}
                  max={analytics.total_requests}
                  color="primary"
                />
              ))
            ) : (
              <Typography color="text.secondary">No data available</Typography>
            )}
          </Paper>
        </Grid>

        {/* Top Products */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
              Top Products
            </Typography>
            {analytics?.top_products ? (
              <List>
                {analytics.top_products.map((product, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon>
                      <Chip
                        label={index + 1}
                        size="small"
                        color="primary"
                        sx={{ minWidth: 32 }}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={product}
                      secondary={`Rank #${index + 1}`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="text.secondary">No data available</Typography>
            )}
          </Paper>
        </Grid>

        {/* Common Issues */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
              Common Issues
            </Typography>
            {analytics?.common_issues ? (
              <List>
                {analytics.common_issues.map((issue, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon>
                      <Chip
                        label={index + 1}
                        size="small"
                        color="warning"
                        sx={{ minWidth: 32 }}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={issue}
                      secondary="Frequently reported"
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="text.secondary">No data available</Typography>
            )}
          </Paper>
        </Grid>

        {/* System Health */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
              System Health
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Database Connection
              </Typography>
              <LinearProgress
                variant="determinate"
                value={100}
                color="success"
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                AI Model Status
              </Typography>
              <LinearProgress
                variant="determinate"
                value={100}
                color="success"
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Cache Performance
              </Typography>
              <LinearProgress
                variant="determinate"
                value={95}
                color="success"
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Box>
              <Typography variant="body2" sx={{ mb: 1 }}>
                API Response Time
              </Typography>
              <LinearProgress
                variant="determinate"
                value={85}
                color="info"
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Performance Summary */}
      <Paper elevation={2} sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
          Performance Summary
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="success.main" sx={{ fontWeight: 'bold' }}>
                {((analytics?.successful_responses || 0) / (analytics?.total_requests || 1) * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Success Rate
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="primary.main" sx={{ fontWeight: 'bold' }}>
                {analytics?.average_response_time || 0}s
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Response Time
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="warning.main" sx={{ fontWeight: 'bold' }}>
                {analytics?.customer_satisfaction || 0}/5
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Customer Rating
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default Analytics;
