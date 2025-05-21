import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Snackbar,
  Card,
  CardContent,
  CircularProgress,
  InputAdornment,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import SecurityIcon from '@mui/icons-material/Security';
import StorageIcon from '@mui/icons-material/Storage';
import SpeedIcon from '@mui/icons-material/Speed';
import BackupIcon from '@mui/icons-material/Backup';

// محاكاة جلب إعدادات النظام
const fetchSettings = async () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        security: {
          passwordMinLength: 8,
          sessionTimeout: 30, // بالدقائق
          maxLoginAttempts: 5,
          enforceStrongPasswords: true,
          enableTwoFactorAuth: false
        },
        storage: {
          maxCellSize: 100, // بالميجابايت
          compressionLevel: 'medium',
          backupFrequency: 'daily',
          retentionPeriod: 30 // بالأيام
        },
        performance: {
          cacheSize: 50, // بالميجابايت
          maxConcurrentConnections: 100,
          queryTimeout: 15, // بالثواني
          enableIndexing: true
        }
      });
    }, 1000);
  });
};

// محاكاة حفظ الإعدادات
const saveSettings = async (settings) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      console.log('تم حفظ الإعدادات:', settings);
      resolve({ success: true });
    }, 1500);
  });
};

const AdminSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    const getSettings = async () => {
      try {
        setLoading(true);
        const data = await fetchSettings();
        setSettings(data);
      } catch (error) {
        console.error('خطأ في جلب إعدادات النظام:', error);
        setSnackbar({
          open: true,
          message: 'حدث خطأ أثناء جلب الإعدادات',
          severity: 'error'
        });
      } finally {
        setLoading(false);
      }
    };

    getSettings();
  }, []);

  const handleSettingChange = (category, setting, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value
      }
    }));
  };

  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      const result = await saveSettings(settings);
      if (result.success) {
        setSnackbar({
          open: true,
          message: 'تم حفظ الإعدادات بنجاح',
          severity: 'success'
        });
      }
    } catch (error) {
      console.error('خطأ في حفظ الإعدادات:', error);
      setSnackbar({
        open: true,
        message: 'حدث خطأ أثناء حفظ الإعدادات',
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress size={60} thickness={4} />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">
          إعدادات النظام
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
          disabled={saving}
        >
          {saving ? 'جاري الحفظ...' : 'حفظ الإعدادات'}
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* إعدادات الأمان */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SecurityIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">إعدادات الأمان</Typography>
              </Box>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    label="الحد الأدنى لطول كلمة المرور"
                    type="number"
                    fullWidth
                    value={settings.security.passwordMinLength}
                    onChange={(e) => handleSettingChange('security', 'passwordMinLength', parseInt(e.target.value))}
                    InputProps={{
                      inputProps: { min: 6, max: 20 }
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    label="مهلة انتهاء الجلسة (بالدقائق)"
                    type="number"
                    fullWidth
                    value={settings.security.sessionTimeout}
                    onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value))}
                    InputProps={{
                      inputProps: { min: 5, max: 120 }
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    label="الحد الأقصى لمحاولات تسجيل الدخول"
                    type="number"
                    fullWidth
                    value={settings.security.maxLoginAttempts}
                    onChange={(e) => handleSettingChange('security', 'maxLoginAttempts', parseInt(e.target.value))}
                    InputProps={{
                      inputProps: { min: 3, max: 10 }
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security.enforceStrongPasswords}
                        onChange={(e) => handleSettingChange('security', 'enforceStrongPasswords', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="فرض كلمات مرور قوية"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security.enableTwoFactorAuth}
                        onChange={(e) => handleSettingChange('security', 'enableTwoFactorAuth', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="تفعيل المصادقة الثنائية"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* إعدادات التخزين */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <StorageIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">إعدادات التخزين</Typography>
              </Box>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography gutterBottom>الحد الأقصى لحجم الخلية (بالميجابايت)</Typography>
                  <Slider
                    value={settings.storage.maxCellSize}
                    onChange={(e, newValue) => handleSettingChange('storage', 'maxCellSize', newValue)}
                    aria-labelledby="max-cell-size-slider"
                    valueLabelDisplay="auto"
                    step={10}
                    marks
                    min={10}
                    max={500}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>مستوى الضغط</InputLabel>
                    <Select
                      value={settings.storage.compressionLevel}
                      onChange={(e) => handleSettingChange('storage', 'compressionLevel', e.target.value)}
                      label="مستوى الضغط"
                    >
                      <MenuItem value="none">بدون ضغط</MenuItem>
                      <MenuItem value="low">منخفض</MenuItem>
                      <MenuItem value="medium">متوسط</MenuItem>
                      <MenuItem value="high">عالي</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>تكرار النسخ الاحتياطي</InputLabel>
                    <Select
                      value={settings.storage.backupFrequency}
                      onChange={(e) => handleSettingChange('storage', 'backupFrequency', e.target.value)}
                      label="تكرار النسخ الاحتياطي"
                    >
                      <MenuItem value="hourly">كل ساعة</MenuItem>
                      <MenuItem value="daily">يومي</MenuItem>
                      <MenuItem value="weekly">أسبوعي</MenuItem>
                      <MenuItem value="monthly">شهري</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    label="فترة الاحتفاظ بالنسخ الاحتياطية (بالأيام)"
                    type="number"
                    fullWidth
                    value={settings.storage.retentionPeriod}
                    onChange={(e) => handleSettingChange('storage', 'retentionPeriod', parseInt(e.target.value))}
                    InputProps={{
                      inputProps: { min: 1, max: 365 }
                    }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* إعدادات الأداء */}
        <Grid item xs={12}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SpeedIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">إعدادات الأداء</Typography>
              </Box>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography gutterBottom>حجم ذاكرة التخزين المؤقت (بالميجابايت)</Typography>
                  <Slider
                    value={settings.performance.cacheSize}
                    onChange={(e, newValue) => handleSettingChange('performance', 'cacheSize', newValue)}
                    aria-labelledby="cache-size-slider"
                    valueLabelDisplay="auto"
                    step={10}
                    marks
                    min={10}
                    max={200}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    label="الحد الأقصى للاتصالات المتزامنة"
                    type="number"
                    fullWidth
                    value={settings.performance.maxConcurrentConnections}
                    onChange={(e) => handleSettingChange('performance', 'maxConcurrentConnections', parseInt(e.target.value))}
                    InputProps={{
                      inputProps: { min: 10, max: 500 }
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    label="مهلة انتهاء الاستعلام (بالثواني)"
                    type="number"
                    fullWidth
                    value={settings.performance.queryTimeout}
                    onChange={(e) => handleSettingChange('performance', 'queryTimeout', parseInt(e.target.value))}
                    InputProps={{
                      inputProps: { min: 5, max: 60 }
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.performance.enableIndexing}
                        onChange={(e) => handleSettingChange('performance', 'enableIndexing', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="تفعيل الفهرسة التلقائية"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* زر النسخ الاحتياطي */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Button
              variant="outlined"
              color="secondary"
              startIcon={<BackupIcon />}
              size="large"
            >
              إنشاء نسخة احتياطية الآن
            </Button>
          </Box>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AdminSettings;
