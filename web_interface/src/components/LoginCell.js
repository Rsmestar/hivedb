import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Container, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';

const LoginCell = () => {
  const [cellKey, setCellKey] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { loginCell } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // التحقق من إدخال مفتاح الخلية
    if (!cellKey) {
      setError('يرجى إدخال مفتاح الخلية');
      return;
    }
    
    // التحقق من إدخال كلمة المرور
    if (!password) {
      setError('يرجى إدخال كلمة المرور');
      return;
    }
    
    setError('');
    setLoading(true);
    
    try {
      // تسجيل الدخول إلى الخلية
      const success = await loginCell(cellKey, password);
      
      if (success) {
        // التوجيه إلى صفحة الخلية
        navigate(`/cell/${cellKey}`);
      } else {
        setError('مفتاح الخلية أو كلمة المرور غير صحيحة');
      }
    } catch (err) {
      setError('حدث خطأ أثناء تسجيل الدخول. يرجى المحاولة مرة أخرى.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box className="auth-container">
        <Paper elevation={3} className="auth-paper">
          <Typography variant="h4" component="h1" gutterBottom align="center">
            الدخول إلى خلية
          </Typography>
          
          <Typography variant="body1" paragraph align="center">
            أدخل مفتاح الخلية وكلمة المرور للوصول إلى بياناتك.
          </Typography>
          
          <Box component="form" className="auth-form" onSubmit={handleSubmit}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="cellKey"
              label="مفتاح الخلية"
              name="cellKey"
              autoComplete="off"
              value={cellKey}
              onChange={(e) => setCellKey(e.target.value)}
              disabled={loading}
              placeholder="مثال: cell1024563254136"
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="كلمة المرور"
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              error={!!error}
              helperText={error}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              className="auth-submit"
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'دخول'}
            </Button>
            
            <Button
              fullWidth
              variant="text"
              color="primary"
              onClick={() => navigate('/')}
              sx={{ mt: 2 }}
              disabled={loading}
            >
              العودة للصفحة الرئيسية
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginCell;
