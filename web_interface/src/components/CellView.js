import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, Typography, Paper, Container, CircularProgress, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Snackbar, Alert, Tabs, Tab } from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';
import { getCellKeys, getCellData, storeCellData, deleteCellData } from '../services/api';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import LogoutIcon from '@mui/icons-material/Logout';
import ShareIcon from '@mui/icons-material/Share';
import StorageIcon from '@mui/icons-material/Storage';
import GridViewIcon from '@mui/icons-material/GridView';
import TableViewIcon from '@mui/icons-material/TableView';
import * as THREE from 'three';
import Navbar from './Navbar';
import HexDataDisplay from './HexDataDisplay';

const CellView = ({ darkMode, toggleDarkMode }) => {
  const { cellKey } = useParams();
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [keys, setKeys] = useState([]);
  const [data, setData] = useState({});
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openShareDialog, setOpenShareDialog] = useState(false);
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [viewMode, setViewMode] = useState(0); // 0: عرض سداسي، 1: عرض قائمة
  
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  
  // التحقق من المصادقة
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);
  
  // تحميل بيانات الخلية
  useEffect(() => {
    const loadCellData = async () => {
      if (!isAuthenticated || !cellKey) return;
      
      try {
        setLoading(true);
        setError('');
        
        // الحصول على قائمة المفاتيح
        const keysList = await getCellKeys(cellKey);
        setKeys(keysList);
        
        // الحصول على البيانات لكل مفتاح
        const dataObj = {};
        for (const key of keysList) {
          try {
            const value = await getCellData(cellKey, key);
            dataObj[key] = value;
          } catch (err) {
            console.error(`خطأ في الحصول على بيانات المفتاح ${key}:`, err);
          }
        }
        
        setData(dataObj);
      } catch (err) {
        console.error('خطأ في تحميل بيانات الخلية:', err);
        setError('حدث خطأ أثناء تحميل بيانات الخلية');
      } finally {
        setLoading(false);
      }
    };
    
    loadCellData();
  }, [isAuthenticated, cellKey]);
  
  // إعداد المشهد ثلاثي الأبعاد
  useEffect(() => {
    if (!containerRef.current || loading || keys.length === 0) return;
    
    // إنشاء المشهد
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, containerRef.current.clientWidth / containerRef.current.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    containerRef.current.innerHTML = '';
    containerRef.current.appendChild(renderer.domElement);
    
    // إضافة إضاءة
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0, 10, 10);
    scene.add(directionalLight);
    
    // إنشاء الخلايا السداسية
    const hexagons = [];
    const hexRadius = 1;
    const hexHeight = 0.2;
    const spacing = 2.2;
    
    keys.forEach((key, index) => {
      // حساب موقع الخلية السداسية
      const row = Math.floor(index / 5);
      const col = index % 5;
      const offset = row % 2 === 0 ? 0 : spacing / 2;
      
      const x = (col * spacing) + offset - (spacing * 2);
      const z = (row * spacing * 0.866) - (spacing * 2);
      
      // إنشاء شكل سداسي
      const hexShape = new THREE.Shape();
      for (let i = 0; i < 6; i++) {
        const angle = (Math.PI / 3) * i;
        const x = hexRadius * Math.cos(angle);
        const y = hexRadius * Math.sin(angle);
        if (i === 0) {
          hexShape.moveTo(x, y);
        } else {
          hexShape.lineTo(x, y);
        }
      }
      
      // إنشاء هندسة الخلية السداسية
      const extrudeSettings = {
        depth: hexHeight,
        bevelEnabled: false
      };
      const hexGeometry = new THREE.ExtrudeGeometry(hexShape, extrudeSettings);
      
      // إنشاء مادة الخلية السداسية
      const hexMaterial = new THREE.MeshPhongMaterial({
        color: 0xf5a623,
        transparent: true,
        opacity: 0.9,
      });
      
      // إنشاء شبكة الخلية السداسية
      const hexMesh = new THREE.Mesh(hexGeometry, hexMaterial);
      hexMesh.position.set(x, 0, z);
      hexMesh.rotation.x = -Math.PI / 2;
      hexMesh.userData = { key };
      
      scene.add(hexMesh);
      hexagons.push(hexMesh);
      
      // إضافة نص المفتاح
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = 256;
      canvas.height = 128;
      context.fillStyle = '#ffffff';
      context.font = '24px Arial';
      context.textAlign = 'center';
      context.fillText(key, 128, 64);
      
      const texture = new THREE.CanvasTexture(canvas);
      const textMaterial = new THREE.MeshBasicMaterial({
        map: texture,
        transparent: true,
        side: THREE.DoubleSide
      });
      
      const textGeometry = new THREE.PlaneGeometry(1.5, 0.5);
      const textMesh = new THREE.Mesh(textGeometry, textMaterial);
      textMesh.position.set(x, hexHeight + 0.1, z);
      textMesh.rotation.x = -Math.PI / 2;
      
      scene.add(textMesh);
    });
    
    // تعيين موقع الكاميرا
    camera.position.set(0, 8, 8);
    camera.lookAt(0, 0, 0);
    
    // تدوير المشهد
    const animate = () => {
      requestAnimationFrame(animate);
      scene.rotation.y += 0.002;
      renderer.render(scene, camera);
    };
    
    animate();
    
    // تحديث حجم المشهد عند تغيير حجم النافذة
    const handleResize = () => {
      if (!containerRef.current) return;
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    };
    
    window.addEventListener('resize', handleResize);
    
    // تنظيف المشهد عند إزالة المكون
    sceneRef.current = { scene, renderer, camera };
    
    // حفظ مرجع containerRef في متغير محلي للاستخدام في دالة التنظيف
    const currentContainer = containerRef.current;
    
    return () => {
      window.removeEventListener('resize', handleResize);
      if (currentContainer) {
        currentContainer.innerHTML = '';
      }
    };
  }, [loading, keys, data]);
  
  // إضافة بيانات جديدة
  const handleAddData = async () => {
    if (!newKey || !newValue) {
      setNotification({
        open: true,
        message: 'يرجى إدخال المفتاح والقيمة',
        severity: 'error'
      });
      return;
    }
    
    try {
      await storeCellData(cellKey, newKey, newValue);
      
      // تحديث البيانات المحلية
      setKeys(prev => [...prev, newKey]);
      setData(prev => ({ ...prev, [newKey]: newValue }));
      
      setNewKey('');
      setNewValue('');
      setOpenAddDialog(false);
      
      setNotification({
        open: true,
        message: 'تم إضافة البيانات بنجاح',
        severity: 'success'
      });
    } catch (err) {
      console.error('خطأ في إضافة البيانات:', err);
      setNotification({
        open: true,
        message: 'حدث خطأ أثناء إضافة البيانات',
        severity: 'error'
      });
    }
  };
  
  // حذف بيانات
  const handleDeleteData = async (key) => {
    try {
      await deleteCellData(cellKey, key);
      
      // تحديث البيانات المحلية
      setKeys(prev => prev.filter(k => k !== key));
      setData(prev => {
        const newData = { ...prev };
        delete newData[key];
        return newData;
      });
      
      setNotification({
        open: true,
        message: 'تم حذف البيانات بنجاح',
        severity: 'success'
      });
    } catch (err) {
      console.error('خطأ في حذف البيانات:', err);
      setNotification({
        open: true,
        message: 'حدث خطأ أثناء حذف البيانات',
        severity: 'error'
      });
    }
  };
  
  // مشاركة الخلية
  const handleShare = () => {
    navigator.clipboard.writeText(`مفتاح الخلية: ${cellKey}`);
    setOpenShareDialog(false);
    setNotification({
      open: true,
      message: 'تم نسخ مفتاح الخلية إلى الحافظة',
      severity: 'success'
    });
  };
  
  // إغلاق الإشعار
  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  return (
    <Box>
      <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} isAdmin={true} />
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h4" component="h1">
                خلية: {cellKey}
              </Typography>
              
              <Box>
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<ShareIcon />}
                  onClick={() => setOpenShareDialog(true)}
                  sx={{ mr: 1 }}
                >
                  مشاركة
                </Button>
                
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<LogoutIcon />}
                  onClick={logout}
                >
                  تسجيل الخروج
                </Button>
              </Box>
            </Box>
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : error ? (
              <Typography color="error">{error}</Typography>
            ) : keys.length === 0 ? (
              <Box sx={{ textAlign: 'center', p: 4 }}>
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  لا توجد بيانات في هذه الخلية
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  onClick={() => setOpenAddDialog(true)}
                  sx={{ mt: 2 }}
                >
                  إضافة بيانات
                </Button>
              </Box>
            ) : (
              <>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Tabs
                    value={viewMode}
                    onChange={(e, newValue) => setViewMode(newValue)}
                    indicatorColor="primary"
                    textColor="primary"
                  >
                    <Tab icon={<GridViewIcon />} label="عرض سداسي" />
                    <Tab icon={<TableViewIcon />} label="عرض قائمة" />
                  </Tabs>
                  
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => setOpenAddDialog(true)}
                  >
                    إضافة بيانات
                  </Button>
                </Box>
                
                {viewMode === 0 ? (
                  // عرض البيانات السداسي
                  <Box sx={{ mb: 4 }}>
                    <HexDataDisplay 
                      data={keys.map(key => ({
                        key: key,
                        value: data[key],
                        type: typeof data[key]
                      }))}
                      onItemClick={(item) => console.log('تم النقر على:', item)}
                    />
                  </Box>
                ) : (
                  // عرض البيانات كقائمة
                  <Box sx={{ mb: 4 }}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      بيانات الخلية:
                    </Typography>
                    
                    {keys.map(key => (
                      <Paper
                        key={key}
                        elevation={1}
                        sx={{
                          p: 2,
                          mb: 2,
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                      >
                        <Box>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {key}
                          </Typography>
                          <Typography variant="body1">
                            {data[key]}
                          </Typography>
                        </Box>
                        
                        <IconButton
                          color="error"
                          onClick={() => handleDeleteData(key)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Paper>
                    ))}
                  </Box>
                )}
              </>
            )}
          </Paper>
        </Box>
      </Container>
      
      {/* مربع حوار إضافة بيانات */}
      <Dialog
        open={openAddDialog}
        onClose={() => setOpenAddDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>إضافة بيانات جديدة</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="المفتاح"
            fullWidth
            variant="outlined"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
          />
          <TextField
            margin="dense"
            label="القيمة"
            fullWidth
            variant="outlined"
            multiline
            rows={4}
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)}>إلغاء</Button>
          <Button onClick={handleAddData} variant="contained" color="primary">
            إضافة
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* مربع حوار مشاركة الخلية */}
      <Dialog
        open={openShareDialog}
        onClose={() => setOpenShareDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>مشاركة الخلية</DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            لمشاركة هذه الخلية مع شخص آخر، أرسل له المعلومات التالية:
          </Typography>
          
          <Paper elevation={1} sx={{ p: 2, bgcolor: '#f5f5f5' }}>
            <Typography variant="body1" fontWeight="bold">
              مفتاح الخلية: {cellKey}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              ملاحظة: ستحتاج أيضًا إلى مشاركة كلمة المرور بشكل آمن.
            </Typography>
          </Paper>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenShareDialog(false)}>إغلاق</Button>
          <Button onClick={handleShare} variant="contained" color="primary">
            نسخ المفتاح
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* إشعار */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CellView;
