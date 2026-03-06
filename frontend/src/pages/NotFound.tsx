import { useLocation } from "react-router-dom";
import { useEffect } from "react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-16">
      <div className="surface max-w-md p-8 text-center">
        <h1 className="text-4xl font-semibold mb-3">404</h1>
        <p className="text-sm text-muted-foreground mb-6">Page not found.</p>
        <a href="/" className="text-primary underline">
          Return to Home
        </a>
      </div>
    </div>
  );
};

export default NotFound;
