import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Header = () => {
  return (
    <header className="w-full">
      <nav className="container mx-auto px-6 py-6 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-primary text-primary-foreground flex items-center justify-center font-semibold">
            C
          </div>
          <div className="flex flex-col leading-none">
            <span className="text-lg font-semibold">Curia AI</span>
            <span className="text-xs text-muted-foreground">Meeting to Jira, instantly</span>
          </div>
        </Link>
        <div className="flex items-center gap-2">
          <Link to="/login">
            <Button variant="ghost">Login</Button>
          </Link>
          <Link to="/login">
            <Button className="cta-button">Get Started</Button>
          </Link>
        </div>
      </nav>
    </header>
  );
};

export default Header;
