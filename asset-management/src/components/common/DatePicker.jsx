import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Icons } from './Icons';

const DatePicker = ({ value, onChange, label }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(value ? new Date(value) : new Date());
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });
  const containerRef = useRef(null);
  const triggerRef = useRef(null);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      const portalDropdown = document.querySelector('.date-picker__dropdown--portal');
      if (
        containerRef.current && 
        !containerRef.current.contains(event.target) &&
        (!portalDropdown || !portalDropdown.contains(event.target))
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const updatePosition = () => {
      if (isOpen && triggerRef.current) {
        const rect = triggerRef.current.getBoundingClientRect();
        const dropdownHeight = 320;
        const dropdownWidth = 280;
        const spaceBelow = window.innerHeight - rect.bottom;
        const spaceRight = window.innerWidth - rect.left;
        
        let top, left;
        
        // Vertical positioning - flip above if not enough space below
        if (spaceBelow < dropdownHeight && rect.top > dropdownHeight) {
          top = rect.top - dropdownHeight - 8;
        } else {
          top = rect.bottom + 8;
        }
        
        // Horizontal positioning - align right if not enough space
        if (spaceRight < dropdownWidth) {
          left = rect.right - dropdownWidth;
        } else {
          left = rect.left;
        }
        
        setDropdownPosition({ top, left });
      }
    };

    if (isOpen) {
      updatePosition();
      window.addEventListener('scroll', updatePosition, true);
      window.addEventListener('resize', updatePosition);
    }

    return () => {
      window.removeEventListener('scroll', updatePosition, true);
      window.removeEventListener('resize', updatePosition);
    };
  }, [isOpen]);

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const daysOfWeek = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();

    const days = [];
    for (let i = 0; i < startingDay; i++) {
      days.push(null);
    }
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }
    return days;
  };

  const formatDate = (date) => {
    if (!date) return '';
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const handlePrevMonth = (e) => {
    e.stopPropagation();
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const handleNextMonth = (e) => {
    e.stopPropagation();
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const handleDateSelect = (date) => {
    onChange(date);
    setIsOpen(false);
  };

  const isSelected = (date) => {
    if (!date || !value) return false;
    return date.toDateString() === value.toDateString();
  };

  const isToday = (date) => {
    if (!date) return false;
    return date.toDateString() === new Date().toDateString();
  };

  const days = getDaysInMonth(currentMonth);

  const dropdownContent = (
    <div 
      ref={dropdownRef}
      className="date-picker__dropdown date-picker__dropdown--portal"
      style={{ 
        position: 'fixed',
        top: dropdownPosition.top, 
        left: dropdownPosition.left,
        zIndex: 99999
      }}
    >
      <div className="date-picker__header">
        <button type="button" onClick={handlePrevMonth} className="date-picker__nav-btn">
          <Icons.ChevronLeft />
        </button>
        <span className="date-picker__month-year">
          {months[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </span>
        <button type="button" onClick={handleNextMonth} className="date-picker__nav-btn">
          <Icons.ChevronRight />
        </button>
      </div>

      <div className="date-picker__weekdays">
        {daysOfWeek.map((day) => (
          <div key={day} className="date-picker__weekday">{day}</div>
        ))}
      </div>

      <div className="date-picker__days">
        {days.map((date, index) => (
          <button
            key={index}
            type="button"
            onClick={() => date && handleDateSelect(date)}
            disabled={!date}
            className={`date-picker__day ${
              isSelected(date) ? 'date-picker__day--selected' : ''
            } ${isToday(date) ? 'date-picker__day--today' : ''} ${
              !date ? 'date-picker__day--empty' : ''
            }`}
          >
            {date ? date.getDate() : ''}
          </button>
        ))}
      </div>

      <div className="date-picker__footer">
        <button type="button" onClick={() => handleDateSelect(new Date())} className="date-picker__today-btn">
          Today
        </button>
      </div>
    </div>
  );

  return (
    <div className="date-picker" ref={containerRef}>
      {label && <label className="date-picker__label">{label}</label>}
      
      <button
        type="button"
        ref={triggerRef}
        onClick={() => setIsOpen(!isOpen)}
        className="date-picker__trigger"
      >
        <Icons.Calendar />
        <span className={value ? 'date-picker__value' : 'date-picker__placeholder'}>
          {value ? formatDate(value) : 'Select date'}
        </span>
      </button>

      {isOpen && createPortal(dropdownContent, document.body)}
    </div>
  );
};

export default DatePicker;