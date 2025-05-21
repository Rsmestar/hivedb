import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, CircularProgress, Paper, Tooltip, IconButton } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';

const HexDataDisplay = ({ data = [], loading = false, onItemClick }) => {
  const [hexSize, setHexSize] = useState(70); // حجم السداسي
  const containerRef = useRef(null);
  const [visibleData, setVisibleData] = useState([]);

  // تحديد البيانات المرئية بناءً على حجم الشاشة
  useEffect(() => {
    if (!data.length) return;
    
    setVisibleData(data.slice(0, 100)); // عرض أول 100 عنصر كحد أقصى للأداء
  }, [data]);

  const handleZoomIn = () => {
    if (hexSize < 120) {
      setHexSize(prevSize => prevSize + 10);
    }
  };

  const handleZoomOut = () => {
    if (hexSize > 40) {
      setHexSize(prevSize => prevSize - 10);
    }
  };

  // حساب لون الخلفية بناءً على نوع البيانات
  const getBackgroundColor = (item) => {
    if (!item || !item.type) return '#6A11CB';
    
    switch (item.type.toLowerCase()) {
      case 'string':
        return '#6A11CB'; // أرجواني
      case 'number':
        return '#2575FC'; // أزرق
      case 'boolean':
        return '#FFC107'; // أصفر
      case 'object':
        return '#FF5722'; // برتقالي
      case 'array':
        return '#4CAF50'; // أخضر
      default:
        return '#9C27B0'; // أرجواني داكن
    }
  };

  // تحديد لون النص بناءً على لون الخلفية
  const getTextColor = (bgColor) => {
    // الألوان الداكنة تحتاج نص أبيض
    const darkColors = ['#6A11CB', '#2575FC', '#9C27B0', '#FF5722'];
    return darkColors.includes(bgColor) ? '#FFFFFF' : '#000000';
  };

  // تقصير النص إذا كان طويلاً جداً
  const truncateText = (text, maxLength = 10) => {
    if (!text) return '';
    if (typeof text !== 'string') {
      text = JSON.stringify(text);
    }
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  };

  // إنشاء شكل سداسي باستخدام CSS
  const Hexagon = ({ item, index }) => {
    const bgColor = getBackgroundColor(item);
    const textColor = getTextColor(bgColor);
    
    return (
      <Tooltip 
        title={
          <Box>
            <Typography variant="subtitle2" fontWeight="bold">
              {item.key || `عنصر ${index + 1}`}
            </Typography>
            <Typography variant="body2">
              النوع: {item.type || 'غير معروف'}
            </Typography>
            <Typography variant="body2">
              القيمة: {item.value !== undefined ? String(item.value) : 'غير محدد'}
            </Typography>
          </Box>
        }
        arrow
      >
        <Box
          onClick={() => onItemClick && onItemClick(item, index)}
          sx={{
            width: `${hexSize}px`,
            height: `${hexSize * 0.866}px`, // ارتفاع السداسي = الجانب * 0.866
            position: 'relative',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            margin: `${hexSize * 0.25}px ${hexSize * 0.05}px`,
            cursor: 'pointer',
            transition: 'transform 0.3s, box-shadow 0.3s',
            '&:hover': {
              transform: 'translateY(-5px)',
              boxShadow: '0 5px 15px rgba(0,0,0,0.3)',
              zIndex: 10
            },
            '&:before, &:after': {
              content: '""',
              position: 'absolute',
              width: '100%',
              height: '100%',
              backgroundColor: bgColor,
              transform: 'rotate(60deg)'
            },
            '&:before': {
              transform: 'rotate(60deg)'
            },
            '&:after': {
              transform: 'rotate(-60deg)'
            }
          }}
        >
          <Box
            sx={{
              position: 'relative',
              zIndex: 1,
              color: textColor,
              fontWeight: 'bold',
              textAlign: 'center',
              padding: '0 10px'
            }}
          >
            <Typography 
              variant="caption" 
              component="div" 
              fontWeight="bold"
              sx={{ fontSize: `${hexSize * 0.18}px` }}
            >
              {truncateText(item.key || `${index + 1}`, 8)}
            </Typography>
            <Typography 
              variant="caption" 
              component="div"
              sx={{ fontSize: `${hexSize * 0.14}px` }}
            >
              {truncateText(item.value, 8)}
            </Typography>
          </Box>
        </Box>
      </Tooltip>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress size={60} thickness={4} />
      </Box>
    );
  }

  if (!visibleData.length) {
    return (
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          textAlign: 'center',
          borderRadius: 2,
          bgcolor: 'background.paper'
        }}
      >
        <Typography variant="h6" color="text.secondary">
          لا توجد بيانات لعرضها
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          أضف بيانات إلى الخلية لتظهر هنا
        </Typography>
      </Paper>
    );
  }

  return (
    <Box sx={{ position: 'relative' }}>
      <Box sx={{ 
        position: 'absolute', 
        top: 10, 
        right: 10, 
        zIndex: 100,
        display: 'flex',
        bgcolor: 'background.paper',
        borderRadius: 1,
        boxShadow: 2,
        p: 0.5
      }}>
        <Tooltip title="تكبير">
          <IconButton onClick={handleZoomIn} size="small">
            <ZoomInIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="تصغير">
          <IconButton onClick={handleZoomOut} size="small">
            <ZoomOutIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="معلومات">
          <IconButton size="small">
            <InfoIcon />
          </IconButton>
        </Tooltip>
      </Box>
      
      <Box 
        ref={containerRef}
        sx={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          justifyContent: 'center',
          padding: 2,
          overflowY: 'auto',
          maxHeight: '70vh'
        }}
      >
        {visibleData.map((item, index) => (
          <Hexagon key={index} item={item} index={index} />
        ))}
      </Box>
      
      {visibleData.length < data.length && (
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            يتم عرض {visibleData.length} من أصل {data.length} عنصر
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default HexDataDisplay;
