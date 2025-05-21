import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Tabs,
  Tab,
  Button,
  IconButton,
  Tooltip
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import DashboardIcon from '@mui/icons-material/Dashboard';
import StorageIcon from '@mui/icons-material/Storage';
import PeopleIcon from '@mui/icons-material/People';
import SettingsIcon from '@mui/icons-material/Settings';

// استيراد المكونات الفرعية
import AdminStats from './AdminStats';
import AdminCellsTable from './AdminCellsTable';
import AdminCharts from './AdminCharts';
import AdminSettings from './AdminSettings';

const AdminDashboard = () => {
  const [tabValue, setTabValue] = useState(0);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleRefresh = () => {
    setRefreshKey(prevKey => prevKey + 1);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          لوحة تحكم المسؤول
        </Typography>
        <Tooltip title="تحديث البيانات">
          <IconButton onClick={handleRefresh} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Paper sx={{ mb: 4 }} elevation={3}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
          indicatorColor="primary"
          textColor="primary"
          aria-label="admin tabs"
        >
          <Tab icon={<DashboardIcon />} label="الإحصائيات" />
          <Tab icon={<StorageIcon />} label="الخلايا" />
          <Tab icon={<PeopleIcon />} label="الرسوم البيانية" />
          <Tab icon={<SettingsIcon />} label="الإعدادات" />
        </Tabs>
      </Paper>

      <Box sx={{ mt: 2 }}>
        {tabValue === 0 && <AdminStats key={refreshKey} />}
        {tabValue === 1 && <AdminCellsTable key={refreshKey} />}
        {tabValue === 2 && <AdminCharts key={refreshKey} />}
        {tabValue === 3 && <AdminSettings key={refreshKey} />}
      </Box>
    </Box>
  );
};

export default AdminDashboard;
