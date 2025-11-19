"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import Link from "next/link";
import { useUser } from "@/app/contexts/userContext";

export default function ClientNav() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const { user } = useUser();

  const handleSearch = () => {
    if (!query.trim()) return;
    router.push(`/stock/${query.toUpperCase()}`);
    setQuery("");
  };

  if (!user?.full_name) return null;

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-blue-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div
          className="
            flex flex-wrap items-center justify-between gap-4
            py-3
          "
        >
          {/* Brand */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-md bg-blue-600 flex items-center justify-center text-white font-bold shadow-sm">
              S
            </div>
            <span className="text-blue-700 font-semibold text-lg whitespace-nowrap">
              Stockopedia
            </span>
          </Link>

          {/* Search */}
          <div className="flex-1 min-w-[220px] max-w-xl flex items-center gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search stock (AAPL, TSLA...)"
              className="
                w-full border border-blue-200 rounded-lg px-3 py-2
                focus:outline-none focus:ring-2 focus:ring-blue-400
              "
            />
            <button
              onClick={handleSearch}
              className="
                px-4 py-2 bg-blue-600 text-white rounded-lg
                hover:bg-blue-700 transition whitespace-nowrap
              "
            >
              Search
            </button>
          </div>

          {/* Right side actions */}
          <div
            className="
              flex items-center gap-6
              text-sm min-w-[220px] justify-end flex-wrap
            "
          >
            <Link
              href="/dashboard"
              className="text-gray-700 hover:text-blue-700 whitespace-nowrap"
            >
              Dashboard
            </Link>

            <div className="text-gray-700 whitespace-nowrap">
              Buying Power:
              <span className="ml-2 text-blue-700 font-semibold">
                ${Number(user.total_capital).toFixed(2)}
              </span>
            </div>

            <button
              onClick={() => {
                localStorage.removeItem("token");
                router.push("/login");
              }}
              className="
                px-3 py-2 bg-blue-600 text-white rounded-md
                hover:bg-blue-700 transition whitespace-nowrap
              "
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
