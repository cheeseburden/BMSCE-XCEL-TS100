import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, ClipboardCheck, Link2 } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI Summary in Minutes",
    description: "Clean decisions and action items extracted from any transcript, ready to share."
  },
  {
    icon: ClipboardCheck,
    title: "Structured Action Items",
    description: "Each task includes owner, priority, and due date to keep teams accountable."
  },
  {
    icon: Link2,
    title: "Instant Jira Tickets",
    description: "Push action items directly into Jira and track progress in one place."
  },
];

const Features = () => {
  return (
    <section id="features" className="py-16 px-6">
      <div className="container mx-auto">
        <div className="text-center space-y-4 mb-12">
          <h2 className="text-3xl font-semibold md:text-4xl">Everything you need to ship fast</h2>
          <p className="text-base text-muted-foreground max-w-2xl mx-auto">
            Curia AI keeps meetings lightweight and outcomes structured for delivery.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card
                key={index}
                className="surface h-full animate-fade-in"
                style={{ animationDelay: `${index * 80}ms` }}
              >
                <CardHeader className="space-y-4">
                  <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Features;
