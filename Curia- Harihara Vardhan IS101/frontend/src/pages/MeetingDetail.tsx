import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import meetingService from "@/services/meetingService";
import { getJiraConfig } from "@/lib/session";

interface ActionItem {
  Summary: string;
  Assignee: string;
  Priority: string;
  "Due date": string;
  jiraIssueKey?: string;
}

interface Meeting {
  _id: string;
  title: string;
  meetUrl?: string;
  transcript: string;
  summary: {
    decisions: string[];
    action_items: ActionItem[];
  };
  status: string;
  jiraIssuesCreated: boolean;
  jiraErrors?: { summary: string; error: string }[];
  createdAt: string;
}

const MeetingDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [transcriptText, setTranscriptText] = useState("");
  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  const jiraConfig = getJiraConfig();
  const jiraBaseUrl = jiraConfig?.jiraUrl ? jiraConfig.jiraUrl.replace(/\/$/, "") : "";

  useEffect(() => {
    fetchMeeting();
  }, [id]);

  const fetchMeeting = async () => {
    try {
      setLoading(true);
      const data = await meetingService.getMeetingById(id!);
      if (data.success) {
        setMeeting(data.meeting);
        setTranscriptText(data.meeting.transcript || "");
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to load meeting.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const saveTranscript = async () => {
    try {
      setSaving(true);
      const data = await meetingService.addTranscript(id!, transcriptText);
      if (data.success) {
        setMeeting(data.meeting);
        setEditing(false);
        toast({ title: "Transcript saved", description: "Ready for analysis." });
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to save transcript.", variant: "destructive" });
    } finally {
      setSaving(false);
    }
  };

  const analyze = async () => {
    if (!jiraConfig) {
      toast({ title: "Missing Jira config", description: "Please add Jira settings first.", variant: "destructive" });
      navigate("/settings");
      return;
    }

    try {
      setAnalyzing(true);
      toast({ title: "Analyzing", description: "AI is processing the transcript." });
      const data = await meetingService.analyzeMeeting(id!);
      if (data.success) {
        setMeeting(data.meeting);
        toast({ title: "Analysis complete", description: data.message || "Jira tickets created." });
      } else {
        toast({ title: "Error", description: data.message || "Analysis failed.", variant: "destructive" });
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to analyze meeting.", variant: "destructive" });
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen px-6 py-12">Loading...</div>;
  }

  if (!meeting) {
    return (
      <div className="min-h-screen px-6 py-12">
        <p className="text-muted-foreground">Meeting not found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-12">
      <div className="container mx-auto max-w-5xl space-y-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <Button variant="ghost" onClick={() => navigate("/dashboard")} className="mb-2">
              ← Back to Meetings
            </Button>
            <h1 className="text-3xl font-semibold">{meeting.title}</h1>
            <p className="text-sm text-muted-foreground">
              {meeting.status} · {new Date(meeting.createdAt).toLocaleDateString()}
            </p>
          </div>
          <Button onClick={analyze} disabled={analyzing || !meeting.transcript} className="cta-button">
            {analyzing ? "Analyzing..." : "Analyze & Create Jira Tickets"}
          </Button>
        </div>

        <Card className="surface">
          <CardHeader>
            <CardTitle>Transcript</CardTitle>
            <CardDescription>Paste or edit the meeting transcript below.</CardDescription>
          </CardHeader>
          <CardContent>
            {editing ? (
              <div className="space-y-3">
                <Textarea
                  value={transcriptText}
                  onChange={(e) => setTranscriptText(e.target.value)}
                  rows={12}
                />
                <div className="flex gap-2">
                  <Button onClick={saveTranscript} className="cta-button" disabled={saving}>
                    {saving ? "Saving..." : "Save Transcript"}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setEditing(false);
                      setTranscriptText(meeting.transcript || "");
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : meeting.transcript ? (
              <div className="space-y-3">
                <pre className="whitespace-pre-wrap rounded-lg bg-secondary/60 p-4 text-sm text-slate-600">
                  {meeting.transcript}
                </pre>
                <Button variant="outline" onClick={() => setEditing(true)}>
                  Edit Transcript
                </Button>
              </div>
            ) : (
              <div className="space-y-3 text-sm text-muted-foreground">
                <p>No transcript yet. Add one to analyze the meeting.</p>
                <Button onClick={() => setEditing(true)} variant="outline">
                  Add Transcript
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {meeting.summary && (meeting.summary.decisions?.length > 0 || meeting.summary.action_items?.length > 0) && (
          <div className="grid gap-6 md:grid-cols-2">
            <Card className="surface">
              <CardHeader>
                <CardTitle>Decisions</CardTitle>
                <CardDescription>Key decisions captured from the transcript.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                {meeting.summary.decisions.length === 0 ? (
                  <p className="text-muted-foreground">No decisions detected.</p>
                ) : (
                  meeting.summary.decisions.map((decision, index) => (
                    <div key={index} className="rounded-lg border border-border bg-white p-3">
                      {decision}
                    </div>
                  ))
                )}
              </CardContent>
            </Card>

            <Card className="surface">
              <CardHeader>
                <CardTitle>Action Items</CardTitle>
                <CardDescription>
                  {meeting.jiraIssuesCreated ? "Jira tickets created." : "No Jira tickets created yet."}
                </CardDescription>
              </CardHeader>
              <CardContent>

                {meeting.summary.action_items.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No action items detected.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border text-left text-xs uppercase text-muted-foreground">
                          <th className="py-2">Task</th>
                          <th className="py-2">Assignee</th>
                          <th className="py-2">Priority</th>
                          <th className="py-2">Jira</th>
                        </tr>
                      </thead>
                      <tbody>
                        {meeting.summary.action_items.map((item, index) => {
                          const issueUrl = item.jiraIssueKey && jiraBaseUrl
                            ? `${jiraBaseUrl}/browse/${item.jiraIssueKey}`
                            : "";
                          return (
                            <tr key={index} className="border-b border-border">
                              <td className="py-3 pr-2">{item.Summary}</td>
                              <td className="py-3 pr-2 text-muted-foreground">{item.Assignee}</td>
                              <td className="py-3 pr-2 text-muted-foreground">{item.Priority}</td>
                              <td className="py-3 text-primary">
                                {item.jiraIssueKey ? (
                                  <a href={issueUrl} target="_blank" rel="noreferrer">
                                    {item.jiraIssueKey}
                                  </a>
                                ) : (
                                  <span className="text-muted-foreground">—</span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default MeetingDetail;
