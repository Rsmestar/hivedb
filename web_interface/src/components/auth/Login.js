import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Alert, 
  CircularProgress,
  Link
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../services/AuthContext';
import HexLogo from '../HexLogo';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      
      // تسجيل الدخول
      await login(email, password);
      
      // التوجيه إلى لوحة التحكم
      navigate('/dashboard');
    } catch (err) {
      console.error('خطأ في تسجيل الدخول:', err);
      setError(err.response?.data?.detail || 'بريد إلكتروني أو كلمة مرور غير صحيحة');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          mt: 8
        }}
      >
        <Box sx={{ width: 80, height: 80, mb: 2 }}>
          <HexLogo size={80} />
        </Box>
        
        <Typography component="h1" variant="h4" gutterBottom>
          تسجيل الدخول
        </Typography>
        
        <Paper
          elevation={3}
          sx={{
            p: 4,
            width: '100%',
            mt: 2,
            borderRadius: 2
          }}
        >
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              label="البريد الإلكتروني"
              variant="outlined"
              fullWidth
              margin="normal"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
            
            <TextField
              label="كلمة المرور"
              variant="outlined"
              fullWidth
              margin="normal"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'تسجيل الدخول'}
            </Button>
            
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Typography variant="body2">
                ليس لديك حساب؟{' '}
                <Link href="/register" underline="hover">
                  إنشاء حساب جديد
                </Link>
              </Typography>
            </Box>
            
            <Box sx={{ mt: 1, textAlign: 'center' }}>
              <Typography variant="body2">
                <Link href="/forgot-password" underline="hover">
                  نسيت كلمة المرور؟
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;
