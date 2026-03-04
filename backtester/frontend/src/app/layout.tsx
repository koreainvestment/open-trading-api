import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout";
import { Providers } from "@/components/providers/Providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "KIS Backtest Framework",
  description: "KIS Backtest Framework",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen`}
      >
        <Providers>
          <Header />
          <main className="min-h-[calc(100vh-4rem)]">{children}</main>
          <footer className="border-t border-slate-200 dark:border-slate-800">
            <div className="max-w-7xl mx-auto px-4 py-4">
              <p className="text-center text-sm text-slate-500">
                KIS Backtest Framework &copy; 2026. Built with Next.js & Lean Engine.
              </p>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  );
}
