import axios from "axios";

// Set VITE_API_URL in a .env file if the backend isn't on localhost:8000.
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export default apiClient;
