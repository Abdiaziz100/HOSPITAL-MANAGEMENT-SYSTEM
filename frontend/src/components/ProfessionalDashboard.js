import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  People as PeopleIcon,
  Event as EventIcon,
  LocalHospital as DoctorIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import axios from 'axios';
import { CardSkeleton } from './LoadingComponents';
import { useNotification } from '../contexts/NotificationContext';

const ProfessionalDashboard = () => {
  const [overviewData, setOverviewData] = useState(null);
  const [recentActivities, setRecentActivities] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const { showError } = useNotification();

  const fetchDashboardData = useCallback(async () => {
    try {
      const [overviewRes, activitiesRes] = await Promise.all([
        axios.get('/api/dashboard/overview'),
        axios.get('/api/dashboard/recent-activities')
      ]);

      setOverviewData(overviewRes.data);
      setRecentActivities(activitiesRes.data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      showError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  const StatCard = ({ title, value, icon, color, subtitle, trend }) => (
    <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h3" component="div" color={color}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{ color: color, fontSize: 48, opacity: 0.8 }}>
            {icon}
          </Box>
        </Box>
        {trend && (
          <Box display="flex" alignItems="center" mt={1}>
            <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
            <Typography variant="caption" color="success.main">
              {trend}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'primary';
      case 'completed': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((item) => (
            <Grid item xs={12} sm={6} md={3} key={item}>
              <Card><CardSkeleton /></Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Dashboard
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Typography variant="caption" color="textSecondary">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Refresh Data">
            <IconButton onClick={fetchDashboardData} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Patients"
            value={overviewData?.total_patients || 0}
            icon={<PeopleIcon />}
            color="primary.main"
            subtitle="Registered patients"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Appointments"
            value={overviewData?.todays_appointments || 0}
            icon={<EventIcon />}
            color="info.main"
            subtitle="Scheduled for today"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Doctors"
            value={overviewData?.active_doctors || 0}
            icon={<DoctorIcon />}
            color="success.main"
            subtitle="Available doctors"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed Today"
            value={overviewData?.completed_today || 0}
            icon={<CheckCircleIcon />}
            color="warning.main"
            subtitle="Appointments completed"
          />
        </Grid>
      </Grid>

      {/* Recent Activities */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Recent Appointments
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {recentActivities?.recent_appointments?.length > 0 ? (
              <List dense>
                {recentActivities.recent_appointments.map((appointment) => (
                  <ListItem key={appointment.id} divider>
                    <ListItemIcon>
                      <ScheduleIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={`${appointment.patient_name} → ${appointment.doctor_name}`}
                      secondary={new Date(appointment.date).toLocaleString()}
                    />
                    <Chip
                      label={appointment.status}
                      color={getStatusColor(appointment.status)}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="textSecondary" align="center" sx={{ py: 4 }}>
                No recent appointments
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Recently Registered Patients
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {recentActivities?.recent_patients?.length > 0 ? (
              <List dense>
                {recentActivities.recent_patients.map((patient) => (
                  <ListItem key={patient.id} divider>
                    <ListItemIcon>
                      <PeopleIcon color="secondary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={patient.name}
                      secondary={`ID: ${patient.patient_id} • ${new Date(patient.created_at).toLocaleDateString()}`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="textSecondary" align="center" sx={{ py: 4 }}>
                No recent patient registrations
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProfessionalDashboard;