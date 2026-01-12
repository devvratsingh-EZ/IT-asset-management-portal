import ExpandableSection from '../common/ExpandableSection';
import { Icons } from '../common/Icons';

/**
 * Specifications Component
 * Displays detailed asset specifications
 * @param {object} specifications - Object containing asset specifications
 */
const Specifications = ({ specifications }) => {
  return (
    <div className="specifications__grid">
      {Object.entries(specifications).map(([key, value], index) => (
        <div key={index} className="specifications__item">
          <div className="specifications__indicator" />
          <div className="specifications__content">
            <p className="specifications__key">{key}</p>
            <p className="specifications__value">{value}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Specifications;
