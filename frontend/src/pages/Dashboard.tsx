import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import meetingService from "@/services/meetingService";
import { logout } from "@/lib/session";

interface Meeting {
  _id: string;
  title: string;
  meetUrl?: string;
  status: string;
  jiraIssuesCreated: boolean;
  summary?: {
    decisions: string[];
    action_items: { jiraIssueKey?: string }[];
  };
  createdAt: string;
}

const Dashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState("");
  const [meetUrl, setMeetUrl] = useState("");
  const [transcript, setTranscript] = useState("");

  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = async () => {
    try {
      setLoading(true);
      const data = await meetingService.getMeetings();
      if (data.success) setMeetings(data.meetings);
    } catch (error) {
      toast({ title: "Error", description: "Failed to load meetings", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      setCreating(true);
      const data = await meetingService.createMeeting({
        title: title.trim(),
        meetUrl: meetUrl || undefined,
        transcript: transcript || undefined
      });
      if (data.success) {
        toast({ title: "Meeting created", description: "Ready to analyze the transcript." });
        setTitle("");
        setMeetUrl("");
        setTranscript("");
        await fetchMeetings();
        if (data.meeting?._id) {
          navigate(`/meeting/${data.meeting._id}`);
        }
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to create meeting", variant: "destructive" });
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Delete this meeting?")) return;
    try {
      await meetingService.deleteMeeting(id);
      toast({ title: "Deleted", description: "Meeting removed." });
      fetchMeetings();
    } catch (error) {
      toast({ title: "Error", description: "Failed to delete meeting.", variant: "destructive" });
    }
  };

  const statusBadge = (status: string) => {
    if (status === "analyzed") return "bg-green-100 text-green-700";
    if (status === "completed") return "bg-blue-100 text-blue-700";
    return "bg-yellow-100 text-yellow-700";
  };

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="container mx-auto space-y-8">
        <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Curia AI</p>
            <h1 className="text-3xl font-semibold">Meetings</h1>
            <p className="text-sm text-muted-foreground">
              Create meetings, add transcripts, analyze into Jira tickets.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate("/settings")}>
              Jira Settings
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                logout();
                navigate("/login");
              }}
            >
              Logout
            </Button>
          </div>
        </header>

        <Card className="surface">
          <CardHeader>
            <CardTitle>New Meeting</CardTitle>
            <CardDescription>Create a meeting and optionally paste a transcript.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="title">Meeting Title</Label>
                  <Input
                    id="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Sprint Planning - March 6"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="meetUrl">Meet URL (optional)</Label>
                  <Input
                    id="meetUrl"
                    value={meetUrl}
                    onChange={(e) => setMeetUrl(e.target.value)}
                    placeholder="https://meet.google.com/..."
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="transcript">Transcript (optional)</Label>
                <Textarea
                  id="transcript"
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  placeholder="Paste the meeting transcript here..."
                  rows={5}
                />
              </div>
              <Button type="submit" className="cta-button" disabled={creating}>
                {creating ? "Creating..." : "Create Meeting"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Recent Meetings</h2>
            <span className="text-sm text-muted-foreground">{meetings.length} total</span>
          </div>

          {loading ? (
            <div className="surface p-6 text-sm text-muted-foreground">Loading meetings...</div>
          ) : meetings.length === 0 ? (
            <div className="surface p-6 text-sm text-muted-foreground">
              No meetings yet. Create your first meeting above.
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {meetings.map((meeting) => (
                <Card
                  key={meeting._id}
                  className="surface cursor-pointer transition hover:-translate-y-0.5"
                  onClick={() => navigate(`/meeting/${meeting._id}`)}
                >
                  <CardHeader className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="text-lg">{meeting.title}</CardTitle>
                      <span className={`rounded-full px-2 py-1 text-xs ${statusBadge(meeting.status)}`}>
                        {meeting.status}
                      </span>
                    </div>
                    <CardDescription>
                      {new Date(meeting.createdAt).toLocaleDateString()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex items-center justify-between">
                    <div className="text-xs text-muted-foreground">
                      {meeting.summary?.action_items?.length || 0} action items
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => handleDelete(meeting._id, e)}
                    >
                      Delete
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
