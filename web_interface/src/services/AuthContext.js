import React, { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from './api';

// إنشاء سياق المصادقة
const AuthContext = createContext();

// مزود سياق المصادقة
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [currentCell, setCurrentCell] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [sessionToken, setSessionToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // تحميل بيانات الجلسة من التخزين المحلي عند بدء التشغيل
  useEffect(() => {
    const loadSession = () => {
      const savedUser = localStorage.getItem('hivedb_user');
      const savedToken = localStorage.getItem('hivedb_token');
      const savedCell = localStorage.getItem('hivedb_cell');
      
      if (savedUser && savedToken) {
        setCurrentUser(JSON.parse(savedUser));
        setAccessToken(savedToken);
        
        if (savedCell) {
          setCurrentCell(JSON.parse(savedCell));
        }
      }
      
      setLoading(false);
    };
    
    loadSession();
  }, []);

  // تسجيل المستخدم
  const register = async (username, email, password) => {
    try {
      setLoading(true);
      
      const response = await api.post('/auth/register', {
        username,
        email,
        password
      });
      
      return response.data;
    } catch (error) {
      console.error('خطأ في التسجيل:', error.response?.data || error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // تسجيل الدخول باستخدام البريد الإلكتروني
  const login = async (email, password) => {
    try {
      setLoading(true);
      
      const response = await api.post('/auth/login', {
        email,
        password
      });
      
      // حفظ بيانات المستخدم والرمز
      const { access_token, user_id, username, email: userEmail, is_admin } = response.data;
      
      const userData = {
        id: user_id,
        username,
        email: userEmail,
        is_admin
      };
      
      setCurrentUser(userData);
      setAccessToken(access_token);
      
      // حفظ في التخزين المحلي
      localStorage.setItem('hivedb_user', JSON.stringify(userData));
      localStorage.setItem('hivedb_token', access_token);
      
      return userData;
    } catch (error) {
      console.error('خطأ في تسجيل الدخول:', error.response?.data || error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // تسجيل الدخول إلى خلية موجودة
  const loginCell = async (cellKey, password) => {
    try {
      if (!currentUser || !accessToken) {
        throw new Error('يجب تسجيل الدخول أولاً');
      }
      
      setLoading(true);
      
      // التحقق من صلاحية الوصول إلى الخلية
      const response = await api.get(`/cells/${cellKey}`, {
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      });
      
      // حفظ بيانات الخلية
      const cellData = response.data;
      
      setCurrentCell(cellData);
      
      // حفظ في التخزين المحلي
      localStorage.setItem('hivedb_cell', JSON.stringify(cellData));
      
      return cellData;
    } catch (error) {
      console.error('خطأ في الوصول إلى الخلية:', error.response?.data || error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // إنشاء خلية جديدة
  const createCell = async (password) => {
    try {
      if (!currentUser || !accessToken) {
        throw new Error('يجب تسجيل الدخول أولاً');
      }
      
      setLoading(true);
      
      // إرسال طلب إنشاء خلية جديدة
      const response = await api.post('/cells', {
        password: password
      }, {
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      });
      
      // الحصول على بيانات الخلية الجديدة
      const cellData = response.data;
      
      // حفظ بيانات الخلية
      setCurrentCell(cellData);
      
      // حفظ في التخزين المحلي
      localStorage.setItem('hivedb_cell', JSON.stringify(cellData));
      
      // توجيه المستخدم تلقائيًا إلى لوحة التحكم بعد إنشاء الخلية بنجاح
      navigate('/dashboard');
      
      return cellData;
    } catch (error) {
      console.error('خطأ في إنشاء الخلية:', error.response?.data || error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };
  
  // الحصول على خلايا المستخدم
  const getUserCells = async () => {
    try {
      if (!currentUser || !accessToken) {
        throw new Error('يجب تسجيل الدخول أولاً');
      }
      
      const response = await api.get('/cells', {
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('خطأ في الحصول على الخلايا:', error.response?.data || error.message);
      throw error;
    }
  };

  // تسجيل الخروج
  const logout = () => {
    setCurrentUser(null);
    setCurrentCell(null);
    setAccessToken(null);
    setSessionToken(null);
    localStorage.removeItem('hivedb_user');
    localStorage.removeItem('hivedb_cell');
    localStorage.removeItem('hivedb_token');
    navigate('/');
  };

  // القيم التي سيتم توفيرها للمكونات
  const value = {
    currentUser,
    currentCell,
    accessToken,
    sessionToken,
    loading,
    register,
    login,
    loginCell,
    createCell,
    getUserCells,
    logout,
    isAuthenticated: !!accessToken
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// هوك مخصص لاستخدام سياق المصادقة
export const useAuth = () => {
  return useContext(AuthContext);
};

export default AuthContext;
