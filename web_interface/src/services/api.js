import axios from 'axios';

// إنشاء نسخة من Axios مع الإعدادات الافتراضية
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// إضافة معترض للطلبات لإضافة رمز المصادقة
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('hivedb_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// إضافة معترض للاستجابات للتعامل مع أخطاء المصادقة
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // تسجيل الخروج تلقائيًا عند انتهاء صلاحية الجلسة
      localStorage.removeItem('hivedb_cell');
      localStorage.removeItem('hivedb_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// وظائف API مساعدة

// الحصول على قائمة المفاتيح في الخلية
export const getCellKeys = async (cellKey) => {
  try {
    const response = await api.get(`/cells/${cellKey}/keys`);
    return response.data.keys;
  } catch (error) {
    console.error('خطأ في الحصول على المفاتيح:', error);
    throw error;
  }
};

// الحصول على قيمة من الخلية
export const getCellData = async (cellKey, dataKey) => {
  try {
    const response = await api.get(`/cells/${cellKey}/data/${dataKey}`);
    return response.data.value;
  } catch (error) {
    console.error('خطأ في الحصول على البيانات:', error);
    throw error;
  }
};

// تخزين قيمة في الخلية
export const storeCellData = async (cellKey, dataKey, value) => {
  try {
    const response = await api.post(`/cells/${cellKey}/data`, {
      key: dataKey,
      value,
    });
    return response.data;
  } catch (error) {
    console.error('خطأ في تخزين البيانات:', error);
    throw error;
  }
};

// حذف قيمة من الخلية
export const deleteCellData = async (cellKey, dataKey) => {
  try {
    const response = await api.delete(`/cells/${cellKey}/data/${dataKey}`);
    return response.data;
  } catch (error) {
    console.error('خطأ في حذف البيانات:', error);
    throw error;
  }
};

export default api;
