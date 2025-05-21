import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Grid, 
  Paper, 
  Typography, 
  Button, 
  CircularProgress,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Divider,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../services/AuthContext';
import Navbar from '../Navbar';
import HexDataDisplay from '../HexDataDisplay';
import AddIcon from '@mui/icons-material/Add';
import StorageIcon from '@mui/icons-material/Storage';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DeleteIcon from '@mui/icons-material/Delete';
import SecurityIcon from '@mui/icons-material/Security';
import { getCellKeys } from '../../services/api';

const Dashboard = ({ darkMode, toggleDarkMode }) => {
  const { currentUser, isAuthenticated, createCell, getUserCells } = useAuth();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [cells, setCells] = useState([]);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [selectedCell, setSelectedCell] = useState(null);
  const [newCellPassword, setNewCellPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [cellStats, setCellStats] = useState({});
  
  // التحقق من المصادقة
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);
  
  // تحميل الخلايا
  useEffect(() => {
    const loadCells = async () => {
      if (!isAuthenticated) return;
      
      try {
        setLoading(true);
        const userCells = await getUserCells();
        setCells(userCells);
        
        // تحميل إحصائيات الخلايا
        const stats = {};
        for (const cell of userCells) {
          try {
            const keys = await getCellKeys(cell.key);
            stats[cell.key] = {
              itemCount: keys.length,
              lastUpdated: cell.updated_at
            };
          } catch (err) {
            console.error(`خطأ في تحميل إحصائيات الخلية ${cell.key}:`, err);
          }
        }
        
        setCellStats(stats);
      } catch (err) {
        console.error('خطأ في تحميل الخلايا:', err);
        setError('حدث خطأ أثناء تحميل الخلايا');
      } finally {
        setLoading(false);
      }
    };
    
    loadCells();
  }, [isAuthenticated, getUserCells]);
  
  // إنشاء خلية جديدة
  const handleCreateCell = async () => {
    // التحقق من تطابق كلمات المرور
    if (newCellPassword !== confirmPassword) {
      setError('كلمات المرور غير متطابقة');
      return;
    }
    
    // التحقق من طول كلمة المرور
    if (newCellPassword.length < 8) {
      setError('يجب أن تكون كلمة المرور 8 أحرف على الأقل');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      // إنشاء خلية جديدة
      const newCell = await createCell(newCellPassword);
      
      // إضافة الخلية الجديدة إلى القائمة
      setCells([...cells, newCell]);
      
      // إغلاق مربع الحوار
      setOpenCreateDialog(false);
      setNewCellPassword('');
      setConfirmPassword('');
      
      // التوجيه إلى الخلية الجديدة
      navigate(`/cell/${newCell.key}`);
    } catch (err) {
      console.error('خطأ في إنشاء الخلية:', err);
      setError(err.response?.data?.detail || 'حدث خطأ أثناء إنشاء الخلية');
    } finally {
      setLoading(false);
    }
  };
  
  // حذف خلية
  const handleDeleteCell = async () => {
    if (!selectedCell) return;
    
    try {
      setLoading(true);
      
      // حذف الخلية (يجب إضافة هذه الوظيفة إلى AuthContext)
      // await deleteCell(selectedCell.key);
      
      // تحديث قائمة الخلايا
      setCells(cells.filter(cell => cell.key !== selectedCell.key));
      
      // إغلاق مربع الحوار
      setOpenDeleteDialog(false);
      setSelectedCell(null);
    } catch (err) {
      console.error('خطأ في حذف الخلية:', err);
      setError(err.response?.data?.detail || 'حدث خطأ أثناء حذف الخلية');
    } finally {
      setLoading(false);
    }
  };
  
  // فتح خلية
  const handleOpenCell = (cell) => {
    navigate(`/cell/${cell.key}`);
  };
  
  if (loading && cells.length === 0) {
    return (
      <Box>
        <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} isAdmin={currentUser?.is_admin} />
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
          <CircularProgress size={60} thickness={4} />
        </Box>
      </Box>
    );
  }
  
  return (
    <Box>
      <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} isAdmin={currentUser?.is_admin} />
      
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Grid container spacing={3}>
          {/* ترحيب */}
          <Grid item xs={12}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 2
              }}
            >
              <Typography variant="h4" gutterBottom>
                مرحباً، {currentUser?.username}
              </Typography>
              <Typography variant="body1">
                مرحباً بك في لوحة تحكم HiveDB. يمكنك إدارة خلاياك وإنشاء خلايا جديدة من هنا.
              </Typography>
            </Paper>
          </Grid>
          
          {/* إحصائيات */}
          <Grid item xs={12} md={4}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                height: 200,
                borderRadius: 2,
                bgcolor: (theme) => theme.palette.primary.main,
                color: 'white'
              }}
            >
              <Typography variant="h6" gutterBottom>
                إجمالي الخلايا
              </Typography>
              <Typography variant="h3" sx={{ my: 2, fontWeight: 'bold' }}>
                {cells.length}
              </Typography>
              <Typography variant="body2">
                يمكنك إنشاء وإدارة خلايا البيانات الخاصة بك
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                height: 200,
                borderRadius: 2,
                bgcolor: (theme) => theme.palette.secondary.main,
                color: 'white'
              }}
            >
              <Typography variant="h6" gutterBottom>
                إجمالي عناصر البيانات
              </Typography>
              <Typography variant="h3" sx={{ my: 2, fontWeight: 'bold' }}>
                {Object.values(cellStats).reduce((total, stat) => total + (stat.itemCount || 0), 0)}
              </Typography>
              <Typography variant="body2">
                مجموع عناصر البيانات في جميع الخلايا
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                height: 200,
                borderRadius: 2,
                bgcolor: (theme) => theme.palette.success.main,
                color: 'white'
              }}
            >
              <Typography variant="h6" gutterBottom>
                الأمان
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', my: 2 }}>
                <SecurityIcon sx={{ fontSize: 40, mr: 2 }} />
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  محمي
                </Typography>
              </Box>
              <Typography variant="body2">
                جميع بياناتك محمية بتشفير قوي ومصادقة آمنة
              </Typography>
            </Paper>
          </Grid>
          
          {/* زر إنشاء خلية جديدة */}
          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              size="large"
              onClick={() => setOpenCreateDialog(true)}
              sx={{ mb: 3 }}
            >
              إنشاء خلية جديدة
            </Button>
          </Grid>
          
          {/* قائمة الخلايا */}
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              الخلايا الخاصة بك
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            {cells.length === 0 ? (
              <Paper
                elevation={2}
                sx={{
                  p: 4,
                  textAlign: 'center',
                  borderRadius: 2
                }}
              >
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  لا توجد خلايا
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  قم بإنشاء خلية جديدة للبدء في تخزين البيانات
                </Typography>
              </Paper>
            ) : (
              <Box sx={{ mt: 3, mb: 5 }}>
                {/* عرض الخلايا بشكل سداسي */}
                <HexDataDisplay 
                  data={cells.map(cell => ({
                    key: cell.key,
                    value: cellStats[cell.key]?.itemCount || 0,
                    type: 'cell',
                    created_at: cell.created_at,
                    // إضافة البيانات الكاملة للخلية لاستخدامها في النقر
                    fullData: cell
                  }))}
                  loading={loading}
                  onItemClick={(item) => {
                    if (item.fullData) {
                      handleOpenCell(item.fullData);
                    }
                  }}
                />
                
                {/* أزرار الإجراءات السريعة */}
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3, gap: 2 }}>
                  <Button
                    variant="outlined"
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => setOpenCreateDialog(true)}
                  >
                    إنشاء خلية جديدة
                  </Button>
                  
                  {cells.length > 0 && (
                    <Button
                      variant="outlined"
                      color="secondary"
                      startIcon={<VisibilityIcon />}
                      onClick={() => handleOpenCell(cells[0])}
                    >
                      فتح آخر خلية
                    </Button>
                  )}
                </Box>
              </Box>
            )}
          </Grid>
        </Grid>
      </Container>
      
      {/* مربع حوار إنشاء خلية جديدة */}
      <Dialog
        open={openCreateDialog}
        onClose={() => setOpenCreateDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>إنشاء خلية جديدة</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <Typography variant="body2" paragraph sx={{ mt: 1 }}>
            أدخل كلمة مرور لحماية الخلية الجديدة. ستحتاج إلى هذه الكلمة للوصول إلى بياناتك.
          </Typography>
          
          <TextField
            autoFocus
            margin="dense"
            label="كلمة المرور"
            type="password"
            fullWidth
            variant="outlined"
            value={newCellPassword}
            onChange={(e) => setNewCellPassword(e.target.value)}
            required
            helperText="يجب أن تكون كلمة المرور 8 أحرف على الأقل"
          />
          
          <TextField
            margin="dense"
            label="تأكيد كلمة المرور"
            type="password"
            fullWidth
            variant="outlined"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreateDialog(false)}>إلغاء</Button>
          <Button 
            onClick={handleCreateCell} 
            variant="contained" 
            color="primary"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'إنشاء خلية'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* مربع حوار حذف خلية */}
      <Dialog
        open={openDeleteDialog}
        onClose={() => setOpenDeleteDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>حذف الخلية</DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            هل أنت متأكد من رغبتك في حذف الخلية <strong>{selectedCell?.key}</strong>؟
          </Typography>
          <Typography variant="body2" color="error">
            تحذير: سيتم حذف جميع البيانات المخزنة في هذه الخلية بشكل نهائي ولا يمكن استعادتها.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)}>إلغاء</Button>
          <Button 
            onClick={handleDeleteCell} 
            variant="contained" 
            color="error"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'حذف'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Dashboard;
