import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tooltip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import LockIcon from '@mui/icons-material/Lock';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import WarningIcon from '@mui/icons-material/Warning';

// محاكاة جلب بيانات الخلايا من الخادم
const fetchCells = async () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const cells = Array.from({ length: 50 }, (_, index) => ({
        id: `cell${1000000 + index}`,
        createdAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
        lastAccess: new Date(Date.now() - Math.floor(Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString(),
        dataCount: Math.floor(Math.random() * 100),
        storageSize: (Math.random() * 5).toFixed(2),
        status: Math.random() > 0.2 ? 'نشط' : 'غير نشط'
      }));
      resolve(cells);
    }, 1000);
  });
};

const AdminCellsTable = () => {
  const [loading, setLoading] = useState(true);
  const [cells, setCells] = useState([]);
  const [filteredCells, setFilteredCells] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCell, setSelectedCell] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  useEffect(() => {
    const getCells = async () => {
      try {
        setLoading(true);
        const data = await fetchCells();
        setCells(data);
        setFilteredCells(data);
      } catch (error) {
        console.error('خطأ في جلب بيانات الخلايا:', error);
      } finally {
        setLoading(false);
      }
    };

    getCells();
  }, []);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredCells(cells);
    } else {
      const filtered = cells.filter(cell => 
        cell.id.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredCells(filtered);
    }
  }, [searchQuery, cells]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
    setPage(0);
  };

  const handleViewCell = (cell) => {
    console.log('عرض الخلية:', cell);
    // هنا سيتم التنقل إلى صفحة تفاصيل الخلية
  };

  const handleDeleteClick = (cell) => {
    setSelectedCell(cell);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedCell) {
      // محاكاة حذف الخلية
      const updatedCells = cells.filter(cell => cell.id !== selectedCell.id);
      setCells(updatedCells);
      setFilteredCells(updatedCells.filter(cell => 
        cell.id.toLowerCase().includes(searchQuery.toLowerCase())
      ));
    }
    setDeleteDialogOpen(false);
    setSelectedCell(null);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setSelectedCell(null);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ar-SA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
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
          إدارة الخلايا
        </Typography>
        <TextField
          variant="outlined"
          placeholder="بحث عن خلية..."
          size="small"
          value={searchQuery}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ width: 250 }}
        />
      </Box>

      <TableContainer component={Paper} elevation={3}>
        <Table sx={{ minWidth: 650 }} aria-label="جدول الخلايا">
          <TableHead>
            <TableRow sx={{ bgcolor: 'background.default' }}>
              <TableCell>معرف الخلية</TableCell>
              <TableCell>تاريخ الإنشاء</TableCell>
              <TableCell>آخر وصول</TableCell>
              <TableCell>عدد البيانات</TableCell>
              <TableCell>المساحة (MB)</TableCell>
              <TableCell>الحالة</TableCell>
              <TableCell>الإجراءات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredCells
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((cell) => (
                <TableRow
                  key={cell.id}
                  sx={{ 
                    '&:hover': { bgcolor: 'action.hover' },
                    transition: 'background-color 0.2s'
                  }}
                >
                  <TableCell component="th" scope="row">
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {cell.status === 'نشط' ? 
                        <LockOpenIcon sx={{ mr: 1, color: 'success.main', fontSize: 18 }} /> : 
                        <LockIcon sx={{ mr: 1, color: 'text.secondary', fontSize: 18 }} />
                      }
                      {cell.id}
                    </Box>
                  </TableCell>
                  <TableCell>{formatDate(cell.createdAt)}</TableCell>
                  <TableCell>{formatDate(cell.lastAccess)}</TableCell>
                  <TableCell>{cell.dataCount}</TableCell>
                  <TableCell>{cell.storageSize}</TableCell>
                  <TableCell>
                    <Chip 
                      label={cell.status} 
                      size="small"
                      color={cell.status === 'نشط' ? 'success' : 'default'}
                      sx={{ 
                        fontWeight: 'medium',
                        minWidth: 80
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Tooltip title="عرض الخلية">
                        <IconButton 
                          size="small" 
                          onClick={() => handleViewCell(cell)}
                          color="primary"
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="حذف الخلية">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteClick(cell)}
                          color="error"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            {filteredCells.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                  <Typography variant="body1" color="text.secondary">
                    لا توجد خلايا مطابقة للبحث
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={filteredCells.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="عدد الصفوف:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} من ${count}`}
      />

      {/* مربع حوار تأكيد الحذف */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
      >
        <DialogTitle id="delete-dialog-title" sx={{ display: 'flex', alignItems: 'center' }}>
          <WarningIcon color="warning" sx={{ mr: 1 }} />
          تأكيد حذف الخلية
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            هل أنت متأكد من رغبتك في حذف الخلية {selectedCell?.id}؟
          </Typography>
          <Typography variant="body2" color="error" sx={{ mt: 2 }}>
            تحذير: هذا الإجراء لا يمكن التراجع عنه وسيؤدي إلى فقدان جميع البيانات المخزنة في هذه الخلية.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            إلغاء
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            حذف
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminCellsTable;
