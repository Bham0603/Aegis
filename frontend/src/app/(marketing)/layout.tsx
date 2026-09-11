import { AnnouncementBar } from "@/components/marketing/AnnouncementBar";
import { Navbar } from "@/components/marketing/Navbar";
import { Footer } from "@/components/marketing/Footer";

/**
 * Layout for public marketing routes.
 * Auth routes ((auth) group) opt out via their own nested layout.
 */
export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <AnnouncementBar />
      <Navbar />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
