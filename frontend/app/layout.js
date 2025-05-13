import { Geist, Geist_Mono } from "next/font/google";
import { AIModelProvider } from "./AIModelContext";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "AI Agent Chat",
  description: "Create AI Agents team",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <AIModelProvider>{children}</AIModelProvider>
      </body>
    </html>
  );
}
