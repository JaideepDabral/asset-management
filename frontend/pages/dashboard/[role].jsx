import Dashboard from '../index';

// Re-use the main Dashboard component.
// The AuthGuard ensures that the 'currentRole' context matches the URL param (implicitly),
// and Dashboard/index.jsx renders the correct view based on 'currentRole'.
// This avoids code duplication and keeps the "Executive Dashboard" untouched.

export default Dashboard;
