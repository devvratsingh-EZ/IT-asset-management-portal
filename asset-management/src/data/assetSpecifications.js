/**
 * Asset Type Specifications Configuration
 * Defines which specification fields are relevant for each asset type
 * Maximum 4 specification fields per asset type
 */

export const ASSET_SPECIFICATIONS = {
  Laptop: {
    fields: [
      { key: 'processor', label: 'Processor', placeholder: 'e.g., Intel i7 11th Gen' },
      { key: 'ram', label: 'RAM', placeholder: 'e.g., 16 GB' },
      { key: 'storage', label: 'Storage', placeholder: 'e.g., 512 GB SSD' },
      { key: 'os', label: 'Operating System', placeholder: 'e.g., Windows 11 Pro' },
    ]
  },
  Desktop: {
    fields: [
      { key: 'processor', label: 'Processor', placeholder: 'e.g., Intel i9 12th Gen' },
      { key: 'ram', label: 'RAM', placeholder: 'e.g., 32 GB' },
      { key: 'storage', label: 'Storage', placeholder: 'e.g., 1 TB SSD' },
      { key: 'os', label: 'Operating System', placeholder: 'e.g., Windows 11 Pro' },
    ]
  },
  Monitor: {
    fields: [
      { key: 'screenSize', label: 'Screen Size', placeholder: 'e.g., 27 inches' },
      { key: 'resolution', label: 'Resolution', placeholder: 'e.g., 2560x1440 (QHD)' },
      { key: 'panelType', label: 'Panel Type', placeholder: 'e.g., IPS, VA, TN' },
      { key: 'refreshRate', label: 'Refresh Rate', placeholder: 'e.g., 144 Hz' },
    ]
  },
  Keyboard: {
    fields: [
      { key: 'keyboardType', label: 'Type', placeholder: 'e.g., Mechanical, Membrane' },
      { key: 'connectivity', label: 'Connectivity', placeholder: 'e.g., Wired USB, Wireless' },
      { key: 'layout', label: 'Layout', placeholder: 'e.g., Full-size, TKL, 60%' },
      { key: 'backlighting', label: 'Backlighting', placeholder: 'e.g., RGB, White, None' },
    ]
  },
  Mouse: {
    fields: [
      { key: 'mouseType', label: 'Type', placeholder: 'e.g., Optical, Laser' },
      { key: 'connectivity', label: 'Connectivity', placeholder: 'e.g., Wired, Wireless, Bluetooth' },
      { key: 'dpi', label: 'DPI', placeholder: 'e.g., 16000 DPI' },
      { key: 'buttons', label: 'Number of Buttons', placeholder: 'e.g., 6 buttons' },
    ]
  },
  Printer: {
    fields: [
      { key: 'printerType', label: 'Type', placeholder: 'e.g., Laser, Inkjet' },
      { key: 'printFunction', label: 'Functions', placeholder: 'e.g., Print, Scan, Copy, Fax' },
      { key: 'connectivity', label: 'Connectivity', placeholder: 'e.g., USB, WiFi, Ethernet' },
      { key: 'printSpeed', label: 'Print Speed', placeholder: 'e.g., 30 ppm' },
    ]
  },
  Scanner: {
    fields: [
      { key: 'scannerType', label: 'Type', placeholder: 'e.g., Flatbed, Document Feeder' },
      { key: 'opticalResolution', label: 'Optical Resolution', placeholder: 'e.g., 1200 x 1200 dpi' },
      { key: 'connectivity', label: 'Connectivity', placeholder: 'e.g., USB, WiFi' },
      { key: 'scanSpeed', label: 'Scan Speed', placeholder: 'e.g., 25 ppm' },
    ]
  },
  Server: {
    fields: [
      { key: 'processor', label: 'Processor', placeholder: 'e.g., Intel Xeon Silver 4314' },
      { key: 'ram', label: 'RAM', placeholder: 'e.g., 128 GB ECC' },
      { key: 'storage', label: 'Storage', placeholder: 'e.g., 4x 2TB SAS RAID' },
      { key: 'formFactor', label: 'Form Factor', placeholder: 'e.g., 2U Rack Mount' },
    ]
  },
  Router: {
    fields: [
      { key: 'wifiStandard', label: 'WiFi Standard', placeholder: 'e.g., WiFi 6 (802.11ax)' },
      { key: 'speed', label: 'Speed', placeholder: 'e.g., AX3000 (3 Gbps)' },
      { key: 'ports', label: 'LAN Ports', placeholder: 'e.g., 4x Gigabit Ethernet' },
      { key: 'coverage', label: 'Coverage Area', placeholder: 'e.g., 2500 sq ft' },
    ]
  },
  Switch: {
    fields: [
      { key: 'ports', label: 'Number of Ports', placeholder: 'e.g., 24 ports' },
      { key: 'speed', label: 'Port Speed', placeholder: 'e.g., Gigabit / 10GbE' },
      { key: 'managed', label: 'Management Type', placeholder: 'e.g., Managed, Unmanaged' },
      { key: 'poe', label: 'PoE Support', placeholder: 'e.g., PoE+, No PoE' },
    ]
  },
  UPS: {
    fields: [
      { key: 'capacity', label: 'Capacity', placeholder: 'e.g., 1500 VA / 900W' },
      { key: 'topology', label: 'Topology', placeholder: 'e.g., Line Interactive, Online' },
      { key: 'outlets', label: 'Number of Outlets', placeholder: 'e.g., 8 outlets' },
      { key: 'backupTime', label: 'Backup Time', placeholder: 'e.g., 10 minutes at full load' },
    ]
  },
  Projector: {
    fields: [
      { key: 'technology', label: 'Technology', placeholder: 'e.g., DLP, LCD, Laser' },
      { key: 'brightness', label: 'Brightness', placeholder: 'e.g., 4000 lumens' },
      { key: 'resolution', label: 'Resolution', placeholder: 'e.g., 1920x1080 (Full HD)' },
      { key: 'throwRatio', label: 'Throw Ratio', placeholder: 'e.g., Short throw, Standard' },
    ]
  },
  Tablet: {
    fields: [
      { key: 'screenSize', label: 'Screen Size', placeholder: 'e.g., 10.9 inches' },
      { key: 'processor', label: 'Processor', placeholder: 'e.g., Apple M1, Snapdragon 8' },
      { key: 'storage', label: 'Storage', placeholder: 'e.g., 256 GB' },
      { key: 'os', label: 'Operating System', placeholder: 'e.g., iPadOS 17, Android 14' },
    ]
  },
  "Mobile Phone": {
    fields: [
      { key: 'screenSize', label: 'Screen Size', placeholder: 'e.g., 6.7 inches' },
      { key: 'processor', label: 'Processor', placeholder: 'e.g., A17 Pro, Snapdragon 8 Gen 3' },
      { key: 'storage', label: 'Storage', placeholder: 'e.g., 256 GB' },
      { key: 'os', label: 'Operating System', placeholder: 'e.g., iOS 17, Android 14' },
    ]
  },
  Headset: {
    fields: [
      { key: 'headsetType', label: 'Type', placeholder: 'e.g., Over-ear, In-ear, On-ear' },
      { key: 'connectivity', label: 'Connectivity', placeholder: 'e.g., Wired 3.5mm, USB, Bluetooth' },
      { key: 'microphone', label: 'Microphone', placeholder: 'e.g., Boom mic, Inline mic, None' },
      { key: 'noiseCancellation', label: 'Noise Cancellation', placeholder: 'e.g., Active ANC, Passive, None' },
    ]
  },
  Webcam: {
    fields: [
      { key: 'resolution', label: 'Resolution', placeholder: 'e.g., 1080p, 4K' },
      { key: 'frameRate', label: 'Frame Rate', placeholder: 'e.g., 30 fps, 60 fps' },
      { key: 'microphone', label: 'Built-in Microphone', placeholder: 'e.g., Stereo, Mono, None' },
      { key: 'fieldOfView', label: 'Field of View', placeholder: 'e.g., 90°, 78°' },
    ]
  },
  "External Hard Drive": {
    fields: [
      { key: 'capacity', label: 'Capacity', placeholder: 'e.g., 2 TB' },
      { key: 'driveType', label: 'Drive Type', placeholder: 'e.g., HDD, SSD' },
      { key: 'interface', label: 'Interface', placeholder: 'e.g., USB 3.0, USB-C, Thunderbolt' },
      { key: 'formFactor', label: 'Form Factor', placeholder: 'e.g., 2.5 inch, Portable' },
    ]
  },
  Other: {
    fields: [
      { key: 'spec1', label: 'Specification 1', placeholder: 'Enter specification' },
      { key: 'spec2', label: 'Specification 2', placeholder: 'Enter specification' },
      { key: 'spec3', label: 'Specification 3', placeholder: 'Enter specification' },
      { key: 'spec4', label: 'Specification 4', placeholder: 'Enter specification' },
    ]
  },
};

/**
 * Get specifications for a given asset type
 * @param {string} assetType - The asset type
 * @returns {Array} Array of specification field definitions
 */
export const getSpecificationsForAssetType = (assetType) => {
  return ASSET_SPECIFICATIONS[assetType]?.fields || ASSET_SPECIFICATIONS.Other.fields;
};
