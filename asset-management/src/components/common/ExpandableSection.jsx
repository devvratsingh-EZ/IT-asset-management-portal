import { useState } from 'react';
import { Icons } from './Icons';

/**
 * Expandable/collapsible section component
 * @param {string} title - Section title
 * @param {React.Component} icon - Icon component to display
 * @param {React.ReactNode} children - Content to display when expanded
 * @param {boolean} defaultExpanded - Whether section is expanded by default
 * @param {boolean} disabled - Whether section is disabled/locked
 * @param {string} disabledMessage - Message to show when hovering disabled section
 */
const ExpandableSection = ({ title, icon: Icon, children, defaultExpanded = false, disabled = false, disabledMessage }) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded && !disabled);
  
  return (
    <div 
      className={`expandable-section ${disabled ? 'expandable-section--disabled' : ''}`}
      title={disabled ? disabledMessage : undefined}
    >
      <button
        onClick={() => !disabled && setIsExpanded(!isExpanded)}
        className="expandable-section__header"
        aria-expanded={isExpanded}
        disabled={disabled}
      >
        <div className="expandable-section__title-wrapper">
          <div className="expandable-section__icon">
            <Icon />
          </div>
          <span className="expandable-section__title">{title}</span>
        </div>
        <div className={`expandable-section__chevron ${isExpanded ? 'expandable-section__chevron--expanded' : ''}`}>
          <Icons.ChevronDown />
        </div>
      </button>
      <div className={`expandable-section__content ${isExpanded && !disabled ? 'expandable-section__content--expanded' : ''}`}>
        <div className="expandable-section__content-inner">
          {children}
        </div>
      </div>
    </div>
  );
};

export default ExpandableSection;
