import type { Metadata } from "next";
import { Geist, Geist_Mono, Noto_Sans_KR } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/layout";
import { Providers } from "@/components/providers/Providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const notoSansKR = Noto_Sans_KR({
  variable: "--font-noto-sans-kr",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "KIS Strategy Builder - 전략 빌더",
  description: "한국투자증권 API 기반 퀀트 전략 프레임워크",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body
        className={`${notoSansKR.variable} ${geistSans.variable} ${geistMono.variable} antialiased min-h-screen`}
      >
        <Providers>
          <Navigation />
          <main className="min-h-[calc(100vh-4rem)]">{children}</main>
          <footer className="border-t border-slate-200 dark:border-slate-800">
            <div className="max-w-7xl mx-auto px-4 py-4">
              <p className="text-center text-sm text-slate-500">
                투자에는 원금 손실의 위험이 있으며, 과거 성과가 미래를 보장하지 않습니다.
              </p>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  );
}
