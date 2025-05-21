import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  CircularProgress,
  Card,
  CardContent,
  CardHeader,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Tooltip
} from '@mui/material';

// ألوان للرسوم البيانية
const COLORS = ['#6A11CB', '#2575FC', '#FFC107', '#FF5722', '#4CAF50', '#9C27B0'];

// محاكاة جلب البيانات من الخادم
const fetchChartData = async () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        cellsData: [
          { name: 'خلايا نشطة', value: 89 },
          { name: 'خلايا غير نشطة', value: 67 }
        ],
        storageData: [
          { name: 'بيانات المستخدمين', value: 18.3 },
          { name: 'بيانات النظام', value: 4.2 },
          { name: 'بيانات التسجيل', value: 2.0 }
        ],
        activityData: [
          { day: 'السبت', operations: 120, cells: 3 },
          { day: 'الأحد', operations: 145, cells: 5 },
          { day: 'الاثنين', operations: 132, cells: 4 },
          { day: 'الثلاثاء', operations: 189, cells: 7 },
          { day: 'الأربعاء', operations: 176, cells: 6 },
          { day: 'الخميس', operations: 210, cells: 8 },
          { day: 'الجمعة', operations: 160, cells: 5 }
        ],
        growthData: [
          { month: 'يناير', cells: 42 },
          { month: 'فبراير', cells: 63 },
          { month: 'مارس', cells: 78 },
          { month: 'أبريل', cells: 91 },
          { month: 'مايو', cells: 112 },
          { month: 'يونيو', cells: 135 },
          { month: 'يوليو', cells: 156 }
        ],
        dataDistribution: [
          { type: 'نصوص', count: 1850 },
          { type: 'أرقام', count: 1230 },
          { type: 'JSON', count: 920 },
          { type: 'روابط', count: 328 }
        ]
      });
    }, 1000);
  });
};

// مكون الرسم البياني الدائري المبسط
const SimplePieCard = ({ data, title, colors }) => {
  const total = data.reduce((sum, item) => sum + item.value, 0);
  
  return (
    <Card elevation={3} sx={{ height: '100%' }}>
      <CardHeader title={title} />
      <Divider />
      <CardContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {data.map((item, index) => {
            const percentage = ((item.value / total) * 100).toFixed(1);
            return (
              <Box key={index}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">{item.name}</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {item.value} ({percentage}%)
                  </Typography>
                </Box>
                <Box sx={{ width: '100%', position: 'relative' }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={parseFloat(percentage)} 
                    sx={{ 
                      height: 10, 
                      borderRadius: 5,
                      backgroundColor: 'rgba(0,0,0,0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: colors[index % colors.length]
                      }
                    }} 
                  />
                </Box>
              </Box>
            );
          })}
        </Box>
      </CardContent>
    </Card>
  );
};

// مكون الرسم البياني الشريطي المبسط
const SimpleBarCard = ({ data, title, dataKey, nameKey, colors }) => {
  const maxValue = Math.max(...data.map(item => item[dataKey]));
  
  return (
    <Card elevation={3} sx={{ height: '100%' }}>
      <CardHeader title={title} />
      <Divider />
      <CardContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          {data.map((item, index) => {
            const percentage = (item[dataKey] / maxValue) * 100;
            return (
              <Box key={index}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">{item[nameKey]}</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {item[dataKey]}
                  </Typography>
                </Box>
                <Tooltip title={`${item[dataKey]}`}>
                  <Box 
                    sx={{ 
                      height: 30, 
                      width: `${percentage}%`, 
                      bgcolor: colors[index % colors.length],
                      borderRadius: 1,
                      transition: 'width 1s ease-in-out',
                      minWidth: '5%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'flex-end',
                      pr: 1,
                      color: '#fff',
                      fontWeight: 'bold'
                    }}
                  >
                    {percentage > 15 && item[dataKey]}
                  </Box>
                </Tooltip>
              </Box>
            );
          })}
        </Box>
      </CardContent>
    </Card>
  );
};

