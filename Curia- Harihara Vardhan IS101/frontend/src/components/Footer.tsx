const Footer = () => {
  return (
    <footer className="border-t border-border py-10 px-6">
      <div className="container mx-auto flex flex-col gap-4 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-primary text-primary-foreground flex items-center justify-center font-semibold">
            C
          </div>
          <span>Curia AI</span>
        </div>
        <p>Automate meeting outcomes, stay focused on shipping.</p>
        <p>© 2026 Curia AI</p>
      </div>
    </footer>
  );
};

export default Footer;
