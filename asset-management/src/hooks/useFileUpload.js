import { useState, useCallback } from 'react';

/**
 * Custom hook for managing file uploads
 * @param {object} options - Configuration options
 * @param {string[]} options.acceptedTypes - Accepted file MIME types
 * @param {number} options.maxSize - Maximum file size in bytes
 * @param {boolean} options.multiple - Allow multiple file selection
 * @returns {object} File upload state and handlers
 */
const useFileUpload = (options = {}) => {
  const {
    acceptedTypes = [],
    maxSize = 10 * 1024 * 1024, // 10MB default
    multiple = false,
  } = options;

  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [error, setError] = useState(null);

  /**
   * Validate a file against configured constraints
   * @param {File} file - File to validate
   * @returns {string|null} Error message or null if valid
   */
  const validateFile = useCallback((file) => {
    if (acceptedTypes.length > 0 && !acceptedTypes.includes(file.type)) {
      return `File type ${file.type} is not accepted`;
    }
    if (file.size > maxSize) {
      return `File size exceeds maximum allowed (${Math.round(maxSize / 1024 / 1024)}MB)`;
    }
    return null;
  }, [acceptedTypes, maxSize]);

  /**
   * Handle file selection
   * @param {Event} event - File input change event
   */
  const handleFileSelect = useCallback((event) => {
    const selectedFiles = Array.from(event.target.files);
    setError(null);

    // Validate all files
    for (const file of selectedFiles) {
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        return;
      }
    }

    if (multiple) {
      setFiles(prev => [...prev, ...selectedFiles]);
      
      // Generate previews for images
      selectedFiles.forEach(file => {
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onloadend = () => {
            setPreviews(prev => [...prev, { name: file.name, url: reader.result }]);
          };
          reader.readAsDataURL(file);
        }
      });
    } else {
      setFiles([selectedFiles[0]]);
      
      // Generate preview for single image
      if (selectedFiles[0]?.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setPreviews([{ name: selectedFiles[0].name, url: reader.result }]);
        };
        reader.readAsDataURL(selectedFiles[0]);
      }
    }
  }, [multiple, validateFile]);

  /**
   * Remove a file by index
   * @param {number} index - Index of file to remove
   */
  const removeFile = useCallback((index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setPreviews(prev => prev.filter((_, i) => i !== index));
  }, []);

  /**
   * Clear all files
   */
  const clearFiles = useCallback(() => {
    setFiles([]);
    setPreviews([]);
    setError(null);
  }, []);

  return {
    files,
    previews,
    error,
    handleFileSelect,
    removeFile,
    clearFiles,
    hasFiles: files.length > 0,
  };
};

export default useFileUpload;
