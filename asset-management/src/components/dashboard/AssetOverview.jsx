import ExpandableSection from '../common/ExpandableSection';
import { Icons } from '../common/Icons';

/**
 * Asset Overview Component
 * Displays key asset information in a grid
 * @param {object} assetData - Asset information object
 * @param {function} formatDate - Date formatting utility function
 */
const AssetOverview = ({ assetData, formatDate }) => {
  const overviewItems = [
    { label: 'Asset ID', value: assetData.assetId, color: 'cyan' },
    { label: 'Serial Number', value: assetData.serialNumber, color: 'teal' },
    { label: 'Asset Type', value: assetData.assetType, color: 'emerald' },
    { label: 'Warranty Expiry', value: formatDate(assetData.warrantyExpiry), color: 'amber' }
  ];

  return (
    <ExpandableSection title="Asset Overview" icon={Icons.Laptop} defaultExpanded={true}>
      <div className="asset-overview__grid">
        {overviewItems.map((item, index) => (
          <div key={index} className="asset-overview__item">
            <p className="asset-overview__label">{item.label}</p>
            <p className={`asset-overview__value asset-overview__value--${item.color}`}>
              {item.value}
            </p>
          </div>
        ))}
      </div>
    </ExpandableSection>
  );
};

export default AssetOverview;
