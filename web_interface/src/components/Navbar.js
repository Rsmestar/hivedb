import React, { useState } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton, 
  Box, 
  Menu, 
  MenuItem, 
  Tooltip, 
  Avatar,
  Switch,
  FormControlLabel
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import HexLogo from './HexLogo';

const Navbar = ({ darkMode, toggleDarkMode, isAdmin = false }) => {
  const { isAuthenticated, currentCell, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [mobileMenuAnchor, setMobileMenuAnchor] = useState(null);
  
  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMobileMenu = (event) => {
    setMobileMenuAnchor(event.currentTarget);
  };
  
  const handleClose = () => {
    setAnchorEl(null);
  };
  
  const handleMobileClose = () => {
    setMobileMenuAnchor(null);
  };
  
  const handleLogout = () => {
    handleClose();
    logout();
    navigate('/');
  };
  
  const handleAdminPanel = () => {
    handleClose();
    navigate('/admin');
  };
  
  const handleDashboard = () => {
    handleClose();
    if (currentCell) {
      navigate(`/cell/${currentCell.key}`);
    }
  };
  
  return (
    <AppBar position="static" elevation={3}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* الشعار والعنوان */}
        <Box sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => navigate('/')}>
          <Box sx={{ width: 40, height: 40, mr: 1 }}>
            <HexLogo size={40} />
          </Box>
          <Typography variant="h5" component="div" sx={{ fontWeight: 'bold', letterSpacing: 1 }}>
            HiveDB
          </Typography>
        </Box>
        
        {/* القائمة الرئيسية - للشاشات الكبيرة */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center' }}>
          {/* زر تبديل الوضع المظلم/الفاتح */}
          <Tooltip title={darkMode ? "الوضع الفاتح" : "الوضع الداكن"}>
            <IconButton color="inherit" onClick={toggleDarkMode} sx={{ mr: 2 }}>
              {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
          </Tooltip>
          
          {isAuthenticated && (
            <>
              <Tooltip title="لوحة التحكم">
                <IconButton color="inherit" onClick={handleDashboard} sx={{ mr: 2 }}>
                  <DashboardIcon />
                </IconButton>
              </Tooltip>
              
              {isAdmin && (
                <Tooltip title="لوحة المسؤول">
                  <IconButton color="inherit" onClick={handleAdminPanel} sx={{ mr: 2 }}>
                    <AdminPanelSettingsIcon />
                  </IconButton>
                </Tooltip>
              )}
              
              <Tooltip title="الحساب">
                <IconButton
                  color="inherit"
                  onClick={handleMenu}
                  sx={{ 
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderRadius: '50%',
                    padding: '4px'
                  }}
                >
                  <AccountCircleIcon />
                </IconButton>
              </Tooltip>
              
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              >
                {currentCell && (
                  <MenuItem sx={{ fontWeight: 'bold' }}>
                    خلية: {currentCell.key}
                  </MenuItem>
                )}
                <MenuItem onClick={handleDashboard}>
                  <DashboardIcon sx={{ mr: 1 }} />
                  لوحة التحكم
                </MenuItem>
                {isAdmin && (
                  <MenuItem onClick={handleAdminPanel}>
                    <AdminPanelSettingsIcon sx={{ mr: 1 }} />
                    لوحة المسؤول
                  </MenuItem>
                )}
                <MenuItem onClick={handleLogout}>
                  <LogoutIcon sx={{ mr: 1 }} />
                  تسجيل الخروج
                </MenuItem>
              </Menu>
            </>
          )}
        </Box>
        
        {/* قائمة الجوال */}
        <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
          <IconButton
            color="inherit"
            onClick={handleMobileMenu}
          >
            <MenuIcon />
          </IconButton>
          
          <Menu
            anchorEl={mobileMenuAnchor}
            open={Boolean(mobileMenuAnchor)}
            onClose={handleMobileClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={() => {
              toggleDarkMode();
              handleMobileClose();
            }}>
              {darkMode ? <Brightness7Icon sx={{ mr: 1 }} /> : <Brightness4Icon sx={{ mr: 1 }} />}
              {darkMode ? "الوضع الفاتح" : "الوضع الداكن"}
            </MenuItem>
            
            {isAuthenticated && (
              <>
                <MenuItem onClick={() => {
                  handleDashboard();
                  handleMobileClose();
                }}>
                  <DashboardIcon sx={{ mr: 1 }} />
                  لوحة التحكم
                </MenuItem>
                
                {isAdmin && (
                  <MenuItem onClick={() => {
                    handleAdminPanel();
                    handleMobileClose();
                  }}>
                    <AdminPanelSettingsIcon sx={{ mr: 1 }} />
                    لوحة المسؤول
                  </MenuItem>
                )}
                
                <MenuItem onClick={() => {
                  handleLogout();
                  handleMobileClose();
                }}>
                  <LogoutIcon sx={{ mr: 1 }} />
                  تسجيل الخروج
                </MenuItem>
              </>
            )}
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
