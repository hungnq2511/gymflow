import type { Metadata } from 'next';
import { ApiLoadingIndicator } from '@/components/api-loading-indicator';
import './globals.css';

export const metadata: Metadata = {
  title: 'GymFlow — Quản lý phòng gym',
  description: 'Quản lý hội viên, gói tập, thanh toán và check-in tại một nơi.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body className="antialiased">
        <ApiLoadingIndicator />
        {children}
      </body>
    </html>
  );
}
