import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress
} from '@mui/material';
import StorageIcon from '@mui/icons-material/Storage';
import PeopleIcon from '@mui/icons-material/People';
import DataUsageIcon from '@mui/icons-material/DataUsage';
import SpeedIcon from '@mui/icons-material/Speed';
import SecurityIcon from '@mui/icons-material/Security';
import AddCircleIcon from '@mui/icons-material/AddCircle';

// في الإنتاج، سنستخدم API حقيقي
const fetchStats = async () => {
  // محاكاة استدعاء API
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        totalCells: 156,
        activeCells: 89,
        totalData: 4328,
        avgDataPerCell: 27.7,
        storageUsed: 24.5, // بالميجابايت
        systemHealth: 'جيد',
        cellsCreatedToday: 12
      });
    }, 1000);
  });
};

const StatCard = ({ title, value, icon, color, subtitle }) => {
  return (
    <Card 
      elevation={3} 
      sx={{ 
        height: '100%',
        transition: 'transform 0.3s, box-shadow 0.3s',
        '&:hover': {
          transform: 'translateY(-5px)',
          boxShadow: '0 10px 20px rgba(0,0,0,0.15)'
        }
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" color="text.secondary">
            {title}
          </Typography>
          <Box 
            sx={{ 
              p: 1, 
              borderRadius: '50%', 
              bgcolor: `${color}22`,
              color: color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {icon}
          </Box>
        </Box>
        <Typography variant="h4" component="div" fontWeight="bold">
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

const AdminStats = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const getStats = async () => {
      try {
        setLoading(true);
        const data = await fetchStats();
        setStats(data);
      } catch (error) {
        console.error('خطأ في جلب الإحصائيات:', error);
      } finally {
        setLoading(false);
      }
    };

    getStats();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress size={60} thickness={4} />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>
        نظرة عامة على النظام
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard 
            title="إجمالي الخلايا" 
            value={stats.totalCells} 
            icon={<StorageIcon />} 
            color="#6A11CB"
            subtitle="إجمالي عدد الخلايا في النظام"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <StatCard 
            title="الخلايا النشطة" 
            value={stats.activeCells} 
            icon={<PeopleIcon />} 
            color="#2575FC"
            subtitle={`${Math.round((stats.activeCells / stats.totalCells) * 100)}% من إجمالي الخلايا`}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <StatCard 
            title="خلايا جديدة اليوم" 
            value={stats.cellsCreatedToday} 
            icon={<AddCircleIcon />} 
            color="#4CAF50"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <StatCard 
            title="إجمالي البيانات" 
            value={stats.totalData.toLocaleString()} 
            icon={<DataUsageIcon />} 
            color="#FF5722"
            subtitle="عدد عناصر البيانات المخزنة"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <StatCard 
            title="متوسط البيانات لكل خلية" 
            value={stats.avgDataPerCell} 
            icon={<SpeedIcon />} 
            color="#FFC107"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <StatCard 
            title="المساحة المستخدمة" 
            value={`${stats.storageUsed} MB`} 
            icon={<SecurityIcon />} 
            color="#9C27B0"
          />
        </Grid>
      </Grid>
      
      <Box sx={{ mt: 4, p: 3, bgcolor: stats.systemHealth === 'جيد' ? '#4CAF5022' : '#F4433622', borderRadius: 2 }}>
        <Typography variant="h6" color={stats.systemHealth === 'جيد' ? '#4CAF50' : '#F44336'}>
          حالة النظام: {stats.systemHealth}
        </Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          {stats.systemHealth === 'جيد' 
            ? 'جميع أنظمة HiveDB تعمل بشكل طبيعي. لا توجد مشاكل مكتشفة.' 
            : 'هناك بعض المشاكل التي تحتاج إلى معالجة. يرجى مراجعة سجلات النظام.'}
        </Typography>
      </Box>
    </Box>
  );
};

export default AdminStats;
