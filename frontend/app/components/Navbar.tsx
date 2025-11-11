"use client";

import { UserDTO } from "../definitions";
import Link from "next/link";
import { useRouter } from "next/navigation";



type NavBarProp={
  user:UserDTO|null;
}
export default function NavBar({user}:NavBarProp){
    const router=useRouter();
   
   

    return (
<nav className="bg-white border-b border-gray-200">
  <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
    
    <h2 className="font-semibold text-gray-900 text-lg">
        Stockopedia
    </h2>

    <div className="flex items-center space-x-6">
      <Link href="/dashboard" className="text-gray-700 hover:text-gray-700">
        Dashboard
      </Link>
      <Link href="/news" className="text-gray-700 hover:text-gray-700">
        Stock News
      </Link>
      <Link href="/earnings-call" className="text-gray-700 hover:text-gray-700">
        Earnings Call
      </Link>

      <p className="text-gray-700">
        Buying Power: <span className="text-gray 900" >${user?.total_capital.toFixed(2)}</span>
      </p>

      <button
        className="px-3 py-1.5 bg-slate-700 hover:bg-gray-300 text-white font-bold rounded-md transition cursor-pointer"
        onClick={() => {
          localStorage.removeItem("token");
          router.push("/login");
        }}
      >
        Logout
      </button>

    </div>

  </div>
</nav>
  );
}