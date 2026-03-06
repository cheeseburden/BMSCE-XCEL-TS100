import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle2 } from "lucide-react";

const About = () => {
  return (
    <section id="about" className="py-16 px-6">
      <div className="container mx-auto">
        <div className="grid gap-10 lg:grid-cols-2 lg:items-center">
          <div className="space-y-6 animate-fade-in">
            <h2 className="text-3xl font-semibold md:text-4xl">
              A clean workflow from meeting to Jira
            </h2>
            <p className="text-muted-foreground">
              Paste a transcript, run analysis, and get Jira tickets created with the
              right priorities. Curia AI keeps everything readable and fast.
            </p>
            <div className="space-y-3">
              {[
                "Paste transcript or add later",
                "AI extracts decisions and action items",
                "Tickets created directly in your Jira project"
              ].map((item) => (
                <div key={item} className="flex items-center gap-3 text-sm text-muted-foreground">
                  <CheckCircle2 className="h-4 w-4 text-primary" />
                  {item}
                </div>
              ))}
            </div>
            <Link to="/login">
              <Button size="lg" className="cta-button">
                Start now
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>

          <div className="surface p-8 animate-slide-right">
            <div className="space-y-4">
              <div className="rounded-xl border border-border bg-white p-4">
                <p className="text-xs uppercase text-muted-foreground">Meeting</p>
                <p className="mt-2 text-sm font-medium">Weekly Sprint Planning</p>
                <p className="text-xs text-muted-foreground">Transcript attached</p>
              </div>
              <div className="rounded-xl border border-border bg-secondary/60 p-4">
                <p className="text-xs uppercase text-muted-foreground">Decision</p>
                <p className="mt-2 text-sm">Ship onboarding flow by Friday.</p>
              </div>
              <div className="rounded-xl border border-border bg-white p-4">
                <p className="text-xs uppercase text-muted-foreground">Action Item</p>
                <p className="mt-2 text-sm font-medium">Finalize UI + QA checklist</p>
                <p className="mt-1 text-xs text-muted-foreground">Priority: High</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
