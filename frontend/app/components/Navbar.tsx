"use client";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useState } from "react";
import { UserDTO } from "../definitions";

type NavBarProp = {
  user: UserDTO | null;
};

export default function NavBar({ user }: NavBarProp) {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    if (!query.trim()) return;
    router.push(`/stock/${query.toUpperCase()}`); // dynamic stock page
    setQuery("");
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
        

        <h2 className="font-semibold text-gray-900 text-lg">Stockopedia</h2>
        <div className="flex items-center space-x-2 w-[300px]">
          <input
            type="text"
            placeholder="Search a stock (e.g. AAPL)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-slate-700"
          />
          <button
            onClick={handleSearch}
            className="bg-slate-700 text-white px-3 py-1.5 rounded-lg hover:bg-slate-800 transition"
          >
            Search
          </button>
        </div>

        <div className="flex items-center space-x-6">
          <Link href="/dashboard" className="text-gray-700 hover:text-slate-900">
            Dashboard
          </Link>
          <p className="text-gray-700">
            Buying Power:{" "}
            <span className="text-gray-900 font-medium">
              ${user?.total_capital.toFixed(2)}
            </span>
          </p>
          <button
            className="px-3 py-1.5 bg-slate-700 hover:bg-slate-800 text-white font-bold rounded-md transition"
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
