import { createTheme } from '@mui/material/styles';

// تعريف الألوان الرئيسية للتطبيق
const primaryColor = '#6A11CB'; // لون أرجواني غامق
const secondaryColor = '#2575FC'; // لون أزرق فاتح
const accentColor = '#FFC107'; // لون أصفر ذهبي
const darkBg = '#121212'; // خلفية داكنة
const lightBg = '#F8F9FA'; // خلفية فاتحة

// إنشاء سمة داكنة وفاتحة
export const lightTheme = createTheme({
  direction: 'rtl',
  palette: {
    mode: 'light',
    primary: {
      main: primaryColor,
      light: '#8C42E9',
      dark: '#4A0D8F',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: secondaryColor,
      light: '#5A9DFF',
      dark: '#0F52BA',
      contrastText: '#FFFFFF',
    },
    accent: {
      main: accentColor,
      light: '#FFD54F',
      dark: '#FFA000',
      contrastText: '#000000',
    },
    background: {
      default: lightBg,
      paper: '#FFFFFF',
      gradient: 'linear-gradient(135deg, #6A11CB 0%, #2575FC 100%)',
    },
    text: {
      primary: '#212121',
      secondary: '#616161',
    },
  },
  typography: {
    fontFamily: 'Cairo, Roboto, Arial, sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1rem',
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '10px 20px',
          boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 6px 15px rgba(0, 0, 0, 0.15)',
          },
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #6A11CB 0%, #2575FC 100%)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 8px 20px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
        },
        elevation1: {
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
        },
        elevation2: {
          boxShadow: '0 4px 15px rgba(0, 0, 0, 0.08)',
        },
        elevation3: {
          boxShadow: '0 6px 20px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #6A11CB 0%, #2575FC 100%)',
          boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
        },
      },
    },
  },
});

export const darkTheme = createTheme({
  direction: 'rtl',
  palette: {
    mode: 'dark',
    primary: {
      main: primaryColor,
      light: '#8C42E9',
      dark: '#4A0D8F',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: secondaryColor,
      light: '#5A9DFF',
      dark: '#0F52BA',
      contrastText: '#FFFFFF',
    },
    accent: {
      main: accentColor,
      light: '#FFD54F',
      dark: '#FFA000',
      contrastText: '#000000',
    },
    background: {
      default: darkBg,
      paper: '#1E1E1E',
      gradient: 'linear-gradient(135deg, #6A11CB 0%, #2575FC 100%)',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0',
    },
  },
  typography: {
    fontFamily: 'Cairo, Roboto, Arial, sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1rem',
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '10px 20px',
          boxShadow: '0 4px 10px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 6px 15px rgba(0, 0, 0, 0.4)',
          },
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #6A11CB 0%, #2575FC 100%)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 8px 20px rgba(0, 0, 0, 0.3)',
          overflow: 'hidden',
          backgroundColor: '#1E1E1E',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          backgroundColor: '#1E1E1E',
        },
        elevation1: {
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
        },
        elevation2: {
          boxShadow: '0 4px 15px rgba(0, 0, 0, 0.25)',
        },
        elevation3: {
          boxShadow: '0 6px 20px rgba(0, 0, 0, 0.3)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #6A11CB 0%, #2575FC 100%)',
          boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)',
        },
      },
    },
  },
});

// وظيفة لاختيار السمة بناءً على وضع الظلام
export const getTheme = (isDarkMode) => {
  return isDarkMode ? darkTheme : lightTheme;
};

export default lightTheme;
