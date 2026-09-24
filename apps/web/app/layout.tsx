import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "nquiry",
  description: "NQUIRY — governed inquiry: Workspaces, Challenges, Sessions.",
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
