import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { hasJiraConfig, isAuthenticated, loginDemo } from "@/lib/session";

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isAuthenticated()) {
      navigate(hasJiraConfig() ? "/dashboard" : "/settings", { replace: true });
    }
  }, [navigate]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    setTimeout(() => {
      if (formData.email && formData.password.length >= 4) {
        loginDemo(formData.email);
        navigate(hasJiraConfig() ? "/dashboard" : "/settings");
      } else {
        setError("Please enter a valid email and password (min 4 chars)");
      }
      setLoading(false);
    }, 300);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    if (error) setError("");
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-16">
      <Card className="surface w-full max-w-md">
        <CardHeader className="space-y-2">
          <CardTitle className="text-2xl font-semibold">Welcome back</CardTitle>
          <CardDescription>Sign in to continue to Curia AI.</CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="you@company.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="Minimum 4 characters"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            <Button type="submit" disabled={loading} className="w-full cta-button">
              {loading ? "Signing In..." : "Sign In"}
            </Button>
          </form>

          <p className="text-xs text-muted-foreground">
            Demo login accepts any email + password (min 4 characters).
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
