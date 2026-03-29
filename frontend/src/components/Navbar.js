import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Divider,
  Box,
  Typography,
  Button
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  LocalHospital as DoctorIcon,
  Event as AppointmentIcon,
  Description as MedicalIcon,
  PersonAdd as UserIcon,
  Logout as LogoutIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const drawerWidth = 240;

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Patients', icon: <PeopleIcon />, path: '/patients' },
    { text: 'Doctors', icon: <DoctorIcon />, path: '/doctors' },
    { text: 'Appointments', icon: <AppointmentIcon />, path: '/appointments' },
    { text: 'Medical Records', icon: <MedicalIcon />, path: '/medical-records' },
  ];

  if (user?.role === 'admin') {
    menuItems.push({ text: 'User Management', icon: <UserIcon />, path: '/users' });
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Hospital MS
        </Typography>
      </Toolbar>
      <Divider />

      <Box sx={{ overflow: 'auto', flexGrow: 1 }}>
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
              >
                <ListItemIcon>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      <Divider />
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Logged in as: {user?.username}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Role: {user?.role}
        </Typography>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<LogoutIcon />}
          onClick={handleLogout}
          sx={{ mt: 2 }}
        >
          Logout
        </Button>
      </Box>
    </Drawer>
  );
};

export default Navbar;
