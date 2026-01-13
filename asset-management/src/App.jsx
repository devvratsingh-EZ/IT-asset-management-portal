import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { LoginScreen } from './components/auth';
import { Dashboard } from './components/dashboard';
import { AssetAddition } from './components/assetAddition';
import { SidePanel } from './components/layout';
import { APP_CONFIG } from './data/constants';
import { Summary } from './components/summary';

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
    return 'summary';
  };

  const handleNavigate = (page) => {
    if (page === 'addition') {
      navigate('/asset_addition');
    } else if (page === 'details') {
      navigate('/asset_assignment');
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

  // Verify token on app load
  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem('authToken');
      const expiresAt = localStorage.getItem('tokenExpiry');

      if (!token || !expiresAt) {
        setIsLoading(false);
        return;
      }

      // Check if token expired locally first
      if (new Date(expiresAt) < new Date()) {
        console.log('Token expired locally');
        handleLogout();
        setIsLoading(false);
        return;
      }

      // Verify with backend
      try {
        const response = await fetch(`${APP_CONFIG.apiBaseUrl}/auth/verify`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();

        if (data.valid) {
          setIsAuthenticated(true);
          setCurrentUser(data.full_name || data.username);
        } else {
          handleLogout();
        }
      } catch (error) {
        console.error('Token verification failed:', error);
        // Keep logged in if backend is unreachable but token not expired
        const storedUser = localStorage.getItem('currentUser');
        if (storedUser) {
          setIsAuthenticated(true);
          setCurrentUser(storedUser);
        }
      }
      setIsLoading(false);
    };

    verifyToken();

    // Set up expiry checker (every minute)
    const expiryChecker = setInterval(() => {
      const expiresAt = localStorage.getItem('tokenExpiry');
      if (expiresAt && new Date(expiresAt) < new Date()) {
        console.log('Token expired - logging out');
        handleLogout();
        window.location.href = '/login';
      }
    }, 60000);

    return () => clearInterval(expiryChecker);
  }, []);

  const handleLogin = (username, token, expiresAt) => {
    setCurrentUser(username);
    setIsAuthenticated(true);
    localStorage.setItem('authToken', token);
    localStorage.setItem('currentUser', username);
    localStorage.setItem('tokenExpiry', expiresAt);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentUser('');
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('tokenExpiry');
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