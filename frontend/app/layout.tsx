import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { Sparkles, FileText, Upload, Settings } from "lucide-react";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Content Engine",
  description: "High-quality X/Twitter content generation via multi-agent AI pipeline",
};

const navItems = [
  { href: "/generate", label: "Generate", icon: Sparkles },
  { href: "/traces", label: "Traces", icon: FileText },
  { href: "/uploads", label: "Uploads", icon: Upload },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} dark`}>
      <body className="min-h-screen bg-zinc-950 text-zinc-100 flex">
        <aside className="w-60 border-r border-zinc-800 flex flex-col p-4 shrink-0">
          <Link href="/" className="text-lg font-bold mb-8 tracking-tight">
            Content Engine
          </Link>
          <nav className="flex flex-col gap-1">
            {navItems.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
              >
                <Icon size={16} />
                {label}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </body>
    </html>
  );
}
