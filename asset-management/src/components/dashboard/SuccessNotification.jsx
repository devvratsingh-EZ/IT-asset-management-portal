import { Icons } from '../common/Icons';

/**
 * Success Notification Component
 * Displays a toast notification after successful form submission
 * @param {boolean} isVisible - Whether to show the notification
 * @param {object} summary - Summary of submitted changes
 * @param {boolean} isNewAsset - Whether this is for a new asset (vs update)
 */
const SuccessNotification = ({ isVisible, summary, isNewAsset = false }) => {
  if (!isVisible || !summary) return null;

  return (
    <div className="success-notification animate-slide-in-right">
      <div className="success-notification__content">
        <div className="success-notification__icon">
          <Icons.Check />
        </div>
        <div className="success-notification__details">
          <h3 className="success-notification__title">
            {isNewAsset ? 'Asset Added Successfully!' : 'Changes Submitted Successfully!'}
          </h3>
          <div className="success-notification__summary">
            {isNewAsset ? (
              <>
                <p>
                  Asset Type: <span>{summary.assetType}</span>
                </p>
                <p>
                  Brand/Model: <span>{summary.brand} {summary.model}</span>
                </p>
                <p>
                  Serial Number: <span>{summary.serialNumber}</span>
                </p>
                <p className="success-notification__note">
                  {summary.message}
                </p>
              </>
            ) : (
              <>
                <p>
                  Assigned To: <span>{summary.assignedTo} ({summary.employeeName})</span>
                </p>
                <p>
                  Repair Status: <span>{summary.repairStatus ? 'Under Repair' : 'Operational'}</span>
                </p>
                <p>
                  Image Uploaded: <span>{summary.imageUploaded ? 'Yes' : 'No'}</span>
                </p>
                <p>
                  Documents Uploaded: <span>{summary.docsUploaded}</span>
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SuccessNotification;
