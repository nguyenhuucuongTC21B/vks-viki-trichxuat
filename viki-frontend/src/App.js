import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

// URL logo ngành Kiểm sát 
const logoUrl = "https://upload.wikimedia.org/wikipedia/vi/thumb/b/ba/Ph%C3%B9_hi%E1%BB%87u_Vi%E1%BB%87n_ki%E1%BB%83m_s%C3%A1t_nh%C3%A2n_d%C3%A2n.svg/1004px-Ph%C3%B9_hi%E1%BB%87u_Vi%E1%BB%87n_ki%E1%BB%83m_s%C3%A1t_nh%C3%A2n_d%C3%A2n.svg.png";

function App() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setFiles(event.target.files);
  };

  const handleProcess = async () => {
    if (files.length === 0) {
      setError('Vui lòng chọn ít nhất một file.');
      return;
    }

    setIsLoading(true);
    setError('');
    setResults([]);

    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }

    try {
  // Xác định địa chỉ API: nếu đang ở môi trường online thì dùng địa chỉ online,
  // nếu không thì dùng địa chỉ trên máy (localhost)
  const apiUrl = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";
  const response = await axios.post(`${apiUrl}/trich-xuat/`, formData);
  setResults(response.data);
} catch (err) {
      setError('Lỗi: Không thể kết nối tới máy chủ hoặc không trích xuất được dữ liệu.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      {/* --- PHẦN LOGO MỚI --- */}
      <img src={logoUrl} alt="Logo Viện Kiểm Sát" className="logo" />

      <h1>Hệ thống trích xuất hồ sơ tố tụng VKSND TP ĐÀ NẴNG - ViKi</h1>

      <div className="upload-section">
        <input type="file" multiple onChange={handleFileChange} />
      </div>

      <button className="process-button" onClick={handleProcess} disabled={isLoading || files.length === 0}>
        {isLoading ? 'Đang xử lý...' : 'Bắt đầu trích xuất'}
      </button>

      {error && <p className="status-message error">{error}</p>}

      {results.length > 0 && (
        <table className="results-table">
          <thead>
            <tr>
              <th>Số hồ sơ</th>
              <th>Tội danh</th>
              <th>Bị cáo</th>
              <th>Người bị hại</th>
              <th>Ngày khởi tố</th>
              <th>Cơ quan ĐT</th>
              <th>Tình trạng</th>
            </tr>
          </thead>
          <tbody>
            {results.map((item, index) => (
              <tr key={index}>
                <td>{item['Số hồ sơ']}</td>
                <td>{item['Tội danh']}</td>
                <td>{item['Bị cáo']}</td>
                <td>{item['Người bị hại']}</td>
                <td>{item['Thời gian khởi tố']}</td>
                <td>{item['Cơ quan điều tra']}</td>
                <td>{item['Tình trạng xử lý']}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* --- PHẦN FOOTER MỚI --- */}
      <footer>
        <p>Thiết kế bởi Nguyễn Hữu Cường - Chuyên viên Cơ yếu CCN1 | Liên hệ: 0905 6666 24 | © 2025 Bản quyền thuộc về VKSND TP ĐÀ NẴNG.</p>
      </footer>
    </div>
  );
}

export default App;
