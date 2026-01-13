import { useState, useEffect } from 'react';
import { Icons } from '../common/Icons';
import { APP_CONFIG } from '../../data/constants';

/**
 * Summary Page Component
 * Displays aggregated asset data from SummaryData view
 */
const Summary = () => {
  const [summaryData, setSummaryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSummaryData();
  }, []);

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

      if (!response.ok) {
        throw new Error('Failed to fetch summary data');
      }

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
          <button onClick={fetchSummaryData} className="summary__retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Calculate totals
  const totalAssets = summaryData.reduce((sum, row) => sum + row.Count, 0);
  const uniqueTypes = [...new Set(summaryData.map(row => row.AssetType))].length;
  const uniqueDepartments = [...new Set(summaryData.map(row => row.Department))].length;

  return (
    <div className="summary">
      <div className="summary__header">
        <h1 className="summary__title">Asset Summary</h1>
        <p className="summary__subtitle">Overview of all assets by type, department, brand and model</p>
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
            {summaryData.length === 0 ? (
              <tr>
                <td colSpan="5" className="summary__empty">
                  <Icons.Package />
                  <span>No asset data available</span>
                </td>
              </tr>
            ) : (
              summaryData.map((row, index) => (
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