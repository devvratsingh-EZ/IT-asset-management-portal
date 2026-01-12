import { Icons } from '../common/Icons';

/**
 * Current Assigned Employee Component
 * Shows employee details or "Not Assigned" message
 */
const CurrentEmployee = ({ employee, employeeId }) => {
  // If no employee assigned
  if (!employee || !employeeId) {
    return (
      <div className="current-employee__not-assigned">
        <div className="current-employee__not-assigned-icon">
          <Icons.UserX />
        </div>
        <h3 className="current-employee__not-assigned-title">Asset Not Assigned</h3>
        <p className="current-employee__not-assigned-text">
          This asset is currently not assigned to any employee.
        </p>
      </div>
    );
  }

  // Get initials for avatar
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase();
  };

  return (
    <div className="current-employee">
      <div className="current-employee__card">
        <div className="current-employee__avatar">
          {getInitials(employee.name)}
        </div>
        <div className="current-employee__details">
          <div className="current-employee__row">
            <div className="current-employee__field">
              <span className="current-employee__label">Employee ID</span>
              <span className="current-employee__value">{employeeId}</span>
            </div>
            <div className="current-employee__field">
              <span className="current-employee__label">Name</span>
              <span className="current-employee__value">{employee.name}</span>
            </div>
          </div>
          <div className="current-employee__row">
            <div className="current-employee__field">
              <span className="current-employee__label">Department</span>
              <span className="current-employee__value">{employee.department}</span>
            </div>
            <div className="current-employee__field">
              <span className="current-employee__label">Email</span>
              <span className="current-employee__value current-employee__value--email">
                {employee.email}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurrentEmployee;