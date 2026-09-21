import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "nquiry",
  description: "NQUIRY architectural prototype — local login and Session view.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
