"use client";
import "@/app/globals.css";
import NavBar from "./components/Navbar";
import { UserProvider } from "./contexts/userContext";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <UserProvider>
          <NavBar />
          {children}
        </UserProvider>
      </body>
    </html>
  );
}
