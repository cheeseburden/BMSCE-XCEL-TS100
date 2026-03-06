import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, CheckCircle, ExternalLink, Save } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { JiraConfig, getJiraConfig, saveJiraConfig } from "@/lib/session";

const Settings = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [config, setConfig] = useState<JiraConfig>({
    jiraUrl: "",
    jiraProjectKey: "",
    jiraEmail: "",
    jiraApiToken: "",
    jiraIssueType: "Task",
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = getJiraConfig();
    if (stored) {
      setConfig(prev => ({ ...prev, ...stored }));
      setSaved(true);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfig(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    setSaved(false);
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    const normalized = saveJiraConfig(config);
    setConfig(normalized);
    setSaved(true);
    toast({ title: "Settings Saved", description: "Jira configuration updated successfully" });
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen px-6 py-12">
      <div className="container mx-auto max-w-2xl space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <Button variant="ghost" onClick={() => navigate("/dashboard")} className="mb-3">
              <ArrowLeft className="mr-2 h-4 w-4" /> Back to Meetings
            </Button>
            <h1 className="text-3xl font-semibold">Jira Settings</h1>
            <p className="text-sm text-muted-foreground">
              Add your Jira workspace credentials to create tickets automatically.
            </p>
          </div>
        </div>

        <Card className="surface">
          <CardHeader>
            <CardTitle>Connect Jira</CardTitle>
            <CardDescription>
              Generate an API token from Atlassian and store it securely in your browser.
              <a
                href="https://id.atlassian.com/manage-profile/security/api-tokens"
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 inline-flex items-center gap-1 text-primary"
              >
                Get API token <ExternalLink className="h-3 w-3" />
              </a>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSave} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="jiraUrl">Jira URL</Label>
                <Input
                  id="jiraUrl"
                  name="jiraUrl"
                  type="url"
                  placeholder="https://yourteam.atlassian.net"
                  value={config.jiraUrl}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="jiraProjectKey">Project Key</Label>
                <Input
                  id="jiraProjectKey"
                  name="jiraProjectKey"
                  type="text"
                  placeholder="e.g. CURIA"
                  value={config.jiraProjectKey}
                  onChange={handleChange}
                  required
                  className="uppercase"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="jiraEmail">Jira Email</Label>
                <Input
                  id="jiraEmail"
                  name="jiraEmail"
                  type="email"
                  placeholder="you@company.com"
                  value={config.jiraEmail}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="jiraApiToken">API Token</Label>
                <Input
                  id="jiraApiToken"
                  name="jiraApiToken"
                  type="password"
                  placeholder="Paste your Jira API token"
                  value={config.jiraApiToken}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="jiraIssueType">Issue Type</Label>
                <Input
                  id="jiraIssueType"
                  name="jiraIssueType"
                  type="text"
                  placeholder="Task"
                  value={config.jiraIssueType || ""}
                  onChange={handleChange}
                />
                <p className="text-xs text-muted-foreground">
                  Optional. Use the exact issue type name in your Jira project (e.g., Task, Story).
                </p>
              </div>

              <Button type="submit" className="w-full cta-button">
                {saved ? (
                  <>
                    <CheckCircle className="mr-2 h-4 w-4" /> Saved
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" /> Save & Continue
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Settings;
