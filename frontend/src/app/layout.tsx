import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'QuantLab — Quantitative Research Platform',
  description: 'Unified institutional quantitative research, backtesting, statistical validation, and market microstructure simulation environment.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-text-primary antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
