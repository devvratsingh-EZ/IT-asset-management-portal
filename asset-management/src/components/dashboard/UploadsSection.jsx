import { useState } from 'react';
import { Icons } from '../common/Icons';

const UploadsSection = ({ assetId }) => {
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [docFiles, setDocFiles] = useState([]);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleDocUpload = (e) => {
    const files = Array.from(e.target.files);
    setDocFiles(prev => [...prev, ...files]);
  };

  const handleRemoveDoc = (index) => {
    setDocFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="uploads-section">
      <div className="uploads-section__column">
        <p className="uploads-section__title">Upload Asset Picture</p>
        <label className="uploads-section__dropzone-label">
          <div className={`uploads-section__dropzone ${imagePreview ? 'uploads-section__dropzone--has-file' : ''}`}>
            {imagePreview ? (
              <div className="uploads-section__preview">
                <img src={imagePreview} alt="Preview" className="uploads-section__preview-image" />
                <p className="uploads-section__preview-name">{imageFile?.name}</p>
              </div>
            ) : (
              <>
                <div className="uploads-section__dropzone-icon"><Icons.Image /></div>
                <p className="uploads-section__dropzone-text">Click to upload image</p>
                <p className="uploads-section__dropzone-hint">JPG, JPEG, PNG</p>
              </>
            )}
          </div>
          <input type="file" accept="image/*" onChange={handleImageUpload} className="uploads-section__input" />
        </label>
      </div>

      <div className="uploads-section__column">
        <p className="uploads-section__title">Upload Asset Documents</p>
        <label className="uploads-section__dropzone-label">
          <div className="uploads-section__dropzone">
            <div className="uploads-section__dropzone-icon"><Icons.File /></div>
            <p className="uploads-section__dropzone-text">Click to upload documents</p>
            <p className="uploads-section__dropzone-hint">PDF, DOCX, CSV, XLSX</p>
          </div>
          <input type="file" accept=".pdf,.docx,.csv,.xlsx" multiple onChange={handleDocUpload} className="uploads-section__input" />
        </label>
        
        {docFiles.length > 0 && (
          <div className="uploads-section__file-list">
            {docFiles.map((file, index) => (
              <div key={index} className="uploads-section__file-item">
                <div className="uploads-section__file-info">
                  <Icons.File />
                  <span className="uploads-section__file-name">{file.name}</span>
                </div>
                <button onClick={() => handleRemoveDoc(index)} className="uploads-section__file-remove">
                  <Icons.X />
                </button>
              </div>
            ))}
            <p className="uploads-section__file-count">{docFiles.length} document(s) selected</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadsSection;