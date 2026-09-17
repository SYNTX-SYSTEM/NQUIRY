import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "nquiry — Phase 0 skeleton",
  description: "NQUIRY architectural prototype — repository and toolchain skeleton (PKG-00).",
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
