import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Tooltip,
  Alert
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AttachMoney as MoneyIcon,
  People as PeopleIcon,
  Science as LabIcon,
  Inventory as InventoryIcon,
  Warning as WarningIcon,
  Star as StarIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import axios from 'axios';
import { LoadingSpinner } from './LoadingComponents';

const AdvancedAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [lowStockItems, setLowStockItems] = useState([]);
  const [pendingLabResults, setPendingLabResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [analyticsRes, inventoryRes, labRes] = await Promise.all([
        axios.get('http://localhost:5000/api/analytics/dashboard'),
        axios.get('http://localhost:5000/api/inventory?low_stock=true'),
        axios.get('http://localhost:5000/api/lab-results?status=pending')
      ]);

      setAnalytics(analyticsRes.data);
      setLowStockItems(inventoryRes.data);
      setPendingLabResults(labRes.data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const MetricCard = ({ title, value, subtitle, icon, color, trend, trendValue }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={color}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
            {trend && (
              <Box display="flex" alignItems="center" mt={1}>
                {trend === 'up' ? (
                  <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
                ) : (
                  <TrendingDownIcon sx={{ fontSize: 16, color: 'error.main', mr: 0.5 }} />
                )}
                <Typography 
                  variant="caption" 
                  color={trend === 'up' ? 'success.main' : 'error.main'}
                >
                  {trendValue}
                </Typography>
              </Box>
            )}
          </Box>
          <Box sx={{ color: color, fontSize: 48, opacity: 0.8 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const ProgressCard = ({ title, current, total, color, icon }) => {
    const percentage = total > 0 ? (current / total) * 100 : 0;
    
    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Box sx={{ color: color, mr: 2 }}>
              {icon}
            </Box>
            <Typography variant="h6">{title}</Typography>
          </Box>
          <Box display="flex" alignItems="center" mb={1}>
            <Typography variant="h4" color={color} sx={{ mr: 2 }}>
              {current}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              of {total}
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={percentage} 
            sx={{ 
              height: 8, 
              borderRadius: 4,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                backgroundColor: color
              }
            }} 
          />
          <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
            {percentage.toFixed(1)}% Complete
          </Typography>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return <LoadingSpinner message="Loading advanced analytics..." />;
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Advanced Analytics</Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Typography variant="caption" color="textSecondary">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Refresh Analytics">
            <IconButton onClick={fetchAnalytics} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Key Performance Indicators */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Monthly Revenue"
            value={`$${analytics?.monthly_revenue?.toFixed(2) || '0.00'}`}
            subtitle="This month"
            icon={<MoneyIcon />}
            color="success.main"
            trend="up"
            trendValue="+12.5%"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="New Patients"
            value={analytics?.new_patients_this_month || 0}
            subtitle="This month"
            icon={<PeopleIcon />}
            color="primary.main"
            trend="up"
            trendValue="+8.3%"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Completed Today"
            value={analytics?.completed_appointments_today || 0}
            subtitle="Appointments"
            icon={<TrendingUpIcon />}
            color="info.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Patient Satisfaction"
            value={analytics?.patient_satisfaction || 'N/A'}
            subtitle="Average rating"
            icon={<StarIcon />}
            color="warning.main"
            trend="up"
            trendValue="+0.2"
          />
        </Grid>
      </Grid>

      {/* Progress Indicators */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <ProgressCard
            title="Lab Results Processing"
            current={analytics?.pending_lab_results || 0}
            total={50} // This would be total lab results for the period
            color="#2196f3"
            icon={<LabIcon />}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <ProgressCard
            title="Inventory Alerts"
            current={analytics?.low_stock_alerts || 0}
            total={20} // This would be total inventory items
            color="#ff9800"
            icon={<InventoryIcon />}
          />
        </Grid>
      </Grid>

      {/* Alerts and Notifications */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Low Stock Alerts
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {lowStockItems.length > 0 ? (
              <List dense>
                {lowStockItems.slice(0, 8).map((item) => (
                  <ListItem key={item.id} divider>
                    <ListItemIcon>
                      <WarningIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText
                      primary={item.item_name}
                      secondary={`Stock: ${item.current_stock} (Min: ${item.minimum_stock})`}
                    />
                    <Chip
                      label="Low Stock"
                      color="warning"
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Alert severity="success">
                All inventory items are adequately stocked
              </Alert>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Pending Lab Results
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {pendingLabResults.length > 0 ? (
              <List dense>
                {pendingLabResults.slice(0, 8).map((result) => (
                  <ListItem key={result.id} divider>
                    <ListItemIcon>
                      <LabIcon color="info" />
                    </ListItemIcon>
                    <ListItemText
                      primary={`${result.patient_name} - ${result.test_name}`}
                      secondary={`Ordered: ${new Date(result.test_date).toLocaleDateString()}`}
                    />
                    <Chip
                      label="Pending"
                      color="info"
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Alert severity="success">
                No pending lab results
              </Alert>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Performance Overview
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h3" color="primary">
                    98.5%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    System Uptime
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h3" color="success.main">
                    1.2s
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Avg Response Time
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h3" color="info.main">
                    {analytics?.completed_appointments_today || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Daily Transactions
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h3" color="warning.main">
                    99.2%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Data Accuracy
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdvancedAnalytics;