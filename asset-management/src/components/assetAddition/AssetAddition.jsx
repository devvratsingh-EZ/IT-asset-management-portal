import { useState, useMemo, useEffect } from 'react';
import { Icons, ExpandableSection, DatePicker, DataPreviewModal } from '../common';
import { APP_CONFIG } from '../../data/constants';
import SuccessNotification from '../dashboard/SuccessNotification';

const AssetAddition = () => {
  // Asset types and specifications from API
  const [assetTypes, setAssetTypes] = useState([]);
  const [allSpecifications, setAllSpecifications] = useState({});
  const [employees, setEmployees] = useState({});
  const [isLoadingData, setIsLoadingData] = useState(true);

  // Form state
  const [formData, setFormData] = useState({
    assetType: '',
    serialNumber: '',
    brand: '',
    model: '',
    specifications: {},
    purchaseDate: null,
    purchaseCost: '',
    gstPaid: '',
    warrantyExpiry: null,
    assignedTo: '',
    repairStatus: false,
  });

  // File uploads state
  const [assetImages, setAssetImages] = useState([]);
  const [purchaseReceipts, setPurchaseReceipts] = useState([]);
  const [warrantyCards, setWarrantyCards] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);

  // UI state
  const [showPreview, setShowPreview] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [submitSummary, setSubmitSummary] = useState(null);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch data on mount
  useEffect(() => {
    const fetchData = async () => {
      setIsLoadingData(true);
      try {
        console.log('Fetching initial data...');
        // Fetch asset types
        const typesResponse = await fetch(`${APP_CONFIG.apiBaseUrl}/assets/asset-types`);
        const typesData = await typesResponse.json();
        if (typesData.success) {
          setAssetTypes(typesData.data);
        }

        // Fetch all specifications
        const specsResponse = await fetch(`${APP_CONFIG.apiBaseUrl}/assets/specifications`);
        const specsData = await specsResponse.json();
        if (specsData.success) {
          setAllSpecifications(specsData.data);
        }

        // Fetch employees
        const employeesResponse = await fetch(`${APP_CONFIG.apiBaseUrl}/employees`);
        const employeesData = await employeesResponse.json();
        if (employeesData.success) {
          setEmployees(employeesData.data);
        }
        console.log('Employees fetched:', employeesData);
      } catch (error) {
        console.error('Failed to fetch data from API:', error);
      } finally {
        setIsLoadingData(false);
      }
    };

    fetchData();
  }, []);

  const isBasicInfoComplete = useMemo(() => {
    return (
      formData.assetType.trim() !== '' &&
      formData.serialNumber.trim() !== '' &&
      formData.brand.trim() !== '' &&
      formData.model.trim() !== ''
    );
  }, [formData.assetType, formData.serialNumber, formData.brand, formData.model]);

  const specificationFields = useMemo(() => {
    if (!formData.assetType || !allSpecifications[formData.assetType]) {
      return [];
    }
    return allSpecifications[formData.assetType].fields || [];
  }, [formData.assetType, allSpecifications]);

  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const updateSpecification = (key, value) => {
    setFormData(prev => ({
      ...prev,
      specifications: { ...prev.specifications, [key]: value }
    }));
  };

  const handleAssetTypeChange = (newType) => {
    setFormData(prev => ({
      ...prev,
      assetType: newType,
      specifications: {}
    }));
    if (errors.assetType) {
      setErrors(prev => ({ ...prev, assetType: null }));
    }
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    setAssetImages(prev => [...prev, ...files]);
    
    files.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreviews(prev => [...prev, { name: file.name, url: reader.result }]);
      };
      reader.readAsDataURL(file);
    });
  };

  const handleDocUpload = (e, type) => {
    const files = Array.from(e.target.files);
    if (type === 'receipts') {
      setPurchaseReceipts(prev => [...prev, ...files]);
    } else if (type === 'warranty') {
      setWarrantyCards(prev => [...prev, ...files]);
    }
  };

  const removeFile = (type, index) => {
    switch (type) {
      case 'images':
        setAssetImages(prev => prev.filter((_, i) => i !== index));
        setImagePreviews(prev => prev.filter((_, i) => i !== index));
        break;
      case 'receipts':
        setPurchaseReceipts(prev => prev.filter((_, i) => i !== index));
        break;
      case 'warranty':
        setWarrantyCards(prev => prev.filter((_, i) => i !== index));
        break;
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.assetType) newErrors.assetType = 'Asset type is required';
    if (!formData.serialNumber) newErrors.serialNumber = 'Serial number is required';
    if (!formData.brand) newErrors.brand = 'Brand is required';
    if (!formData.model) newErrors.model = 'Model is required';
    if (!formData.purchaseDate) newErrors.purchaseDate = 'Purchase date is required';
    if (!formData.purchaseCost) newErrors.purchaseCost = 'Purchase cost is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handlePreview = () => {
    if (validateForm()) {
      setShowPreview(true);
    }
  };

  const preparePayload = () => {
    const assignedToName = formData.assignedTo ? employees[formData.assignedTo]?.name : null;
    return {
      assetType: formData.assetType,
      serialNumber: formData.serialNumber,
      brand: formData.brand,
      model: formData.model,
      specifications: formData.specifications,
      purchaseDate: formData.purchaseDate,
      purchaseCost: parseFloat(formData.purchaseCost) || 0,
      gstPaid: parseFloat(formData.gstPaid) || 0,
      warrantyExpiry: formData.warrantyExpiry,
      assignedTo: formData.assignedTo || null,
      assignedToName: assignedToName,
      repairStatus: formData.repairStatus,
    };
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setShowPreview(false);
    
    try {
      const payload = preparePayload();
      console.log('Submitting asset payload:', payload);  // ADD THIS
      console.log('API URL:', `${APP_CONFIG.apiBaseUrl}/assets`);  // ADD THIS
      const response = await fetch(`${APP_CONFIG.apiBaseUrl}/assets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      console.log('Response status:', response.status);  // ADD THIS
      const result = await response.json();
      console.log('Response data:', result);
      
      if (result.success) {
        setSubmitSummary({
          assetId: result.assetId,
          assetType: payload.assetType,
          serialNumber: payload.serialNumber,
          brand: payload.brand,
          model: payload.model,
          message: `Asset ${result.assetId} created successfully`
        });
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 5000);
        resetForm();
      } else {
        alert(`Failed to create asset: ${result.detail || result.message || 'Unknown error'}`);
        console.error('Failed to create asset:', result);
        console.error('Failed to create asset:', result.message);
      }
    } catch (error) {
      console.error('Error creating asset:', error);
      alert(`Error creating asset: ${error.message || 'Server connection failed'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      assetType: '',
      serialNumber: '',
      brand: '',
      model: '',
      specifications: {},
      purchaseDate: null,
      purchaseCost: '',
      gstPaid: '',
      warrantyExpiry: null,
      assignedTo: '',
      repairStatus: false,
    });
    setAssetImages([]);
    setPurchaseReceipts([]);
    setWarrantyCards([]);
    setImagePreviews([]);
    setErrors({});
  };

  const lockedMessage = "Please complete all fields in Basic Information section first";

  if (isLoadingData) {
    return (
      <div className="asset-addition">
        <div className="asset-addition__header">
          <h1 className="asset-addition__title">Add New Asset</h1>
          <p className="asset-addition__subtitle">Loading asset data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="asset-addition">
      <div className="asset-addition__header">
        <h1 className="asset-addition__title">Add New Asset</h1>
        <p className="asset-addition__subtitle">Enter details of newly purchased assets</p>
      </div>

      {!isBasicInfoComplete && (
        <div className="asset-addition__progress-notice">
          <Icons.ClipboardList />
          <span>Complete the <strong>Basic Information</strong> section to unlock other sections</span>
        </div>
      )}

      <div className="asset-addition__sections">
        <ExpandableSection
          title="Basic Information"
          icon={Icons.Package}
          defaultExpanded={true}
        >
          <div className="asset-addition__form-grid">
            <div className="asset-addition__field">
              <label className="asset-addition__label">
                Asset Type <span className="asset-addition__required">*</span>
              </label>
              <select
                value={formData.assetType}
                onChange={(e) => handleAssetTypeChange(e.target.value)}
                className={`asset-addition__select ${errors.assetType ? 'asset-addition__select--error' : ''}`}
              >
                <option value="">Select asset type</option>
                {assetTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              {errors.assetType && <span className="asset-addition__error">{errors.assetType}</span>}
            </div>

            <div className="asset-addition__field">
              <label className="asset-addition__label">
                Serial Number <span className="asset-addition__required">*</span>
              </label>
              <input
                type="text"
                value={formData.serialNumber}
                onChange={(e) => updateField('serialNumber', e.target.value)}
                placeholder="Enter serial number"
                className={`asset-addition__input ${errors.serialNumber ? 'asset-addition__input--error' : ''}`}
              />
              {errors.serialNumber && <span className="asset-addition__error">{errors.serialNumber}</span>}
            </div>

            <div className="asset-addition__field">
              <label className="asset-addition__label">
                Brand <span className="asset-addition__required">*</span>
              </label>
              <input
                type="text"
                value={formData.brand}
                onChange={(e) => updateField('brand', e.target.value)}
                placeholder="e.g., Dell, HP, Lenovo"
                className={`asset-addition__input ${errors.brand ? 'asset-addition__input--error' : ''}`}
              />
              {errors.brand && <span className="asset-addition__error">{errors.brand}</span>}
            </div>

            <div className="asset-addition__field">
              <label className="asset-addition__label">
                Model <span className="asset-addition__required">*</span>
              </label>
              <input
                type="text"
                value={formData.model}
                onChange={(e) => updateField('model', e.target.value)}
                placeholder="e.g., Latitude 7420"
                className={`asset-addition__input ${errors.model ? 'asset-addition__input--error' : ''}`}
              />
              {errors.model && <span className="asset-addition__error">{errors.model}</span>}
            </div>
          </div>
        </ExpandableSection>

        <ExpandableSection
          title={`Specifications${formData.assetType ? ` - ${formData.assetType}` : ''}`}
          icon={Icons.Cpu}
          defaultExpanded={true}
          disabled={!isBasicInfoComplete}
          disabledMessage={lockedMessage}
        >
          <div className="asset-addition__form-grid">
            {specificationFields.map((spec) => (
              <div key={spec.key} className="asset-addition__field">
                <label className="asset-addition__label">{spec.label}</label>
                <input
                  type="text"
                  value={formData.specifications[spec.key] || ''}
                  onChange={(e) => updateSpecification(spec.key, e.target.value)}
                  placeholder={spec.placeholder}
                  className="asset-addition__input"
                />
              </div>
            ))}
            {specificationFields.length === 0 && (
              <div className="asset-addition__empty-state">
                <p>Select an asset type to see relevant specifications</p>
              </div>
            )}
          </div>
        </ExpandableSection>

        <ExpandableSection
          title="Purchase Information"
          icon={Icons.Receipt}
          defaultExpanded={true}
          disabled={!isBasicInfoComplete}
          disabledMessage={lockedMessage}
        >
          <div className="asset-addition__form-grid">
            <div className="asset-addition__field">
              <DatePicker
                value={formData.purchaseDate}
                onChange={(date) => updateField('purchaseDate', date)}
                label={<>Date of Purchase <span className="asset-addition__required">*</span></>}
              />
              {errors.purchaseDate && <span className="asset-addition__error">{errors.purchaseDate}</span>}
            </div>

            <div className="asset-addition__field">
              <label className="asset-addition__label">
                Purchase Cost (₹) <span className="asset-addition__required">*</span>
              </label>
              <div className="asset-addition__input-with-icon">
                <Icons.IndianRupee />
                <input
                  type="number"
                  value={formData.purchaseCost}
                  onChange={(e) => updateField('purchaseCost', e.target.value)}
                  placeholder="Enter amount"
                  min="0"
                  step="0.01"
                  className={`asset-addition__input asset-addition__input--with-icon ${errors.purchaseCost ? 'asset-addition__input--error' : ''}`}
                />
              </div>
              {errors.purchaseCost && <span className="asset-addition__error">{errors.purchaseCost}</span>}
            </div>

            <div className="asset-addition__field">
              <label className="asset-addition__label">GST Paid (₹)</label>
              <div className="asset-addition__input-with-icon">
                <Icons.IndianRupee />
                <input
                  type="number"
                  value={formData.gstPaid}
                  onChange={(e) => updateField('gstPaid', e.target.value)}
                  placeholder="Enter GST amount"
                  min="0"
                  step="0.01"
                  className="asset-addition__input asset-addition__input--with-icon"
                />
              </div>
            </div>

            <div className="asset-addition__field">
              <DatePicker
                value={formData.warrantyExpiry}
                onChange={(date) => updateField('warrantyExpiry', date)}
                label="Warranty Expiry Date"
              />
            </div>
          </div>
        </ExpandableSection>

        <ExpandableSection
          title="Initial Assignment"
          icon={Icons.User}
          defaultExpanded={false}
          disabled={!isBasicInfoComplete}
          disabledMessage={lockedMessage}
        >
          <div className="asset-addition__form-grid">
            <div className="asset-addition__field">
              <label className="asset-addition__label">Assign to Employee (Optional)</label>
              <select
                value={formData.assignedTo}
                onChange={(e) => updateField('assignedTo', e.target.value)}
                className="asset-addition__select"
              >
                <option value="">Not assigned</option>
                {Object.entries(employees).map(([id, emp]) => (
                  <option key={id} value={id}>{emp.name} ({id})</option>
                ))}
              </select>
            </div>
          </div>
        </ExpandableSection>

        <ExpandableSection
          title="Upload Documents & Images"
          icon={Icons.Upload}
          defaultExpanded={true}
          disabled={!isBasicInfoComplete}
          disabledMessage={lockedMessage}
        >
          <div className="asset-addition__uploads-grid">
            <div className="asset-addition__upload-section">
              <h4 className="asset-addition__upload-title">
                <Icons.Image /> Asset Images
              </h4>
              <label className="asset-addition__dropzone">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="asset-addition__file-input"
                />
                <Icons.Upload />
                <span>Click or drag images here</span>
                <span className="asset-addition__dropzone-hint">PNG, JPG up to 10MB</span>
              </label>
              {imagePreviews.length > 0 && (
                <div className="asset-addition__file-list">
                  {imagePreviews.map((preview, index) => (
                    <div key={index} className="asset-addition__image-preview">
                      <img src={preview.url} alt={preview.name} />
                      <button
                        type="button"
                        onClick={() => removeFile('images', index)}
                        className="asset-addition__remove-btn"
                      >
                        <Icons.X />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="asset-addition__upload-section">
              <h4 className="asset-addition__upload-title">
                <Icons.FileText /> Purchase Receipts
              </h4>
              <label className="asset-addition__dropzone">
                <input
                  type="file"
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleDocUpload(e, 'receipts')}
                  className="asset-addition__file-input"
                />
                <Icons.Upload />
                <span>Click or drag files here</span>
                <span className="asset-addition__dropzone-hint">PDF, Images up to 10MB</span>
              </label>
              {purchaseReceipts.length > 0 && (
                <div className="asset-addition__file-list">
                  {purchaseReceipts.map((file, index) => (
                    <div key={index} className="asset-addition__file-item">
                      <Icons.File />
                      <span className="asset-addition__file-name">{file.name}</span>
                      <button
                        type="button"
                        onClick={() => removeFile('receipts', index)}
                        className="asset-addition__remove-btn"
                      >
                        <Icons.X />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="asset-addition__upload-section">
              <h4 className="asset-addition__upload-title">
                <Icons.Shield /> Warranty Cards
              </h4>
              <label className="asset-addition__dropzone">
                <input
                  type="file"
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleDocUpload(e, 'warranty')}
                  className="asset-addition__file-input"
                />
                <Icons.Upload />
                <span>Click or drag files here</span>
                <span className="asset-addition__dropzone-hint">PDF, Images up to 10MB</span>
              </label>
              {warrantyCards.length > 0 && (
                <div className="asset-addition__file-list">
                  {warrantyCards.map((file, index) => (
                    <div key={index} className="asset-addition__file-item">
                      <Icons.File />
                      <span className="asset-addition__file-name">{file.name}</span>
                      <button
                        type="button"
                        onClick={() => removeFile('warranty', index)}
                        className="asset-addition__remove-btn"
                      >
                        <Icons.X />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </ExpandableSection>

        <div className="asset-addition__actions">
          <button
            type="button"
            onClick={resetForm}
            className="asset-addition__reset-btn"
          >
            Reset Form
          </button>
          <button
            type="button"
            onClick={handlePreview}
            className="asset-addition__preview-btn"
            disabled={!isBasicInfoComplete || isSubmitting}
          >
            <Icons.Eye />
            {isSubmitting ? 'Submitting...' : 'Preview & Submit'}
          </button>
        </div>
      </div>

      <DataPreviewModal
        isOpen={showPreview}
        onClose={() => setShowPreview(false)}
        onConfirm={handleSubmit}
        data={preparePayload()}
        specificationFields={specificationFields}
      />

      <SuccessNotification 
        isVisible={showSuccess} 
        summary={submitSummary}
        isNewAsset={true}
      />
    </div>
  );
};

export default AssetAddition;