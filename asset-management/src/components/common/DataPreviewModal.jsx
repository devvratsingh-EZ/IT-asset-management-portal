import { Icons } from '../common/Icons';

/**
 * Data Preview Modal Component
 * Shows a tabular preview of asset data before submission
 * @param {boolean} isOpen - Whether the modal is visible
 * @param {function} onClose - Callback to close the modal
 * @param {function} onConfirm - Callback to confirm and submit
 * @param {object} data - The asset data to preview
 * @param {Array} specificationFields - Array of specification field definitions
 */
const DataPreviewModal = ({ isOpen, onClose, onConfirm, data, specificationFields = [] }) => {
  if (!isOpen || !data) return null;

  const formatDate = (date) => {
    if (!date) return 'Not specified';
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatCurrency = (amount) => {
    if (!amount) return '₹0.00';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  // Group data for display
  const basicInfo = [
    { label: 'Asset Type', value: data.assetType || 'Not specified' },
    { label: 'Serial Number', value: data.serialNumber || 'Not specified' },
    { label: 'Brand', value: data.brand || 'Not specified' },
    { label: 'Model', value: data.model || 'Not specified' },
  ];

  // Dynamic specifications based on asset type
  const specifications = specificationFields.map(spec => ({
    label: spec.label,
    value: data.specifications?.[spec.key] || data[spec.key] || 'N/A'
  }));

  const purchaseInfo = [
    { label: 'Date of Purchase', value: formatDate(data.purchaseDate) },
    { label: 'Purchase Cost', value: formatCurrency(data.purchaseCost) },
    { label: 'GST Paid', value: formatCurrency(data.gstPaid) },
    { label: 'Total Cost (incl. GST)', value: formatCurrency((parseFloat(data.purchaseCost) || 0) + (parseFloat(data.gstPaid) || 0)) },
    { label: 'Warranty Expiry', value: formatDate(data.warrantyExpiry) },
  ];

  const assignmentInfo = [
    { label: 'Initial Assignment', value: data.assignedTo ? `${data.assignedToName} (${data.assignedTo})` : 'Unassigned' },
    { label: 'Repair Status', value: data.repairStatus ? 'Under Repair' : 'Working' },
  ];

  const uploadedFiles = [
    { label: 'Asset Images', value: data.assetImages?.length || 0, type: 'count' },
    { label: 'Purchase Receipts', value: data.purchaseReceipts?.length || 0, type: 'count' },
    { label: 'Warranty Cards', value: data.warrantyCards?.length || 0, type: 'count' },
  ];

  return (
    <div className="data-preview-modal__overlay" onClick={onClose}>
      <div className="data-preview-modal" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="data-preview-modal__header">
          <div className="data-preview-modal__title-section">
            <div className="data-preview-modal__icon">
              <Icons.Eye />
            </div>
            <div>
              <h2 className="data-preview-modal__title">Review Asset Data</h2>
              <p className="data-preview-modal__subtitle">Please verify all information before submitting</p>
            </div>
          </div>
          <button onClick={onClose} className="data-preview-modal__close-btn">
            <Icons.X />
          </button>
        </div>

        {/* Modal Content */}
        <div className="data-preview-modal__content">
          {/* Basic Information */}
          <div className="data-preview-modal__section">
            <h3 className="data-preview-modal__section-title">Basic Information</h3>
            <table className="data-preview-modal__table">
              <tbody>
                {basicInfo.map((item, index) => (
                  <tr key={index} className="data-preview-modal__row">
                    <td className="data-preview-modal__cell-label">{item.label}</td>
                    <td className="data-preview-modal__cell-value">{item.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Specifications */}
          {specifications.length > 0 && (
            <div className="data-preview-modal__section">
              <h3 className="data-preview-modal__section-title">Specifications - {data.assetType}</h3>
              <table className="data-preview-modal__table">
                <tbody>
                  {specifications.map((item, index) => (
                    <tr key={index} className="data-preview-modal__row">
                      <td className="data-preview-modal__cell-label">{item.label}</td>
                      <td className="data-preview-modal__cell-value">{item.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Purchase Information */}
          <div className="data-preview-modal__section">
            <h3 className="data-preview-modal__section-title">Purchase Information</h3>
            <table className="data-preview-modal__table">
              <tbody>
                {purchaseInfo.map((item, index) => (
                  <tr key={index} className="data-preview-modal__row">
                    <td className="data-preview-modal__cell-label">{item.label}</td>
                    <td className="data-preview-modal__cell-value">{item.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Assignment Information */}
          <div className="data-preview-modal__section">
            <h3 className="data-preview-modal__section-title">Assignment Details</h3>
            <table className="data-preview-modal__table">
              <tbody>
                {assignmentInfo.map((item, index) => (
                  <tr key={index} className="data-preview-modal__row">
                    <td className="data-preview-modal__cell-label">{item.label}</td>
                    <td className="data-preview-modal__cell-value">{item.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Uploaded Files */}
          <div className="data-preview-modal__section">
            <h3 className="data-preview-modal__section-title">Uploaded Files</h3>
            <table className="data-preview-modal__table">
              <tbody>
                {uploadedFiles.map((item, index) => (
                  <tr key={index} className="data-preview-modal__row">
                    <td className="data-preview-modal__cell-label">{item.label}</td>
                    <td className="data-preview-modal__cell-value">
                      <span className={`data-preview-modal__file-count ${item.value > 0 ? 'data-preview-modal__file-count--uploaded' : ''}`}>
                        {item.value} file{item.value !== 1 ? 's' : ''} uploaded
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Note */}
          <div className="data-preview-modal__note">
            <p>
              <strong>Note:</strong> A unique Asset ID will be automatically generated by the system upon submission.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="data-preview-modal__footer">
          <button onClick={onClose} className="data-preview-modal__cancel-btn">
            Cancel
          </button>
          <button onClick={onConfirm} className="data-preview-modal__confirm-btn">
            <Icons.Check />
            Confirm & Submit
          </button>
        </div>
      </div>
    </div>
  );
};

export default DataPreviewModal;
