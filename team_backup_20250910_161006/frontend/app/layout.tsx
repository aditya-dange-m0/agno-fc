import './globals.css';
export const metadata = {
  title: 'PLM System',
  description: 'Project Lifecycle Management Application',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-100">{children}</body>
    </html>
  );
}