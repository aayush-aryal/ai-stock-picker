"use client";

import NavBar from "../components/Navbar";
export default function DashBoardLayout({
  children,
}:{
    children:React.ReactNode
}){
  return(
        <div>
            <main> {children}</main>
        </div>
  )
}