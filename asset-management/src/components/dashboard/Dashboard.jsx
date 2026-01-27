import { useState, useMemo, useRef, useEffect } from 'react';
import Header from './Header';
import Specifications from './Specifications';
import CurrentEmployee from './CurrentEmployee';
import AssignmentHistory from './AssignmentHistory';
import UpdateAssetForm from './UpdateAssetForm';
import UploadsSection from './UploadsSection';
import SuccessNotification from './SuccessNotification';
import { ExpandableSection } from '../common';
import { Icons } from '../common/Icons';
import { assetService, employeeService } from '../../services/api';

/**
 * Searchable Asset Selector Component
 */
const SearchableAssetSelector = ({ selectedAssetId, onSelectAsset, assetIds, isLoading }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef(null);

  const filteredAssets = useMemo(() => {
    if (!searchTerm) return assetIds;
    return assetIds.filter(id => 
      id.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [assetIds, searchTerm]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (id) => {
    onSelectAsset(id);
    setSearchTerm('');
    setIsOpen(false);
  };

  const handleClear = () => {
    onSelectAsset('');
    setSearchTerm('');
  };

  return (
    <ExpandableSection
      title="Select Asset"
      icon={Icons.Search}
      defaultExpanded={true}
    >
      <div className="asset-selector-search" ref={dropdownRef}>
        <div className="asset-selector-search__input-wrapper">
          <Icons.Search />
          <input
            type="text"
            value={isOpen ? searchTerm : (selectedAssetId || '')}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              if (!isOpen) setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            placeholder={isLoading ? "Loading assets..." : "Search or select an Asset ID..."}
            className="asset-selector-search__input"
            disabled={isLoading}
          />
          {selectedAssetId && !isOpen && (
            <button 
              onClick={handleClear}
              className="asset-selector-search__clear"
              type="button"
            >
              <Icons.X />
            </button>
          )}
          <button 
            onClick={() => setIsOpen(!isOpen)}
            className="asset-selector-search__toggle"
            type="button"
          >
            <Icons.ChevronDown />
          </button>
        </div>

        {isOpen && (
          <div className="asset-selector-search__dropdown">
            {filteredAssets.length > 0 ? (
              filteredAssets.map(id => (
                <button
                  key={id}
                  onClick={() => handleSelect(id)}
                  className={`asset-selector-search__option ${
                    selectedAssetId === id ? 'asset-selector-search__option--selected' : ''
                  }`}
                >
                  <Icons.Package />
                  <span>{id}</span>
                  {selectedAssetId === id && <Icons.Check />}
                </button>
              ))
            ) : (
              <div className="asset-selector-search__no-results">
                {isLoading ? "Loading..." : `No assets found matching "${searchTerm}"`}
              </div>
            )}
          </div>
        )}
      </div>
    </ExpandableSection>
  );
};

/**
 * Main Dashboard Component - Now fetches from API
 */
const Dashboard = ({ user, onLogout, hideHeader = false }) => {
  // Data state
  const [allAssets, setAllAssets] = useState({});
  const [allAssignmentHistory, setAllAssignmentHistory] = useState({});
  const [employees, setEmployees] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  
  // Selection state
  const [selectedAssetId, setSelectedAssetId] = useState('');
  
  // UI state
  const [showSuccess, setShowSuccess] = useState(false);
  const [updateSummary, setUpdateSummary] = useState(null);

  // Update form state
  const [updateFormState, setUpdateFormState] = useState({ 
    assignedTo: '', 
    repairStatus: false,
    repairDetails: '',
    tempAssetId: ''
  });
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const [repairFormState, setRepairFormState] = useState({ repairDetails: '', tempAssetId: '' });

  // Fetch data from API on mount
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Fetch assets
        const assetsData = await assetService.getAssets();
        if (assetsData.success) {
          setAllAssets(assetsData.data);
        }

        // Fetch employees
        const employeesData = await employeeService.getEmployees();
        if (employeesData.success) {
          setEmployees(employeesData.data);
        }

        // Fetch assignment history
        const historyData = await assetService.getAllAssignmentHistory();
        if (historyData.success) {
          setAllAssignmentHistory(historyData.data);
        }
      } catch (error) {
        console.error('Failed to fetch data from API:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const assetIds = useMemo(() => Object.keys(allAssets), [allAssets]);
  
  const assetData = useMemo(() => {
    return selectedAssetId ? allAssets[selectedAssetId] : null;
  }, [selectedAssetId, allAssets]);
  
  const assignmentHistory = useMemo(() => {
    return selectedAssetId ? (allAssignmentHistory[selectedAssetId] || []) : [];
  }, [selectedAssetId, allAssignmentHistory]);
  
  const isAssetSelected = !!selectedAssetId && !!assetData;

  // Sync update form state when asset selection changes
  useEffect(() => {
    if (assetData) {
      setUpdateFormState({
        assignedTo: assetData.assignedTo || '',
        repairStatus: assetData.repairStatus || false,
        repairDetails: '',
        tempAssetId: ''
      });
      setRepairFormState({ repairDetails: '', tempAssetId: '' });
    }
  }, [assetData]);

  const formatDate = (date) => {
    if (!date) return 'N/A';
    return new Date(date).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const currentEmployee = useMemo(() => {
    if (!assetData?.assignedTo) return null;
    return employees[assetData.assignedTo] || null;
  }, [assetData, employees]);

  const handleUpdateSubmit = async (updatedData) => {
    try {
      const result = await assetService.updateAsset(assetData.assetId, updatedData);
      
      if (result.success) {
        // Refresh data
        const assetsData = await assetService.getAssets();
        if (assetsData.success) {
          setAllAssets(assetsData.data);
        }
        
        const historyData = await assetService.getAllAssignmentHistory();
        if (historyData.success) {
          setAllAssignmentHistory(historyData.data);
        }
        
        setUpdateSummary({
          assetId: assetData.assetId,
          changes: Object.keys(updatedData).length
        });
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 3000);
      }
    } catch (error) {
      console.error('Failed to update asset:', error);
    }
  };

  const handleFormFieldChange = (field, value) => {
    setUpdateFormState(prev => ({ ...prev, [field]: value }));
  };

  const handleRepairDataChange = (repairData) => {
    setRepairFormState(repairData);
    setUpdateFormState(prev => ({
      ...prev,
      repairDetails: repairData.repairDetails,
      tempAssetId: repairData.tempAssetId
    }));
  };

  const handleSaveClick = () => {
    setShowConfirmModal(true);
  };

  const handleConfirmSave = async () => {
    setShowConfirmModal(false);
    
    try {
      const wasUnderRepair = assetData.repairStatus;
      const isNowUnderRepair = updateFormState.repairStatus;

      // Handle repair status changes
      if (!wasUnderRepair && isNowUnderRepair) {
        // Starting repair
        if (!updateFormState.repairDetails?.trim()) {
          alert('Please provide repair details');
          return;
        }
        
        const repairResult = await assetService.startRepair(
          assetData.assetId,
          updateFormState.repairDetails,
          updateFormState.tempAssetId || null
        );
        
        if (!repairResult.success) {
          alert('Failed to start repair');
          return;
        }
      } else if (wasUnderRepair && !isNowUnderRepair) {
        // Ending repair
        const endResult = await assetService.endRepair(assetData.assetId);
        if (!endResult.success) {
          alert('Failed to end repair');
          return;
        }
      }

      // Update assignment if not under repair or repair status unchanged
      if (!isNowUnderRepair || wasUnderRepair === isNowUnderRepair) {
        await handleUpdateSubmit({
          assignedTo: updateFormState.assignedTo,
          repairStatus: updateFormState.repairStatus
        });
      } else {
        // Refresh data after repair change
        const assetsData = await assetService.getAssets();
        if (assetsData.success) {
          setAllAssets(assetsData.data);
        }
        
        const historyData = await assetService.getAllAssignmentHistory();
        if (historyData.success) {
          setAllAssignmentHistory(historyData.data);
        }
        
        setUpdateSummary({
          assetId: assetData.assetId,
          changes: 1
        });
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 3000);
      }
    } catch (error) {
      console.error('Failed to save changes:', error);
      alert('Failed to save changes: ' + error.message);
    }
  };

  const disabledMessage = "Please select an Asset ID first to view this section";

  return (
    <div className="dashboard">
      {!hideHeader && <Header user={user} onLogout={onLogout} />}

      <div className="asset-addition">
        <div className="asset-addition__header">
          <h1 className="asset-addition__title">Asset Details & Update Portal</h1>
          <p className="asset-addition__subtitle">View and manage IT asset information</p>
        </div>

        {!isAssetSelected && (
          <div className="asset-addition__progress-notice">
            <Icons.ClipboardList />
            <span>Select an <strong>Asset ID</strong> above to view and manage asset details</span>
          </div>
        )}

        <div className="asset-addition__sections">
          <SearchableAssetSelector
            selectedAssetId={selectedAssetId}
            onSelectAsset={setSelectedAssetId}
            assetIds={assetIds}
            isLoading={isLoading}
          />

          <ExpandableSection
            title="Asset Overview"
            icon={Icons.Laptop}
            defaultExpanded={true}
            disabled={!isAssetSelected}
            disabledMessage={disabledMessage}
          >
            {isAssetSelected && (
              <div className="asset-overview__grid">
                <div className="asset-overview__item">
                  <p className="asset-overview__label">Asset ID</p>
                  <p className="asset-overview__value asset-overview__value--cyan">{assetData.assetId}</p>
                </div>
                <div className="asset-overview__item">
                  <p className="asset-overview__label">Serial Number</p>
                  <p className="asset-overview__value asset-overview__value--teal">{assetData.serialNumber}</p>
                </div>
                <div className="asset-overview__item">
                  <p className="asset-overview__label">Asset Type</p>
                  <p className="asset-overview__value asset-overview__value--emerald">{assetData.assetType}</p>
                </div>
                <div className="asset-overview__item">
                  <p className="asset-overview__label">{assetData.isRental ? 'Lease Expiry' : 'Warranty Expiry'}</p>
                  <p className="asset-overview__value asset-overview__value--amber">
                    {formatDate(assetData.isRental ? assetData.leaseExpiry : assetData.warrantyExpiry)}
                  </p>
                </div>
                <div className="asset-overview__item">
                  <p className="asset-overview__label">Rental Status</p>
                  <p className={`asset-overview__value ${assetData.isRental ? 'asset-overview__value--amber' : 'asset-overview__value--emerald'}`}>
                    {assetData.isRental ? 'Yes' : 'No'}
                  </p>
                </div>
              </div>
            )}
          </ExpandableSection>

          <ExpandableSection
            title="Specifications"
            icon={Icons.Cpu}
            defaultExpanded={false}
            disabled={!isAssetSelected}
            disabledMessage={disabledMessage}
          >
            {isAssetSelected && <Specifications specifications={assetData.specifications} />}
          </ExpandableSection>

          <ExpandableSection
            title="Current Assigned Employee"
            icon={Icons.User}
            defaultExpanded={true}
            disabled={!isAssetSelected}
            disabledMessage={disabledMessage}
          >
            {isAssetSelected && (
              <CurrentEmployee
                employee={currentEmployee}
                employeeId={assetData.assignedTo}
              />
            )}
          </ExpandableSection>

          <ExpandableSection
            title="Assignment History"
            icon={Icons.History}
            defaultExpanded={false}
            disabled={!isAssetSelected}
            disabledMessage={disabledMessage}
          >
            {isAssetSelected && <AssignmentHistory history={assignmentHistory} />}
          </ExpandableSection>

          <ExpandableSection
            title="Update Asset Information"
            icon={Icons.Edit}
            defaultExpanded={false}
            disabled={!isAssetSelected}
            disabledMessage={disabledMessage}
          >
            {isAssetSelected && (
              <UpdateAssetForm
                assetData={assetData}
                employees={employees}
                onFieldChange={handleFormFieldChange}
                formState={updateFormState}
                onRepairChange={handleRepairDataChange}
              />
            )}
          </ExpandableSection>

          <ExpandableSection
            title="Documents & Images"
            icon={Icons.Upload}
            defaultExpanded={false}
            disabled={!isAssetSelected}
            disabledMessage={disabledMessage}
          >
            {isAssetSelected && <UploadsSection assetId={assetData.assetId} />}
          </ExpandableSection>
        </div>

        {/* Save Changes Button - Outside all sections */}
        {isAssetSelected && (
          <div className="asset-addition__actions" style={{ marginTop: '1.5rem' }}>
            <button
              type="button"
              onClick={handleSaveClick}
              className="asset-addition__preview-btn"
            >
              <Icons.Check />
              Save Changes
            </button>
          </div>
        )}

        {/* Confirmation Modal */}
        {showConfirmModal && (
          <div className="data-preview-modal__overlay">
            <div className="data-preview-modal" style={{ maxWidth: '400px' }}>
              <div className="data-preview-modal__header">
                <div className="data-preview-modal__title-section">
                  <div className="data-preview-modal__icon">
                    <Icons.AlertCircle />
                  </div>
                  <div>
                    <h2 className="data-preview-modal__title">Confirm Changes</h2>
                    <p className="data-preview-modal__subtitle">Are you sure you want to save?</p>
                  </div>
                </div>
              </div>
              <div className="data-preview-modal__content">
                <p style={{ color: 'var(--color-text-secondary)' }}>
                  This will update the assignment and repair status for asset <strong style={{ color: 'var(--color-primary-light)' }}>{assetData?.assetId}</strong>.
                </p>
              </div>
              <div className="data-preview-modal__footer">
                <button
                  onClick={() => setShowConfirmModal(false)}
                  className="data-preview-modal__cancel-btn"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmSave}
                  className="data-preview-modal__confirm-btn"
                >
                  <Icons.Check />
                  Confirm
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <SuccessNotification isVisible={showSuccess} summary={updateSummary} />
    </div>
  );
};

export default Dashboard;