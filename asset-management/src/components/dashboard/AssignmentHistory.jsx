import { Icons } from '../common/Icons';

/**
 * Assignment History Component
 * Shows history table or "No history" message
 */
const AssignmentHistory = ({ history }) => {
  // If no assignment history
  if (!history || history.length === 0) {
    return (
      <div className="assignment-history__empty">
        <div className="assignment-history__empty-icon">
          <Icons.FileX />
        </div>
        <h3 className="assignment-history__empty-title">No Assignment History</h3>
        <p className="assignment-history__empty-text">
          This asset has never been assigned to any employee.
        </p>
      </div>
    );
  }

  return (
    <div className="assignment-history">
      <table className="assignment-history__table">
        <thead>
          <tr>
            <th>Employee Name</th>
            <th>Employee ID</th>
            <th>Assigned On</th>
            <th>Returned On</th>
          </tr>
        </thead>
        <tbody>
          {history.map((record, index) => (
            <tr key={index}>
              <td>{record.employeeName}</td>
              <td>
                <span className="assignment-history__badge">{record.employeeId}</span>
              </td>
              <td>{record.assignedOn}</td>
              <td>
                {record.returnedOn === 'Active' ? (
                  <span className="assignment-history__active">
                    <span className="assignment-history__active-dot" />
                    Active
                  </span>
                ) : (
                  record.returnedOn
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AssignmentHistory;