import React, { useState, useMemo } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Container, CssBaseline, ThemeProvider } from '@mui/material';
import HomePage from './components/HomePage';
import CreateCell from './components/CreateCell';
import CellView from './components/CellView';
import LoginCell from './components/LoginCell';
import Register from './components/auth/Register';
import Login from './components/auth/Login';
import Dashboard from './components/dashboard/Dashboard';
import AdminPage from './pages/AdminPage';
import { AuthProvider, useAuth } from './services/AuthContext';
import { getTheme } from './styles/theme';

function App() {
  const [darkMode, setDarkMode] = useState(false);
  
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };
  
  const theme = useMemo(() => getTheme(darkMode), [darkMode]);
  
  // مكون لحماية المسارات التي تتطلب مصادقة
  const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();
    
    if (loading) {
      return <div>جاري التحميل...</div>;
    }
    
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }
    
    return children;
  };
  
  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>
        <CssBaseline />
        <Container maxWidth={false} disableGutters>
          <Routes>
            {/* المسارات العامة */}
            <Route path="/" element={<HomePage darkMode={darkMode} toggleDarkMode={toggleDarkMode} />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            
            {/* المسارات المحمية */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
              </ProtectedRoute>
            } />
            <Route path="/create" element={
              <ProtectedRoute>
                <CreateCell darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
              </ProtectedRoute>
            } />
            <Route path="/cell/:cellKey" element={
              <ProtectedRoute>
                <CellView darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
              </ProtectedRoute>
            } />
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminPage darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
              </ProtectedRoute>
            } />
            
            {/* مسار غير موجود */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Container>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
