import { useState, useEffect } from 'react';
import { Icons } from '../common/Icons';
import { assetService } from '../../services/api';

const UpdateAssetForm = ({ assetData, employees, onFieldChange, formState, onRepairChange }) => {
  const [availableTempAssets, setAvailableTempAssets] = useState([]);
  const [repairInfo, setRepairInfo] = useState(null);
  const [isLoadingRepair, setIsLoadingRepair] = useState(false);

  // Fetch repair status and temp assets when asset changes or repair status changes
  useEffect(() => {
    const fetchRepairData = async () => {
      if (!assetData?.assetId) return;
      
      setIsLoadingRepair(true);
      try {
        // Fetch current repair status
        const repairResult = await assetService.getRepairStatus(assetData.assetId);
        if (repairResult.success && repairResult.data) {
          setRepairInfo(repairResult.data);
          // Initialize form with existing repair data
          if (onRepairChange) {
            onRepairChange({
              repairDetails: repairResult.data.repairDetails || '',
              tempAssetId: repairResult.data.tempAssetId || ''
            });
          }
        } else {
          setRepairInfo(null);
        }

        // Fetch available temp assets if user is assigned
        if (assetData.assignedTo) {
          const tempResult = await assetService.getAvailableTempAssets(assetData.assetId);
          if (tempResult.success) {
            setAvailableTempAssets(tempResult.data);
          }
        }
      } catch (error) {
        console.error('Failed to fetch repair data:', error);
      } finally {
        setIsLoadingRepair(false);
      }
    };

    fetchRepairData();
  }, [assetData?.assetId, assetData?.assignedTo]);

  const handleRepairToggle = () => {
    const newStatus = !formState.repairStatus;
    onFieldChange('repairStatus', newStatus);
    
    if (!newStatus) {
      // Clearing repair status
      onFieldChange('repairDetails', '');
      onFieldChange('tempAssetId', '');
    }
  };

  const hasAssignedEmployee = !!assetData?.assignedTo;
  const showRepairFields = formState.repairStatus;

  return (
    <div className="update-asset-form">
      <div className="update-asset-form__field">
        <label className="update-asset-form__label">Reassign Asset To</label>
        <select
          value={formState.assignedTo}
          onChange={(e) => onFieldChange('assignedTo', e.target.value)}
          className="update-asset-form__select"
          disabled={formState.repairStatus}
        >
          <option value="">-- Not Assigned --</option>
          {Object.entries(employees).map(([id, emp]) => (
            <option key={id} value={id}>{emp.name} ({id})</option>
          ))}
        </select>
        {formState.repairStatus && (
          <span className="update-asset-form__hint">Cannot reassign while under repair</span>
        )}
      </div>

      <div className="update-asset-form__field">
        <label className="update-asset-form__label">Repair Status</label>
        <button
          type="button"
          onClick={handleRepairToggle}
          className={`update-asset-form__toggle ${formState.repairStatus ? 'update-asset-form__toggle--active' : ''}`}
        >
          <span className="update-asset-form__toggle-label">
            <Icons.Wrench />
            {formState.repairStatus ? 'Under Repair' : 'Working Condition'}
          </span>
          <div className={`update-asset-form__toggle-switch ${formState.repairStatus ? 'update-asset-form__toggle-switch--on' : ''}`}>
            <div className="update-asset-form__toggle-knob" />
          </div>
        </button>
      </div>

      {showRepairFields && (
        <>
          <div className="update-asset-form__field update-asset-form__field--full">
            <label className="update-asset-form__label">
              Repair Details <span className="update-asset-form__required">*</span>
            </label>
            <textarea
              value={formState.repairDetails || ''}
              onChange={(e) => onFieldChange('repairDetails', e.target.value)}
              placeholder="Describe the issue and repair requirements..."
              className="update-asset-form__textarea"
              rows={4}
              disabled={!!repairInfo}
            />
            {repairInfo && (
              <span className="update-asset-form__hint">
                Repair started: {new Date(repairInfo.repairStartTimestamp).toLocaleDateString()}
              </span>
            )}
          </div>

          {hasAssignedEmployee && (
            <div className="update-asset-form__field update-asset-form__field--full">
              <label className="update-asset-form__label">
                Assign Temporary Asset
                {!repairInfo && <span className="update-asset-form__optional"> (Optional)</span>}
              </label>
              {isLoadingRepair ? (
                <div className="update-asset-form__loading">Loading available assets...</div>
              ) : repairInfo?.tempAssetId && repairInfo.tempAssetId !== assetData.assetId ? (
                <div className="update-asset-form__temp-asset-display">
                  <Icons.Package />
                  <span>Temp Asset: <strong>{repairInfo.tempAssetId}</strong></span>
                </div>
              ) : !repairInfo ? (
                <select
                  value={formState.tempAssetId || ''}
                  onChange={(e) => onFieldChange('tempAssetId', e.target.value)}
                  className="update-asset-form__select"
                >
                  <option value="">-- No Temp Asset --</option>
                  {availableTempAssets.map(asset => (
                    <option key={asset.assetId} value={asset.assetId}>
                      {asset.assetId} ({asset.serialNumber})
                    </option>
                  ))}
                </select>
              ) : (
                <div className="update-asset-form__no-temp">No temporary asset assigned</div>
              )}
              {!repairInfo && availableTempAssets.length === 0 && (
                <span className="update-asset-form__hint">
                  No unassigned assets of type "{assetData.assetType}" available
                </span>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default UpdateAssetForm;