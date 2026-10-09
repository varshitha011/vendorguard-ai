import type { Metadata } from "next";
import "./globals.css";
import "./refinements.css";
import { AppShell } from "@/components/Navbar";
import { DataProvider } from "@/components/DataProvider";
export const metadata: Metadata = { title: "VendorGuard — Supply intelligence workspace", description: "Monitor supplier health, review disruption alerts, and explore material coverage for packaging production." };
export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body><DataProvider><AppShell>{children}</AppShell></DataProvider></body></html>;
}
