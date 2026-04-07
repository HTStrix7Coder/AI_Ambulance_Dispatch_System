import axios from "axios";

// Create an Axios instance with the backend URL
const API = axios.create({ baseURL: "http://localhost:8000" });

// API call to the triage endpoint
export const triageCase = (formData) =>
  API.post("/triage/", formData);