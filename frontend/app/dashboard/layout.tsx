"use client";
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