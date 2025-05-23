import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import * as d3 from 'd3';
import axios from 'axios';
import { toast } from 'react-toastify';
import '../styles/HexagonalDashboard.css';

const HexagonalDashboard = ({ hiveId }) => {
  const [cells, setCells] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCell, setSelectedCell] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [viewMode, setViewMode] = useState('visual'); // visual, list, or map
  const svgRef = useRef(null);
  const navigate = useNavigate();

  // الإحداثيات السداسية
  const hexRadius = 50;
  const hexHeight = Math.sqrt(3) * hexRadius;
  const hexWidth = 2 * hexRadius;
  const hexagonPoints = [
    [0, -hexRadius],
    [hexRadius * 0.866, -hexRadius * 0.5],
    [hexRadius * 0.866, hexRadius * 0.5],
    [0, hexRadius],
    [-hexRadius * 0.866, hexRadius * 0.5],
    [-hexRadius * 0.866, -hexRadius * 0.5]
  ];

  // تحميل بيانات الخلايا
  useEffect(() => {
    const fetchCells = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/hives/${hiveId}/cells`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setCells(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching cells:', error);
        toast.error('فشل في تحميل بيانات الخلايا');
        setLoading(false);
      }
    };

    fetchCells();
  }, [hiveId]);

  // رسم الخلايا السداسية
  useEffect(() => {
    if (loading || viewMode !== 'visual' || !cells.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;
    const centerX = width / 2;
    const centerY = height / 2;

    // إنشاء مجموعة للخلايا مع تكبير/تصغير
    const cellGroup = svg.append('g')
      .attr('transform', `translate(${centerX}, ${centerY}) scale(${zoomLevel})`);

    // دالة لتحويل الإحداثيات السداسية إلى إحداثيات كارتيزية
    const hexToPixel = (q, r) => {
      const x = hexWidth * (q + r/2) * 0.75;
      const y = hexHeight * r * 0.5;
      return [x, y];
    };

    // إنشاء الخلايا
    cells.forEach(cell => {
      const [q, r] = cell.coordinates.split(',').map(Number);
      const [x, y] = hexToPixel(q, r);

      // إنشاء مسار سداسي
      const hexPath = d3.line()(hexagonPoints.map(point => [point[0] + x, point[1] + y]));

      // إضافة الخلية
      const hexCell = cellGroup.append('path')
        .attr('d', hexPath)
        .attr('class', `hex-cell ${cell.cell_id === selectedCell?.cell_id ? 'selected' : ''}`)
        .attr('fill', getCellColor(cell))
        .attr('stroke', '#333')
        .attr('stroke-width', 2)
        .on('click', () => handleCellClick(cell));

      // إضافة نص داخل الخلية
      cellGroup.append('text')
        .attr('x', x)
        .attr('y', y)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('class', 'hex-text')
        .text(getCellLabel(cell));

      // إضافة تأثيرات التحويم
      hexCell.on('mouseover', function() {
        d3.select(this).attr('stroke-width', 3).attr('stroke', '#007bff');
      }).on('mouseout', function() {
        d3.select(this).attr('stroke-width', 2).attr('stroke', '#333');
      });
    });

    // إضافة التكبير/التصغير
    svg.call(d3.zoom()
      .scaleExtent([0.5, 5])
      .on('zoom', (event) => {
        cellGroup.attr('transform', event.transform);
        setZoomLevel(event.transform.k);
      }));

  }, [cells, loading, selectedCell, zoomLevel, viewMode]);

  // تحديد لون الخلية بناءً على نوعها
  const getCellColor = (cell) => {
    switch (cell.data_type) {
      case 'json':
        return '#e3f2fd'; // أزرق فاتح
      case 'binary':
        return '#f1f8e9'; // أخضر فاتح
      case 'key_value':
        return '#fff3e0'; // برتقالي فاتح
      case 'index':
        return '#f3e5f5'; // أرجواني فاتح
      default:
        return '#f5f5f5'; // رمادي فاتح
    }
  };

  // تحديد تسمية الخلية
  const getCellLabel = (cell) => {
    // استخراج اسم الخلية من البيانات إن وجد
    if (cell.data && cell.data.name) {
      return cell.data.name;
    }
    // استخدام معرف الخلية المختصر
    return cell.cell_id.substring(0, 6);
  };

  // معالجة النقر على خلية
  const handleCellClick = (cell) => {
    setSelectedCell(cell);
  };

  // فتح تفاصيل الخلية
  const openCellDetails = () => {
    if (selectedCell) {
      navigate(`/cells/${selectedCell.cell_id}`);
    }
  };

  // إنشاء خلية جديدة
  const createNewCell = () => {
    navigate(`/hives/${hiveId}/create-cell`);
  };

  // تبديل وضع العرض
  const toggleViewMode = (mode) => {
    setViewMode(mode);
  };

  // عرض قائمة الخلايا
  const renderCellList = () => {
    return (
      <div className="cell-list">
        <table className="table">
          <thead>
            <tr>
              <th>معرف الخلية</th>
              <th>الإحداثيات</th>
              <th>نوع البيانات</th>
              <th>تاريخ الإنشاء</th>
              <th>إجراءات</th>
            </tr>
          </thead>
          <tbody>
            {cells.map(cell => (
              <tr 
                key={cell.cell_id} 
                className={cell.cell_id === selectedCell?.cell_id ? 'selected-row' : ''}
                onClick={() => setSelectedCell(cell)}
              >
                <td>{cell.cell_id}</td>
                <td>{cell.coordinates}</td>
                <td>{cell.data_type}</td>
                <td>{new Date(cell.created_at).toLocaleString('ar-SA')}</td>
                <td>
                  <button 
                    className="btn btn-sm btn-primary"
                    onClick={() => navigate(`/cells/${cell.cell_id}`)}
                  >
                    عرض
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  // عرض خريطة الحرارة
  const renderHeatMap = () => {
    return (
      <div className="heat-map">
        <div className="map-container">
          {/* هنا يمكن إضافة خريطة حرارية تفاعلية باستخدام مكتبة مثل heatmap.js */}
          <div className="map-placeholder">
            <h3>خريطة الحرارة للخلايا</h3>
            <p>تظهر كثافة البيانات وتوزيعها في الشبكة السداسية</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="hexagonal-dashboard">
      <div className="dashboard-header">
        <h2>لوحة تحكم الخلايا السداسية</h2>
        <div className="view-controls">
          <button 
            className={`btn ${viewMode === 'visual' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => toggleViewMode('visual')}
          >
            عرض بصري
          </button>
          <button 
            className={`btn ${viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => toggleViewMode('list')}
          >
            قائمة
          </button>
          <button 
            className={`btn ${viewMode === 'map' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => toggleViewMode('map')}
          >
            خريطة حرارية
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading-spinner">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">جاري التحميل...</span>
          </div>
        </div>
      ) : (
        <div className="dashboard-content">
          {viewMode === 'visual' && (
            <div className="visual-view">
              <div className="svg-container">
                <svg ref={svgRef} className="hex-grid" width="100%" height="600"></svg>
              </div>
              <div className="zoom-controls">
                <button className="btn btn-sm btn-outline-secondary" onClick={() => setZoomLevel(Math.max(0.5, zoomLevel - 0.5))}>
                  <i className="fas fa-search-minus"></i>
                </button>
                <span>{Math.round(zoomLevel * 100)}%</span>
                <button className="btn btn-sm btn-outline-secondary" onClick={() => setZoomLevel(Math.min(5, zoomLevel + 0.5))}>
                  <i className="fas fa-search-plus"></i>
                </button>
              </div>
            </div>
          )}

          {viewMode === 'list' && renderCellList()}
          {viewMode === 'map' && renderHeatMap()}

          <div className="cell-details">
            {selectedCell ? (
              <div className="selected-cell-info">
                <h3>تفاصيل الخلية</h3>
                <p><strong>المعرف:</strong> {selectedCell.cell_id}</p>
                <p><strong>الإحداثيات:</strong> {selectedCell.coordinates}</p>
                <p><strong>نوع البيانات:</strong> {selectedCell.data_type}</p>
                <button className="btn btn-primary" onClick={openCellDetails}>
                  فتح الخلية
                </button>
              </div>
            ) : (
              <div className="no-selection">
                <p>اختر خلية لعرض التفاصيل</p>
              </div>
            )}
            <div className="action-buttons">
              <button className="btn btn-success" onClick={createNewCell}>
                إنشاء خلية جديدة
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HexagonalDashboard;
