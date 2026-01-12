import { Icons } from '../common/Icons';

const UpdateAssetForm = ({ assetData, employees, onFieldChange, formState }) => {
  return (
    <div className="update-asset-form">
      <div className="update-asset-form__field">
        <label className="update-asset-form__label">Reassign Asset To</label>
        <select
          value={formState.assignedTo}
          onChange={(e) => onFieldChange('assignedTo', e.target.value)}
          className="update-asset-form__select"
        >
          <option value="">-- Not Assigned --</option>
          {Object.entries(employees).map(([id, emp]) => (
            <option key={id} value={id}>{emp.name} ({id})</option>
          ))}
        </select>
      </div>

      <div className="update-asset-form__field">
        <label className="update-asset-form__label">Repair Status</label>
        <button
          type="button"
          onClick={() => onFieldChange('repairStatus', !formState.repairStatus)}
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
    </div>
  );
};

export default UpdateAssetForm;