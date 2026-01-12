import { useState } from 'react';
import { Icons } from '../common/Icons';
import { APP_CONFIG } from '../../data/constants';

const LoginScreen = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${APP_CONFIG.apiBaseUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        onLogin(data.full_name || data.username, data.token, data.expires_at);
      } else {
        setError(data.detail || 'Invalid username or password');
        setIsLoading(false);
      }
    } catch (err) {
      console.error('Login API error:', err);
      setError('Unable to connect to server. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="login-screen">
      <div className="login-screen__bg-gradient" />
      <div className="login-screen__bg-orb login-screen__bg-orb--left" />
      <div className="login-screen__bg-orb login-screen__bg-orb--right" />
      <div className="login-screen__bg-grid" />

      <div className="login-screen__container">
        <div className="login-screen__logo animate-fade-in">
          <div className="login-screen__logo-icon"><Icons.Laptop /></div>
          <h1 className="login-screen__title">IT Asset Management</h1>
          <p className="login-screen__subtitle">Secure Portal Access</p>
        </div>

        <div className="login-screen__card animate-slide-up">
          <form onSubmit={handleSubmit} className="login-screen__form">
            <div className="login-screen__field">
              <label className="login-screen__label">Username</label>
              <div className="login-screen__input-wrapper">
                <div className="login-screen__input-icon"><Icons.User /></div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="login-screen__input"
                  placeholder="Enter your username"
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="login-screen__field">
              <label className="login-screen__label">Password</label>
              <div className="login-screen__input-wrapper">
                <div className="login-screen__input-icon"><Icons.Lock /></div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="login-screen__input"
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
              </div>
            </div>

            {error && <div className="login-screen__error animate-shake">{error}</div>}

            <button type="submit" disabled={isLoading} className="login-screen__submit">
              {isLoading ? (
                <span className="login-screen__submit-loading">
                  <Icons.Spinner /> Authenticating...
                </span>
              ) : 'Sign In'}
            </button>
          </form>

          <div className="login-screen__demo-info">
            <p>Demo credentials: <span>itadmin / pass123</span></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;