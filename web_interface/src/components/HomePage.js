import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Container, 
  Paper, 
  Grid, 
  Card, 
  CardContent, 
  useTheme,
  useMediaQuery,
  Fade,
  Stack,
  Chip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';
import HexLogo from './HexLogo';

const HomePage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, currentCell } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [loaded, setLoaded] = useState(false);
  
  useEffect(() => {
    setLoaded(true);
  }, []);

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #f5f7fa 0%, #e4efe9 100%)',
      py: 6
    }}>
      <Container maxWidth="lg">
        <Fade in={loaded} timeout={800}>
          <Box>
            <Box sx={{ 
              textAlign: 'center', 
              mb: 8,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <HexLogo size={isMobile ? 150 : 200} animated={true} showText={false} />
              <Typography 
                variant="h4" 
                component="h1" 
                sx={{ 
                  mt: 3, 
                  fontWeight: 700,
                  background: 'linear-gradient(90deg, #3a0ca3 0%, #4361ee 50%, #4cc9f0 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  letterSpacing: '0.05em',
                  fontFamily: '"Poppins", "Tajawal", sans-serif',
                }}
              >
                نظام قواعد بيانات سداسي متطور
              </Typography>
              <Typography 
                variant="h6" 
                sx={{ 
                  mt: 2, 
                  maxWidth: 700,
                  color: 'text.secondary',
                  fontWeight: 400
                }}
              >
                بنية بيانات مبتكرة تتفوق على الأنظمة التقليدية بقدرات فريدة للتخزين والاسترجاع
              </Typography>
              
              <Stack direction="row" spacing={1} sx={{ mt: 3 }}>
                <Chip 
                  label="يتفوق على Directus" 
                  color="primary" 
                  sx={{ fontWeight: 500, backgroundColor: '#4361ee' }} 
                />
                <Chip 
                  label="واجهة عربية" 
                  color="secondary" 
                  sx={{ fontWeight: 500, backgroundColor: '#3a0ca3', color: 'white' }} 
                />
                <Chip 
                  label="أداء عالي" 
                  sx={{ fontWeight: 500, backgroundColor: '#4cc9f0', color: 'white' }} 
                />
              </Stack>
            </Box>

            <Grid container spacing={4} justifyContent="center" sx={{ mb: 6 }}>
              <Grid item xs={12} md={4}>
                <Card elevation={3} sx={{ 
                  height: '100%', 
                  borderRadius: 3, 
                  transition: 'transform 0.3s, box-shadow 0.3s',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 20px rgba(0,0,0,0.1)'
                  }
                }}>
                  <CardContent sx={{ p: 4, textAlign: 'center' }}>
                    <Box sx={{ 
                      mb: 2, 
                      width: 60, 
                      height: 60, 
                      borderRadius: '50%', 
                      background: 'linear-gradient(135deg, #4cc9f0 0%, #3a86ff 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: '0 auto',
                      color: 'white',
                      fontSize: '24px'
                    }}>
                      ⚡
                    </Box>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                      سريع وفعال
                    </Typography>
                    <Typography sx={{ color: 'text.secondary' }}>
                      إنشاء وإدارة البيانات بسرعة فائقة بفضل البنية السداسية المبتكرة والتخزين المؤقت السائل
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card elevation={3} sx={{ 
                  height: '100%', 
                  borderRadius: 3, 
                  transition: 'transform 0.3s, box-shadow 0.3s',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 20px rgba(0,0,0,0.1)'
                  }
                }}>
                  <CardContent sx={{ p: 4, textAlign: 'center' }}>
                    <Box sx={{ 
                      mb: 2, 
                      width: 60, 
                      height: 60, 
                      borderRadius: '50%', 
                      background: 'linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: '0 auto',
                      color: 'white',
                      fontSize: '24px'
                    }}>
                      🔒
                    </Box>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                      أمان متقدم
                    </Typography>
                    <Typography sx={{ color: 'text.secondary' }}>
                      حماية البيانات بتقنيات تشفير متطورة مع نظام صلاحيات دقيق وسجل تدقيق شامل
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card elevation={3} sx={{ 
                  height: '100%', 
                  borderRadius: 3, 
                  transition: 'transform 0.3s, box-shadow 0.3s',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 20px rgba(0,0,0,0.1)'
                  }
                }}>
                  <CardContent sx={{ p: 4, textAlign: 'center' }}>
                    <Box sx={{ 
                      mb: 2, 
                      width: 60, 
                      height: 60, 
                      borderRadius: '50%', 
                      background: 'linear-gradient(135deg, #480ca8 0%, #4cc9f0 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: '0 auto',
                      color: 'white',
                      fontSize: '24px'
                    }}>
                      🌐
                    </Box>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                      تحليلات متقدمة
                    </Typography>
                    <Typography sx={{ color: 'text.secondary' }}>
                      رؤى تحليلية متطورة لبياناتك مع قدرات استعلام متقدمة تتفوق على الأنظمة التقليدية
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Box sx={{ textAlign: 'center', mb: 6 }}>
              {isAuthenticated ? (
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate(`/cell/${currentCell.key}`)}
                  sx={{ 
                    mx: 1, 
                    minWidth: 220,
                    py: 1.5,
                    px: 4,
                    borderRadius: 2,
                    fontWeight: 600,
                    boxShadow: '0 8px 16px rgba(67, 97, 238, 0.3)',
                    background: 'linear-gradient(90deg, #3a0ca3 0%, #4361ee 100%)',
                    '&:hover': {
                      boxShadow: '0 12px 20px rgba(67, 97, 238, 0.4)',
                    }
                  }}
                >
                  الذهاب إلى لوحة التحكم
                </Button>
              ) : (
                <Stack 
                  direction={isMobile ? 'column' : 'row'} 
                  spacing={isMobile ? 2 : 3} 
                  justifyContent="center"
                >
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => navigate('/create')}
                    sx={{ 
                      minWidth: 220,
                      py: 1.5,
                      px: 4,
                      borderRadius: 2,
                      fontWeight: 600,
                      boxShadow: '0 8px 16px rgba(67, 97, 238, 0.3)',
                      background: 'linear-gradient(90deg, #3a0ca3 0%, #4361ee 100%)',
                      '&:hover': {
                        boxShadow: '0 12px 20px rgba(67, 97, 238, 0.4)',
                      }
                    }}
                  >
                    إنشاء مشروع جديد
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={() => navigate('/login')}
                    sx={{ 
                      minWidth: 220,
                      py: 1.5,
                      px: 4,
                      borderRadius: 2,
                      fontWeight: 600,
                      borderColor: '#4361ee',
                      color: '#4361ee',
                      borderWidth: 2,
                      '&:hover': {
                        borderColor: '#3a0ca3',
                        borderWidth: 2,
                        backgroundColor: 'rgba(67, 97, 238, 0.04)'
                      }
                    }}
                  >
                    تسجيل الدخول
                  </Button>
                </Stack>
              )}
            </Box>

            <Paper elevation={4} sx={{ mt: 8, p: 0, borderRadius: 4, overflow: 'hidden' }}>
              <Box sx={{ 
                p: 4, 
                background: 'linear-gradient(135deg, #3a0ca3 0%, #4361ee 100%)',
                color: 'white'
              }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  كيف يعمل HiveDB؟
                </Typography>
                <Typography sx={{ opacity: 0.9 }}>
                  نظام بيانات سداسي متطور يتفوق على الأنظمة التقليدية
                </Typography>
              </Box>
              
              <Box sx={{ p: 4 }}>
                <Grid container spacing={4}>
                  <Grid item xs={12} md={6}>
                    <Box sx={{ mb: 4 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Box sx={{ 
                          width: 36, 
                          height: 36, 
                          borderRadius: '50%', 
                          background: 'linear-gradient(135deg, #4cc9f0 0%, #3a86ff 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontWeight: 'bold',
                          mr: 2
                        }}>
                          1
                        </Box>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          إنشاء مشروع
                        </Typography>
                      </Box>
                      <Typography sx={{ color: 'text.secondary', pl: 7 }}>
                        أنشئ مشروعًا جديدًا بنقرة واحدة واستفد من البنية السداسية المتطورة لتخزين البيانات بطريقة مبتكرة
                      </Typography>
                    </Box>
                    
                    <Box sx={{ mb: 4 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Box sx={{ 
                          width: 36, 
                          height: 36, 
                          borderRadius: '50%', 
                          background: 'linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontWeight: 'bold',
                          mr: 2
                        }}>
                          2
                        </Box>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          تخزين البيانات
                        </Typography>
                      </Box>
                      <Typography sx={{ color: 'text.secondary', pl: 7 }}>
                        استخدم واجهة المستخدم السداسية المتطورة أو واجهة برمجة التطبيقات RESTful لتخزين واسترجاع البيانات
                      </Typography>
                    </Box>
                    
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Box sx={{ 
                          width: 36, 
                          height: 36, 
                          borderRadius: '50%', 
                          background: 'linear-gradient(135deg, #480ca8 0%, #4cc9f0 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontWeight: 'bold',
                          mr: 2
                        }}>
                          3
                        </Box>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          تحليل واستعلام
                        </Typography>
                      </Box>
                      <Typography sx={{ color: 'text.secondary', pl: 7 }}>
                        استفد من قدرات الاستعلام المتقدمة والتحليلات المتطورة التي تتفوق على الأنظمة التقليدية
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Paper elevation={2} sx={{ p: 3, borderRadius: 2, bgcolor: '#f8f9fa' }}>
                      <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#3a0ca3' }}>
                        مثال للاستخدام مع واجهة برمجة التطبيقات
                      </Typography>
                      <Box sx={{ 
                        p: 2, 
                        bgcolor: '#1e1e1e', 
                        borderRadius: 2,
                        boxShadow: 'inset 0 0 10px rgba(0,0,0,0.2)'
                      }}>
                        <Typography variant="body2" component="pre" sx={{ 
                          fontFamily: '"Fira Code", monospace', 
                          direction: 'ltr', 
                          textAlign: 'left',
                          color: '#e9e9e9',
                          fontSize: '0.85rem',
                          overflow: 'auto'
                        }}>
{`# استخدام HiveDB مع Python
import hivedb

# الاتصال بالمشروع
project = hivedb.connect(
  project_id="hex_1024563254136",
  api_key="sk_hex_a1b2c3d4e5f6"
)

# إنشاء خلية جديدة
cell = project.create_cell(
  coordinates="0,0",
  data_type="json"
)

# تخزين البيانات
cell.store("user_profile", {
  "name": "أحمد",
  "age": 28,
  "interests": ["تقنية", "برمجة", "تحليل البيانات"]
})

# استعلام متقدم
neighbors = project.query.neighbors(
  cell_id=cell.id,
  depth=2,
  direction="north"
)`}
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                </Grid>
              </Box>
            </Paper>
          </Box>
        </Fade>
      </Container>
    </Box>
  );
};

export default HomePage;
