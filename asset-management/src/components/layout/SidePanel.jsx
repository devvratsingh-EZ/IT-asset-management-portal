import { Icons } from '../common/Icons';

/**
 * Collapsible Side Panel Navigation Component
 * Provides navigation between Asset Details and Asset Addition pages
 * @param {boolean} isOpen - Whether the panel is expanded
 * @param {function} onToggle - Callback to toggle panel state
 * @param {string} activePage - Currently active page ('details' | 'addition')
 * @param {function} onNavigate - Callback for navigation
 */
const SidePanel = ({ isOpen, onToggle, activePage, onNavigate }) => {
  const navItems = [
    {
      id: 'details',
      label: 'Asset Details',
      icon: Icons.ClipboardList,
      description: 'View & manage existing assets'
    },
    {
      id: 'addition',
      label: 'New Asset',
      icon: Icons.Plus,
      description: 'Add newly purchased assets'
    }
  ];

  return (
    <>
      {/* Mobile menu toggle button */}
      <button
        onClick={onToggle}
        className="side-panel__mobile-toggle"
        aria-label="Toggle navigation menu"
      >
        <Icons.Menu />
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="side-panel__overlay"
          onClick={onToggle}
        />
      )}

      {/* Side Panel */}
      <aside className={`side-panel ${isOpen ? 'side-panel--open' : 'side-panel--closed'}`}>
        {/* Panel Header */}
        <div className="side-panel__header">
          {isOpen && (
            <div className="side-panel__logo">
              <div className="side-panel__logo-icon">
                <Icons.Package />
              </div>
              <span className="side-panel__logo-text">Asset Manager</span>
            </div>
          )}
          <button
            onClick={onToggle}
            className="side-panel__toggle-btn"
            aria-label={isOpen ? 'Collapse panel' : 'Expand panel'}
          >
            {isOpen ? <Icons.ChevronLeft /> : <Icons.ChevronRight />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="side-panel__nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`side-panel__nav-item ${isActive ? 'side-panel__nav-item--active' : ''}`}
                title={!isOpen ? item.label : undefined}
              >
                <div className="side-panel__nav-icon">
                  <Icon />
                </div>
                {isOpen && (
                  <div className="side-panel__nav-content">
                    <span className="side-panel__nav-label">{item.label}</span>
                    <span className="side-panel__nav-description">{item.description}</span>
                  </div>
                )}
                {isActive && <div className="side-panel__nav-indicator" />}
              </button>
            );
          })}
        </nav>

        {/* Panel Footer */}
        {isOpen && (
          <div className="side-panel__footer">
            <p className="side-panel__footer-text">
              IT Asset Management
            </p>
          </div>
        )}
      </aside>
    </>
  );
};

export default SidePanel;
