import { useState, useEffect } from 'react';
import { Icons } from '../common/Icons';
import { assetService } from '../../services/api';

/**
 * Confirmation Modal Component
 */
const DeleteConfirmModal = ({ isOpen, assetIds, onConfirm, onCancel, isDeleting }) => {
  if (!isOpen) return null;

  return (
    <div className="delete-modal__overlay">
      <div className="delete-modal">
        <div className="delete-modal__header">
          <div className="delete-modal__icon">
            <Icons.AlertCircle />
          </div>
          <h2 className="delete-modal__title">Confirm Deletion</h2>
        </div>
        <div className="delete-modal__content">
          <p className="delete-modal__warning">
            You are about to permanently delete <strong>{assetIds.length}</strong> asset(s). This action cannot be undone.
          </p>
          <div className="delete-modal__asset-list">
            <p className="delete-modal__list-label">Assets to be deleted:</p>
            <ul>
              {assetIds.map(id => (
                <li key={id}>{id}</li>
              ))}
            </ul>
          </div>
        </div>
        <div className="delete-modal__footer">
          <button 
            className="delete-modal__cancel-btn" 
            onClick={onCancel}
            disabled={isDeleting}
          >
            Cancel
          </button>
          <button 
            className="delete-modal__confirm-btn" 
            onClick={onConfirm}
            disabled={isDeleting}
          >
            {isDeleting ? (
              <>
                <Icons.Spinner />
                Deleting...
              </>
            ) : (
              <>
                <Icons.X />
                Delete Assets
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * Delete Asset Page Component
 */
const DeleteAsset = () => {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIds, setSelectedIds] = useState([]);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [notification, setNotification] = useState({ show: false, success: false, message: '', deletedIds: [] });

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      setLoading(true);
      const result = await assetService.getAssets();

      if (result.success) {
        // Convert object to array
        const assetArray = Object.values(result.data);
        setAssets(assetArray);
      } else {
        throw new Error(result.message || 'Failed to load assets');
      }
    } catch (err) {
      console.error('Error fetching assets:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredAssets = assets.filter(asset =>
    asset.assetId.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelectAll = () => {
    if (selectedIds.length === filteredAssets.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredAssets.map(a => a.assetId));
    }
  };

  const handleSelectOne = (assetId) => {
    if (selectedIds.includes(assetId)) {
      setSelectedIds(selectedIds.filter(id => id !== assetId));
    } else {
      setSelectedIds([...selectedIds, assetId]);
    }
  };

  const handleDeleteClick = () => {
    if (selectedIds.length === 0) return;
    setShowConfirmModal(true);
  };

  const handleConfirmDelete = async () => {
  try {
    setIsDeleting(true);
    const response = await assetService.bulkDeleteAssets(selectedIds);
    
    if (!response || !response.success) {
      throw new Error(response?.detail || response?.message || 'Deletion failed');
    }

    const deletedIds = [...selectedIds];
    setAssets(assets.filter(a => !selectedIds.includes(a.assetId)));
    setSelectedIds([]);
    setShowConfirmModal(false);
    
    // Show success notification
    setNotification({
      show: true,
      success: true,
      message: `Successfully deleted ${deletedIds.length} asset(s)`,
      deletedIds
    });
    
    // Auto-hide after 5 seconds
    setTimeout(() => setNotification(prev => ({ ...prev, show: false })), 5000);
    
  } catch (err) {
    console.error('Error deleting assets:', err);
    setShowConfirmModal(false);
    
    // Show error notification
    setNotification({
      show: true,
      success: false,
      message: `Deletion failed: ${err.message}`,
      deletedIds: []
    });
    
    setTimeout(() => setNotification(prev => ({ ...prev, show: false })), 5000);
  } finally {
    setIsDeleting(false);
  }
};

  if (loading) {
    return (
      <div className="delete-asset">
        <div className="delete-asset__loading">
          <Icons.Spinner />
          <span>Loading assets...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="delete-asset">
        <div className="delete-asset__error">
          <Icons.AlertCircle />
          <span>{error}</span>
          <button onClick={fetchAssets} className="delete-asset__retry-btn">Retry</button>
        </div>
      </div>
    );
  }

  const isAllSelected = filteredAssets.length > 0 && selectedIds.length === filteredAssets.length;

  return (
    <div className="delete-asset">
      <div className="delete-asset__header">
        <h1 className="delete-asset__title">Delete Assets</h1>
        <p className="delete-asset__subtitle">Select assets to permanently remove from the system</p>
      </div>

      {/* Search Bar */}
      <div className="delete-asset__search">
        <div className="delete-asset__search-wrapper">
          <Icons.Search />
          <input
            type="text"
            placeholder="Search by Asset ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="delete-asset__search-input"
          />
          {searchTerm && (
            <button 
              className="delete-asset__search-clear"
              onClick={() => setSearchTerm('')}
            >
              <Icons.X />
            </button>
          )}
        </div>
        {selectedIds.length > 0 && (
          <span className="delete-asset__selected-count">
            {selectedIds.length} asset(s) selected
          </span>
        )}
      </div>

      {/* Assets Table */}
      <div className="delete-asset__table-container">
        <table className="delete-asset__table">
          <thead>
            <tr className="delete-asset__table-header-row">
              <th className="delete-asset__table-header delete-asset__table-header--checkbox">
                <input
                  type="checkbox"
                  checked={isAllSelected}
                  onChange={handleSelectAll}
                  disabled={filteredAssets.length === 0}
                />
              </th>
              <th className="delete-asset__table-header">Asset ID</th>
              <th className="delete-asset__table-header">Asset Type</th>
              <th className="delete-asset__table-header">Brand</th>
              <th className="delete-asset__table-header">Model</th>
              <th className="delete-asset__table-header">Assigned To</th>
            </tr>
          </thead>
          <tbody>
            {filteredAssets.length === 0 ? (
              <tr>
                <td colSpan="6" className="delete-asset__empty">
                  <Icons.Package />
                  <span>{searchTerm ? 'No assets match your search' : 'No assets available'}</span>
                </td>
              </tr>
            ) : (
              filteredAssets.map((asset) => (
                <tr 
                  key={asset.assetId} 
                  className={`delete-asset__table-row ${selectedIds.includes(asset.assetId) ? 'delete-asset__table-row--selected' : ''}`}
                >
                  <td className="delete-asset__table-cell delete-asset__table-cell--checkbox">
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(asset.assetId)}
                      onChange={() => handleSelectOne(asset.assetId)}
                    />
                  </td>
                  <td className="delete-asset__table-cell">
                    <span className="delete-asset__asset-id">{asset.assetId}</span>
                  </td>
                  <td className="delete-asset__table-cell">{asset.assetType}</td>
                  <td className="delete-asset__table-cell">{asset.specifications?.brand || '-'}</td>
                  <td className="delete-asset__table-cell">{asset.specifications?.model || '-'}</td>
                  <td className="delete-asset__table-cell">
                    {asset.assignedTo ? (
                      <span className="delete-asset__assigned">{asset.assignedTo}</span>
                    ) : (
                      <span className="delete-asset__unassigned">Not Assigned</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Delete Button */}
      <div className="delete-asset__actions">
        <button
          className="delete-asset__delete-btn"
          onClick={handleDeleteClick}
          disabled={selectedIds.length === 0}
        >
          <Icons.X />
          Delete Selected Assets
        </button>
      </div>


      {/* Notification */}
        {notification.show && (
        <div className={`delete-notification ${notification.success ? 'delete-notification--success' : 'delete-notification--error'}`}>
            <div className="delete-notification__content">
            <div className={`delete-notification__icon ${notification.success ? 'delete-notification__icon--success' : 'delete-notification__icon--error'}`}>
                {notification.success ? <Icons.Check /> : <Icons.AlertCircle />}
            </div>
            <div>
                <p className="delete-notification__title">
                {notification.success ? 'Deletion Successful' : 'Deletion Failed'}
                </p>
                <p className="delete-notification__message">{notification.message}</p>
                {notification.success && notification.deletedIds.length > 0 && (
                <p className="delete-notification__ids">
                    IDs: {notification.deletedIds.join(', ')}
                </p>
                )}
            </div>
            <button 
                className="delete-notification__close"
                onClick={() => setNotification(prev => ({ ...prev, show: false }))}
            >
                <Icons.X />
            </button>
            </div>
        </div>
        )}

      {/* Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={showConfirmModal}
        assetIds={selectedIds}
        onConfirm={handleConfirmDelete}
        onCancel={() => setShowConfirmModal(false)}
        isDeleting={isDeleting}
      />
    </div>
  );
};

export default DeleteAsset;