// مكون جدول النشاط
const ActivityTable = ({ data, title }) => {
  return (
    <Card elevation={3} sx={{ height: '100%' }}>
      <CardHeader title={title} />
      <Divider />
      <CardContent>
        <Box sx={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ padding: '12px 8px', textAlign: 'right', borderBottom: '1px solid rgba(224, 224, 224, 1)' }}>اليوم</th>
                <th style={{ padding: '12px 8px', textAlign: 'center', borderBottom: '1px solid rgba(224, 224, 224, 1)' }}>العمليات</th>
                <th style={{ padding: '12px 8px', textAlign: 'center', borderBottom: '1px solid rgba(224, 224, 224, 1)' }}>الخلايا الجديدة</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={index} style={{ backgroundColor: index % 2 === 0 ? 'rgba(0, 0, 0, 0.03)' : 'transparent' }}>
                  <td style={{ padding: '12px 8px', textAlign: 'right' }}>{row.day}</td>
                  <td style={{ padding: '12px 8px', textAlign: 'center' }}>{row.operations}</td>
                  <td style={{ padding: '12px 8px', textAlign: 'center' }}>{row.cells}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Box>
      </CardContent>
    </Card>
  );
};

const AdminCharts = () => {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState(null);
  const [timeRange, setTimeRange] = useState('week');

  useEffect(() => {
    const getChartData = async () => {
      try {
        setLoading(true);
        const data = await fetchChartData();
        setChartData(data);
      } catch (error) {
        console.error('خطأ في جلب بيانات الرسوم البيانية:', error);
      } finally {
        setLoading(false);
      }
    };

    getChartData();
  }, []);

  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
    // في التطبيق الحقيقي، سنقوم بإعادة جلب البيانات بناءً على النطاق الزمني المحدد
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
          تحليل البيانات
        </Typography>
        <FormControl variant="outlined" size="small" sx={{ minWidth: 150 }}>
          <InputLabel>النطاق الزمني</InputLabel>
          <Select
            value={timeRange}
            onChange={handleTimeRangeChange}
            label="النطاق الزمني"
          >
            <MenuItem value="day">اليوم</MenuItem>
            <MenuItem value="week">الأسبوع</MenuItem>
            <MenuItem value="month">الشهر</MenuItem>
            <MenuItem value="year">السنة</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        {/* توزيع حالة الخلايا */}
        <Grid item xs={12} md={6}>
          <SimplePieCard
            data={chartData.cellsData}
            title="توزيع حالة الخلايا"
            colors={['#6A11CB', '#E0E0E0']}
          />
        </Grid>

        {/* توزيع المساحة التخزينية */}
        <Grid item xs={12} md={6}>
          <SimplePieCard
            data={chartData.storageData}
            title="توزيع المساحة التخزينية (MB)"
            colors={['#2575FC', '#FFC107', '#FF5722']}
          />
        </Grid>

        {/* نشاط النظام */}
        <Grid item xs={12}>
          <ActivityTable
            data={chartData.activityData}
            title="نشاط النظام خلال الأسبوع"
          />
        </Grid>

        {/* نمو الخلايا */}
        <Grid item xs={12} md={6}>
          <SimpleBarCard
            data={chartData.growthData}
            title="نمو عدد الخلايا"
            dataKey="cells"
            nameKey="month"
            colors={['#6A11CB', '#2575FC', '#FFC107', '#FF5722', '#4CAF50', '#9C27B0']}
          />
        </Grid>

        {/* توزيع أنواع البيانات */}
        <Grid item xs={12} md={6}>
          <SimpleBarCard
            data={chartData.dataDistribution}
            title="توزيع أنواع البيانات"
            dataKey="count"
            nameKey="type"
            colors={['#2575FC', '#FFC107', '#FF5722', '#4CAF50']}
          />
        </Grid>
      </Grid>

      <Box sx={{ mt: 4, p: 3, bgcolor: 'background.paper', borderRadius: 2, boxShadow: 1 }}>
        <Typography variant="h6" gutterBottom>
          تحليل الاتجاهات
        </Typography>
        <Typography variant="body1">
          بناءً على البيانات المعروضة، يمكن ملاحظة زيادة مستمرة في عدد الخلايا الجديدة بنسبة 15% شهرياً. كما أن معدل النشاط في النظام يزداد بشكل ملحوظ خلال منتصف الأسبوع.
        </Typography>
      </Box>
    </Box>
  );
};

export default AdminCharts;
