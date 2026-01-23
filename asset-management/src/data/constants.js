// Application configuration
export const APP_CONFIG = {
  appName: "IT Asset Management",
  companyName: "EZ IT Systems",
  // Use current window origin if available, otherwise fallback to localhost
  // This ensures cookies work regardless of localhost vs 127.0.0.1
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || `${window.location.origin}/api`,
};

