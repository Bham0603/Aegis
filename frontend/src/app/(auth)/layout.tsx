import { AegisMark } from "@/components/marketing/AnnouncementBar";

/**
 * Minimal layout for authentication routes — no navbar/footer,
 * focused atmosphere. Matches the Aegis design system.
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex min-h-screen flex-col bg-background">
      <div
        aria-hidden="true"
        className="absolute inset-0 glow-top pointer-events-none"
      />
      <header className="relative z-10 flex h-16 items-center px-4 sm:px-6 lg:px-10">
        <AegisMark />
      </header>
      <main className="relative z-10 flex flex-1 items-center justify-center px-4 py-10">
        {children}
      </main>
    </div>
  );
}
