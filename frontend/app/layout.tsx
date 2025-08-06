// app/layout.tsx
import { ReactNode } from 'react';
import { AuthProvider } from '@/context/AuthContext';

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html>
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
