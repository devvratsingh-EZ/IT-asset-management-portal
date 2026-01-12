import { Icons } from '../common/Icons';

/**
 * Dashboard Header Component
 * Displays app branding and user controls
 * @param {string} user - Current logged in username
 * @param {function} onLogout - Callback for logout action
 */
const Header = ({ user, onLogout }) => {
  return (
    <header className="dashboard-header">
      <div className="dashboard-header__container">
        <div className="dashboard-header__content">
          {/* Logo */}
          <div className="dashboard-header__logo">
            <div className="dashboard-header__logo-icon">
              <Icons.Laptop />
            </div>
            <span className="dashboard-header__logo-text">
              Asset Portal
            </span>
          </div>
          
          {/* User Controls */}
          <div className="dashboard-header__controls">
            <span className="dashboard-header__welcome">
              Welcome, <span className="dashboard-header__username">{user}</span>
            </span>
            <button
              onClick={onLogout}
              className="dashboard-header__logout-btn"
            >
              <Icons.Logout />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
