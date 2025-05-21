import React, { useState, useEffect } from 'react';
import { Box, Container, CircularProgress, Typography, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';
import Navbar from '../components/Navbar';
import AdminDashboard from '../components/admin/AdminDashboard';

const AdminPage = ({ darkMode, toggleDarkMode }) => {
  const { isAuthenticated, currentCell } = useAuth();
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // التحقق من صلاحيات المسؤول
    const checkAdminAccess = async () => {
      if (!isAuthenticated) {
        navigate('/login');
        return;
      }

      try {
        setLoading(true);
        // هنا يمكن إضافة استدعاء API للتحقق من صلاحيات المسؤول
        // للتبسيط، سنفترض أن المستخدم الحالي هو مسؤول
        setIsAdmin(true);
      } catch (error) {
        console.error('خطأ في التحقق من صلاحيات المسؤول:', error);
        setIsAdmin(false);
        navigate('/');
      } finally {
        setLoading(false);
      }
    };

    checkAdminAccess();
  }, [isAuthenticated, navigate]);

  if (loading) {
    return (
      <Box>
        <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} isAdmin={isAdmin} />
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
          <CircularProgress size={60} thickness={4} />
        </Box>
      </Box>
    );
  }

  if (!isAdmin) {
    return (
      <Box>
        <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        <Container maxWidth="md" sx={{ mt: 8 }}>
          <Paper sx={{ p: 4, textAlign: 'center' }} elevation={3}>
            <Typography variant="h4" color="error" gutterBottom>
              غير مصرح بالوصول
            </Typography>
            <Typography variant="body1">
              ليس لديك صلاحيات كافية للوصول إلى لوحة تحكم المسؤول.
            </Typography>
          </Paper>
        </Container>
      </Box>
    );
  }

  return (
    <Box>
      <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} isAdmin={isAdmin} />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <AdminDashboard />
      </Container>
    </Box>
  );
};

export default AdminPage;
