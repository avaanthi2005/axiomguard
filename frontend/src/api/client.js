import axios from 'axios';

export const API = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API,
});

// Attach the JWT (if the user is logged in) to every request automatically.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('axiomguard_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If a token expires or is invalid, the backend returns 401 — clear the
// stale session so the app doesn't get stuck in a broken "logged in" state.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('axiomguard_token');
      localStorage.removeItem('axiomguard_user');
    }
    return Promise.reject(error);
  }
);

export default api;
