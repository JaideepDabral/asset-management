/**
 * API Configuration Constants
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
export const API_VERSION = '/api/v1';

export const API_URL = `${API_BASE_URL}${API_VERSION}`;

// For backward compatibility, also export the full API URL
export default {
    API_BASE_URL,
    API_VERSION,
    API_URL
};
