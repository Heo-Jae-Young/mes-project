import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import Header from './components/layout/Header';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CCPLogsPage from './pages/CCPLogsPage';
import ProductionPage from './pages/ProductionPage';
import ProductsPage from './pages/ProductsPage';
import MaterialsPage from './pages/MaterialsPage';
import MaterialDetailPage from './pages/MaterialDetailPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Toaster position="top-right" />
          
          <Routes>
            {/* 로그인 페이지 (공개) */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* 보호된 라우트들 */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } />
            
            <Route path="/ccp-logs" element={
              <ProtectedRoute>
                <CCPLogsPage />
              </ProtectedRoute>
            } />
            
            <Route path="/production" element={
              <ProtectedRoute>
                <ProductionPage />
              </ProtectedRoute>
            } />
            
            <Route path="/products" element={
              <ProtectedRoute>
                <ProductsPage />
              </ProtectedRoute>
            } />
            
            <Route path="/materials" element={
              <ProtectedRoute>
                <MaterialsPage />
              </ProtectedRoute>
            } />
            
            <Route path="/materials/:id" element={
              <ProtectedRoute>
                <MaterialDetailPage />
              </ProtectedRoute>
            } />
            
            {/* 기본 경로는 대시보드로 리디렉션 */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* 404 페이지 */}
            <Route path="*" element={
              <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-gray-900">404</h1>
                  <p className="mt-2 text-gray-600">페이지를 찾을 수 없습니다.</p>
                </div>
              </div>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
