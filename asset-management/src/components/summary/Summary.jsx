import { useState, useEffect, useRef } from 'react';
import { Icons } from '../common/Icons';
import { APP_CONFIG } from '../../data/constants';

/**
 * Filter Dropdown Component with checkboxes
 */
const FilterDropdown = ({ label, options, selectedValues, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleToggleAll = () => {
    if (selectedValues.length === options.length) {
      onChange([]);
    } else {
      onChange([...options]);
    }
  };

  const handleToggleOption = (option) => {
    if (selectedValues.includes(option)) {
      onChange(selectedValues.filter(v => v !== option));
    } else {
      onChange([...selectedValues, option]);
    }
  };

  const isAllSelected = selectedValues.length === options.length;
  const hasFilters = selectedValues.length > 0 && selectedValues.length < options.length;

  return (
    <div className="filter-dropdown" ref={dropdownRef}>
      <button
        className={`filter-dropdown__trigger ${hasFilters ? 'filter-dropdown__trigger--active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{label}</span>
        {hasFilters && <span className="filter-dropdown__badge">{selectedValues.length}</span>}
        <Icons.ChevronDown />
      </button>

      {isOpen && (
        <div className="filter-dropdown__menu">
          <label className="filter-dropdown__option filter-dropdown__option--all">
            <input
              type="checkbox"
              checked={isAllSelected}
              onChange={handleToggleAll}
            />
            <span>Select All</span>
          </label>
          <div className="filter-dropdown__divider" />
          <div className="filter-dropdown__options">
            {options.map((option) => (
              <label key={option} className="filter-dropdown__option">
                <input
                  type="checkbox"
                  checked={selectedValues.includes(option)}
                  onChange={() => handleToggleOption(option)}
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Summary Page Component
 */
const Summary = () => {
  const [summaryData, setSummaryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter states
  const [filters, setFilters] = useState({
    AssetType: [],
    Department: [],
    Brand: [],
    Model: []
  });

  useEffect(() => {
    fetchSummaryData();
  }, []);

  // Initialize filters when data loads
  useEffect(() => {
    if (summaryData.length > 0) {
      setFilters({
        AssetType: [...new Set(summaryData.map(r => r.AssetType))],
        Department: [...new Set(summaryData.map(r => r.Department))],
        Brand: [...new Set(summaryData.map(r => r.Brand))],
        Model: [...new Set(summaryData.map(r => r.Model))]
      });
    }
  }, [summaryData]);

  const fetchSummaryData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${APP_CONFIG.apiBaseUrl}/summary`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error('Failed to fetch summary data');

      const result = await response.json();
      if (result.success) {
        setSummaryData(result.data);
      } else {
        throw new Error(result.message || 'Failed to load summary');
      }
    } catch (err) {
      console.error('Error fetching summary:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Get unique values for each column
  const getUniqueValues = (key) => [...new Set(summaryData.map(r => r[key]))].sort();

  // Filter data based on selected filters
  const filteredData = summaryData.filter(row => {
    return (
      (filters.AssetType.length === 0 || filters.AssetType.includes(row.AssetType)) &&
      (filters.Department.length === 0 || filters.Department.includes(row.Department)) &&
      (filters.Brand.length === 0 || filters.Brand.includes(row.Brand)) &&
      (filters.Model.length === 0 || filters.Model.includes(row.Model))
    );
  });

  const updateFilter = (key, values) => {
    setFilters(prev => ({ ...prev, [key]: values }));
  };

  const clearAllFilters = () => {
    setFilters({
      AssetType: getUniqueValues('AssetType'),
      Department: getUniqueValues('Department'),
      Brand: getUniqueValues('Brand'),
      Model: getUniqueValues('Model')
    });
  };

  const hasActiveFilters = Object.keys(filters).some(key => {
    const allOptions = getUniqueValues(key);
    return filters[key].length > 0 && filters[key].length < allOptions.length;
  });

  if (loading) {
    return (
      <div className="summary">
        <div className="summary__loading">
          <Icons.Spinner />
          <span>Loading summary data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="summary">
        <div className="summary__error">
          <Icons.AlertCircle />
          <span>{error}</span>
          <button onClick={fetchSummaryData} className="summary__retry-btn">Retry</button>
        </div>
      </div>
    );
  }

  const totalAssets = filteredData.reduce((sum, row) => sum + row.Count, 0);
  const uniqueTypes = [...new Set(filteredData.map(row => row.AssetType))].length;
  const uniqueDepartments = [...new Set(filteredData.map(row => row.Department))].length;

  return (
    <div className="summary">
      <div className="summary__header">
        <h1 className="summary__title">Asset Summary</h1>
        <p className="summary__subtitle">Overview of all assets by type, department, brand, and model</p>
      </div>

      {/* Stats Cards */}
      <div className="summary__stats">
        <div className="summary__stat-card">
          <div className="summary__stat-icon summary__stat-icon--cyan">
            <Icons.Package />
          </div>
          <div className="summary__stat-content">
            <span className="summary__stat-value">{totalAssets}</span>
            <span className="summary__stat-label">Total Assets</span>
          </div>
        </div>
        <div className="summary__stat-card">
          <div className="summary__stat-icon summary__stat-icon--teal">
            <Icons.Cpu />
          </div>
          <div className="summary__stat-content">
            <span className="summary__stat-value">{uniqueTypes}</span>
            <span className="summary__stat-label">Asset Types</span>
          </div>
        </div>
        <div className="summary__stat-card">
          <div className="summary__stat-icon summary__stat-icon--emerald">
            <Icons.User />
          </div>
          <div className="summary__stat-content">
            <span className="summary__stat-value">{uniqueDepartments}</span>
            <span className="summary__stat-label">Departments</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="summary__filters">
        <div className="summary__filters-row">
          <FilterDropdown
            label="Asset Type"
            options={getUniqueValues('AssetType')}
            selectedValues={filters.AssetType}
            onChange={(values) => updateFilter('AssetType', values)}
          />
          <FilterDropdown
            label="Department"
            options={getUniqueValues('Department')}
            selectedValues={filters.Department}
            onChange={(values) => updateFilter('Department', values)}
          />
          <FilterDropdown
            label="Brand"
            options={getUniqueValues('Brand')}
            selectedValues={filters.Brand}
            onChange={(values) => updateFilter('Brand', values)}
          />
          <FilterDropdown
            label="Model"
            options={getUniqueValues('Model')}
            selectedValues={filters.Model}
            onChange={(values) => updateFilter('Model', values)}
          />
          {hasActiveFilters && (
            <button className="summary__clear-filters" onClick={clearAllFilters}>
              <Icons.X />
              Clear Filters
            </button>
          )}
        </div>
        {hasActiveFilters && (
          <p className="summary__filter-info">
            Showing {filteredData.length} of {summaryData.length} rows
          </p>
        )}
      </div>

      {/* Summary Table */}
      <div className="summary__table-container">
        <table className="summary__table">
          <thead>
            <tr className="summary__table-header-row">
              <th className="summary__table-header">Asset Type</th>
              <th className="summary__table-header">Department</th>
              <th className="summary__table-header">Brand</th>
              <th className="summary__table-header">Model</th>
              <th className="summary__table-header summary__table-header--right">Count</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.length === 0 ? (
              <tr>
                <td colSpan="5" className="summary__empty">
                  <Icons.Package />
                  <span>No data matches the selected filters</span>
                </td>
              </tr>
            ) : (
              filteredData.map((row, index) => (
                <tr key={index} className="summary__table-row">
                  <td className="summary__table-cell">
                    <span className="summary__asset-type">{row.AssetType}</span>
                  </td>
                  <td className="summary__table-cell">
                    <span className={`summary__department ${row.Department === 'Not Assigned' ? 'summary__department--unassigned' : ''}`}>
                      {row.Department}
                    </span>
                  </td>
                  <td className="summary__table-cell">{row.Brand}</td>
                  <td className="summary__table-cell">{row.Model}</td>
                  <td className="summary__table-cell summary__table-cell--right">
                    <span className="summary__count">{row.Count}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Summary;