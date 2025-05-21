import React from 'react';
import { Box, Button, Typography, Container, Paper, Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';

const HomePage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, currentCell } = useAuth();

  return (
    <Box sx={{ minHeight: '100vh', py: 4 }}>
      <Container maxWidth="lg">
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Typography variant="h3" component="h1" gutterBottom>
              🐝 HiveDB
            </Typography>
            <Typography variant="h5" component="h2" gutterBottom>
              نظام قواعد بيانات ثوري مستوحى من خلية النحل
            </Typography>
          </Box>

          <Grid container spacing={4} justifyContent="center" sx={{ mb: 6 }}>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  ⚡ سريع وبسيط
                </Typography>
                <Typography>
                  إنشاء خلية بيانات خاصة بك في 3 ثوانٍ فقط، دون الحاجة إلى تسجيل حساب.
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  🔒 آمن تمامًا
                </Typography>
                <Typography>
                  بياناتك مشفرة بتقنيات متقدمة، ولا يمكن الوصول إليها إلا بكلمة المرور الخاصة بك.
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  🌐 سهل الاستخدام
                </Typography>
                <Typography>
                  واجهة رسومية سهلة الاستخدام، وواجهة برمجية بسيطة للمطورين.
                </Typography>
              </Box>
            </Grid>
          </Grid>

          <Box sx={{ textAlign: 'center', mb: 4 }}>
            {isAuthenticated ? (
              <Button
                variant="contained"
                size="large"
                color="primary"
                onClick={() => navigate(`/cell/${currentCell.key}`)}
                sx={{ mx: 1, minWidth: 200 }}
              >
                الذهاب إلى خليتي
              </Button>
            ) : (
              <>
                <Button
                  variant="contained"
                  size="large"
                  color="primary"
                  onClick={() => navigate('/create')}
                  sx={{ mx: 1, minWidth: 200 }}
                >
                  إنشاء خلية جديدة
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  color="primary"
                  onClick={() => navigate('/login')}
                  sx={{ mx: 1, minWidth: 200 }}
                >
                  الدخول إلى خلية موجودة
                </Button>
              </>
            )}
          </Box>

          <Box sx={{ mt: 8, p: 3, bgcolor: '#f8f8f8', borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              كيف يعمل HiveDB؟
            </Typography>
            <Typography paragraph>
              1. <strong>أنشئ خلية</strong> - أدخل كلمة مرور فقط واحصل على مفتاح خلية فريد.
            </Typography>
            <Typography paragraph>
              2. <strong>خزّن بياناتك</strong> - استخدم الواجهة الرسومية أو مكتبة Python لتخزين البيانات في خليتك.
            </Typography>
            <Typography paragraph>
              3. <strong>شارك خليتك</strong> - أرسل مفتاح الخلية وكلمة المرور لمن تريد مشاركته.
            </Typography>

            <Box sx={{ mt: 2, p: 2, bgcolor: '#f0f0f0', borderRadius: 1 }}>
              <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', direction: 'ltr', textAlign: 'left' }}>
{`# مثال بسيط باستخدام Python
import hivedb

# الاتصال بالخلية
my_cell = hivedb.connect(
  cell_key="cell1024563254136",
  password="IloveBees123"
)

# تخزين بيانات
my_cell.store("cat_name", "Whiskers")

# جلب البيانات
print(my_cell.get("cat_name"))  # يُعطي: Whiskers`}
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default HomePage;
