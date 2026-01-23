import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { LoginScreen } from './components/auth';
import { Dashboard } from './components/dashboard';
import { AssetAddition } from './components/assetAddition';
import { SidePanel } from './components/layout';
import { APP_CONFIG } from './data/constants';
import { Summary } from './components/summary';
import { DeleteAsset } from './components/deleteAsset';
import { authService, tokenManager } from './services/api';

/**
 * Main Layout Component with Side Panel
 */
function MainLayout({ user, onLogout }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  const getActivePage = () => {
  if (location.pathname === '/asset_addition') return 'addition';
  if (location.pathname === '/asset_assignment') return 'details';
  if (location.pathname === '/summary') return 'summary';
  if (location.pathname === '/delete_asset') return 'delete';
  return 'summary';
};

  const handleNavigate = (page) => {
  if (page === 'addition') {
    navigate('/asset_addition');
  } else if (page === 'details') {
    navigate('/asset_assignment');
  } else if (page === 'delete') {
    navigate('/delete_asset');
  } else {
    navigate('/summary');
  }
  if (window.innerWidth < 768) setSidebarOpen(false);
};

  const handleLogoutClick = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="app-layout">
      <SidePanel
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        activePage={getActivePage()}
        onNavigate={handleNavigate}
      />
      <div className={`app-layout__main ${sidebarOpen ? 'app-layout__main--sidebar-open' : ''}`}>
        <div className="dashboard__bg-gradient" />
        <div className="dashboard__bg-grid" />
        <header className="app-header">
          <div className="app-header__content">
            <div className="app-header__logo">
              <span className="app-header__logo-text">{APP_CONFIG.appName}</span>
            </div>
            <div className="app-header__user">
              <span className="app-header__username">Welcome, {user}</span>
              <button onClick={handleLogoutClick} className="app-header__logout-btn">Logout</button>
            </div>
          </div>
        </header>
        <main className="app-content">
          <Routes>
            <Route path="/summary" element={<Summary />} />
            <Route path="/asset_assignment" element={<Dashboard user={user} onLogout={handleLogoutClick} hideHeader={true} />} />
            <Route path="/asset_addition" element={<AssetAddition />} />
            <Route path="*" element={<Navigate to="/summary" replace />} />
            <Route path="/delete_asset" element={<DeleteAsset />} />
        </Routes>
        </main>
        <footer className="app-footer">
          <p>© {APP_CONFIG.companyName} | Internal Use Only</p>
        </footer>
      </div>
    </div>
  );
}

/**
 * Main Application Component with JWT Auth
 */
function AssetManagementApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // Verify token on app load and restore session from refresh token if available
  useEffect(() => {
    const restoreSession = async () => {
      try {
        // Attempt to verify/restore token
        const result = await authService.verifyToken();
        
        if (result && result.valid) {
          setIsAuthenticated(true);
          setCurrentUser(result.full_name || result.username || 'User');
          console.log('%c[SESSION] Session restored on page load', 'color: #0ea5e9;', result);
        } else {
          // Session expired or refresh token not available
          handleLogout();
          console.log('%c[SESSION] No valid session found - user needs to login', 'color: orange;');
        }
      } catch (error) {
        console.error('%c[SESSION] Session restoration failed', 'color: red;', error);
        handleLogout();
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();

    // Listen for auth:logout event from api.js (when refresh token expires)
    const handleForceLogout = () => {
      handleLogout();
      window.location.href = '/login';
    };
    window.addEventListener('auth:logout', handleForceLogout);

    return () => {
      window.removeEventListener('auth:logout', handleForceLogout);
    };
  }, []);

  const handleLogin = (username, token, expiresAt) => {
    tokenManager.setToken(token, expiresAt);
    setCurrentUser(username);
    setIsAuthenticated(true);
    // No localStorage for tokens anymore
  };

  const handleLogout = () => {
    tokenManager.clearToken();
    setIsAuthenticated(false);
    setCurrentUser('');
  };

  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: '#0a1929',
        color: '#22d3ee'
      }}>
        Verifying session...
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ?
              <Navigate to="/summary" replace /> :
              <LoginScreen onLogin={handleLogin} />
          }
        />
        <Route
          path="/*"
          element={
            isAuthenticated ?
              <MainLayout user={currentUser} onLogout={handleLogout} /> :
              <Navigate to="/login" replace />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default AssetManagementApp;