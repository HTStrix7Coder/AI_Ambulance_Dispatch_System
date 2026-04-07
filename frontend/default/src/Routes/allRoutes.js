import React from "react";
import { Navigate } from "react-router-dom";

//Dashboard
import DashboardMedical from "../pages/DashboardMedical";

//login
import Login from "../pages/Authentication/Login";
import ForgetPasswordPage from "../pages/Authentication/ForgetPassword";
import Logout from "../pages/Authentication/Logout";
import Register from "../pages/Authentication/Register";

// User Profile
import UserProfile from "../pages/Authentication/user-profile";

import Medicalchat from "../pages/MedicalChat";
import Cases from "../pages/Cases";
import Ambulances from "../pages/Admin/Ambulances";
import Patients from "../pages/Admin/Patients";
import SystemPrompt from "../pages/Admin/SystemPrompt";

const authProtectedRoutes = [
  { path: "/dashboard", component: <DashboardMedical /> },
  { path: "/medical-chat", component: <Medicalchat/> },
  { path: "/cases", component: <Cases/> },
  { path: "/admin/ambulances", component: <Ambulances/> },
  { path: "/admin/patients", component: <Patients/> },
  { path: "/admin/system-prompt", component: <SystemPrompt/> },
  { path: "/profile", component: <UserProfile /> },
  {
    path: "/",
    exact: true,
    component: <Navigate to="/dashboard" />,
  },
  { path: "*", component: <Navigate to="/dashboard" /> },
];

const publicRoutes = [
  // Authentication Page
  { path: "/logout", component: <Logout /> },
  { path: "/login", component: <Login /> },
  { path: "/forgot-password", component: <ForgetPasswordPage /> },
  { path: "/register", component: <Register /> },
];

export { authProtectedRoutes, publicRoutes };