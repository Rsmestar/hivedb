import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Container, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';

const CreateCell = () => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { createCell } = useAuth();

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
    
    setError('');
    setLoading(true);
    
    try {
      // إنشاء خلية جديدة
      const success = await createCell(password);
      
      if (success) {
        // التوجيه إلى صفحة الخلية
        navigate(`/cell/${success.cellKey}`);
      } else {
        setError('حدث خطأ أثناء إنشاء الخلية. يرجى المحاولة مرة أخرى.');
      }
    } catch (err) {
      setError('حدث خطأ أثناء إنشاء الخلية. يرجى المحاولة مرة أخرى.');
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
            إنشاء خلية جديدة
          </Typography>
          
          <Typography variant="body1" paragraph align="center">
            أدخل كلمة مرور قوية لخليتك الجديدة.
            لا تحتاج إلى بريد إلكتروني أو اسم مستخدم!
          </Typography>
          
          <Box component="form" className="auth-form" onSubmit={handleSubmit}>
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
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="confirmPassword"
              label="تأكيد كلمة المرور"
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
              {loading ? <CircularProgress size={24} /> : 'إنشاء الخلية'}
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

export default CreateCell;
