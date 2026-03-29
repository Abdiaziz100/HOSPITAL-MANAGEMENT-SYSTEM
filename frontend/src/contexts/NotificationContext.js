import React, { createContext, useContext, useState } from 'react';
import { Snackbar, Alert, Slide } from '@mui/material';

const NotificationContext = createContext();

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider');
  }
  return context;
};

function SlideTransition(props) {
  return <Slide {...props} direction="up" />;
}

export const NotificationProvider = ({ children }) => {
  const [notification, setNotification] = useState({
    open: false,
    message: '',
    severity: 'info',
    autoHideDuration: 6000
  });

  const showNotification = (message, severity = 'info', autoHideDuration = 6000) => {
    setNotification({
      open: true,
      message,
      severity,
      autoHideDuration
    });
  };

  const hideNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  const showSuccess = (message) => showNotification(message, 'success');
  const showError = (message) => showNotification(message, 'error', 8000);
  const showWarning = (message) => showNotification(message, 'warning');
  const showInfo = (message) => showNotification(message, 'info');

  return (
    <NotificationContext.Provider value={{
      showNotification,
      showSuccess,
      showError,
      showWarning,
      showInfo
    }}>
      {children}
      <Snackbar
        open={notification.open}
        autoHideDuration={notification.autoHideDuration}
        onClose={hideNotification}
        TransitionComponent={SlideTransition}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={hideNotification}
          severity={notification.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </NotificationContext.Provider>
  );
};