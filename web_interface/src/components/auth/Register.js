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

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // التحقق من تطابق كلمات المرور
    if (password !== confirmPassword) {
      setError('كلمات المرور غير متطابقة');
      return;
    }
    
    // التحقق من طول كلمة المرور
    if (password.length < 8) {
      setError('يجب أن تكون كلمة المرور 8 أحرف على الأقل');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      // تسجيل المستخدم الجديد
      await register(username, email, password);
      
      // التوجيه إلى صفحة تسجيل الدخول
      navigate('/login');
    } catch (err) {
      console.error('خطأ في التسجيل:', err);
      setError(err.response?.data?.detail || 'حدث خطأ أثناء التسجيل');
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
          إنشاء حساب جديد
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
              label="اسم المستخدم"
              variant="outlined"
              fullWidth
              margin="normal"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
            
            <TextField
              label="البريد الإلكتروني"
              variant="outlined"
              fullWidth
              margin="normal"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
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
              helperText="يجب أن تكون كلمة المرور 8 أحرف على الأقل"
            />
            
            <TextField
              label="تأكيد كلمة المرور"
              variant="outlined"
              fullWidth
              margin="normal"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
              {loading ? <CircularProgress size={24} /> : 'إنشاء حساب'}
            </Button>
            
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Typography variant="body2">
                لديك حساب بالفعل؟{' '}
                <Link href="/login" underline="hover">
                  تسجيل الدخول
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Register;
