import type { Metadata } from 'next';
import './globals.css';
import { Providers } from '@/components/providers';

export const metadata: Metadata = {
  title: 'PRAGYA | AI-Powered Competency & Workforce Intelligence Platform',
  description:
    'Capacity building and competency-based personalized learning platform for India’s Official Statistical System (MoSPI). Assess • Learn • Improve • Predict.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#070A13] text-[#F8FAFC] selection:bg-cyan-500/30 selection:text-cyan-200">
        <Providers>
          <div className="min-h-screen flex flex-col relative overflow-hidden">
            {/* Subtle futuristic background ambient glow */}
            <div className="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 w-[800px] h-[350px] bg-gradient-to-r from-cyan-500/10 via-violet-500/10 to-transparent blur-3xl opacity-70" />
            <main className="flex-1 flex flex-col relative z-10">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
