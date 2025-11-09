"use client";

import NavBar from "../components/Navbar";
export default function DashBoardLayout({
  children,
}:{
    children:React.ReactNode
}){
  return(
    <html lang="en">
      <body>
        <NavBar/>
        {children}
      </body>
    </html>
  )
}