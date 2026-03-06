import { Navigate, useLocation } from "react-router-dom";
import { hasJiraConfig, isAuthenticated } from "@/lib/session";

export const RequireAuth = ({ children }: { children: JSX.Element }) => {
  const location = useLocation();
  if (!isAuthenticated()) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
};

export const RequireJira = ({ children }: { children: JSX.Element }) => {
  if (!hasJiraConfig()) {
    return <Navigate to="/settings" replace />;
  }
  return children;
};
