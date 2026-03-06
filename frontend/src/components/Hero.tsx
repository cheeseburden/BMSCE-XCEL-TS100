import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle2 } from "lucide-react";

const Hero = () => {
  return (
    <section className="relative overflow-hidden px-6 pb-16 pt-8">
      <div className="container mx-auto grid gap-12 lg:grid-cols-2 lg:items-center">
        <div className="space-y-8 animate-fade-in">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary/60 px-4 py-2 text-sm text-muted-foreground">
            <span className="h-2 w-2 rounded-full bg-primary" />
            Turn meetings into Jira tickets automatically
          </div>

          <div className="space-y-4">
            <h1 className="text-4xl font-semibold leading-tight md:text-6xl">
              Capture decisions. Ship action items.
              <span className="block text-primary">No manual Jira work.</span>
            </h1>
            <p className="text-lg text-muted-foreground">
              Curia AI analyzes meeting transcripts, extracts decisions and action items,
              and creates Jira tickets with the right priority and owners.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link to="/login">
              <Button size="lg" className="cta-button">
                Get Started
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline">
                Sign In
              </Button>
            </Link>
          </div>

          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-primary" />
              Jira tickets created in seconds
            </span>
            <span className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-primary" />
              Works with any transcript
            </span>
          </div>
        </div>

        <div className="surface p-8 animate-slide-right">
          <div className="space-y-6">
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Transcript</p>
              <p className="mt-2 text-sm text-slate-600">
                “Let’s ship the onboarding flow this week. Sam will finalize the UI by Friday.”
              </p>
            </div>
            <div className="rounded-xl border border-border bg-secondary/60 p-4">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Extracted Action</p>
              <p className="mt-2 text-sm font-medium">Finalize onboarding UI</p>
              <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                <span>Assignee: Sam</span>
                <span className="rounded-full bg-primary/10 px-2 py-1 text-primary">High</span>
              </div>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-border bg-white px-4 py-3">
              <span className="text-sm font-medium">Jira Issue</span>
              <span className="text-sm text-primary">CURIA-128</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
