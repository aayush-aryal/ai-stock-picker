"use client";
import NavBar from "@/app/components/Navbar";
import { UserDTO } from "@/app/definitions";
import { useEffect, useState } from "react";

type StockInfoType = {
  symbol: string;
  address: string;
  city: string;
  country: string;
  phone: string;
  zip: string;
  industry: string;
  sector: string;
  long_business_summary: string;
  full_time_employees: number;
  web_site: string;
};

type StockInfoResponse = {
  ticker: string;
  info: StockInfoType[];
};

export default function StockInfoPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {

  const [stockInfo, setStockInfo] = useState<StockInfoType | null>(null);
  const [user,setUser]=useState<UserDTO|null>(null);
  useEffect(() => {
    async function loadData() {
      const { ticker } = await params;
      const token=localStorage.getItem("token")
      const stockrequest = await fetch(
        `http://localhost:8000/ticker/get-ticker-info?ticker=${ticker}`
      );
      const stockinfo: StockInfoResponse = await stockrequest.json();
      setStockInfo(stockinfo.info[0]);
      const userrequest=await fetch(
        "http://localhost:8000/auth/users/me",{
            headers:{Authorization:`Bearer ${token}`}
        });
    
      const user=await userrequest.json()
      setUser(user)
      
      
    }
    loadData();
  }, []);

  if (!stockInfo) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-gray-500 text-lg">Loading stock information...</p>
      </div>
    );
  }

  return (
    <>
        <NavBar user={user} />
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Navbar */}
   

      {/* Stock Info Card */}
      <div className="bg-white shadow-lg rounded-xl p-6 max-w-3xl mx-auto">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold text-gray-800">{stockInfo.symbol}</h1>
          <span className="text-gray-500">{stockInfo.industry} / {stockInfo.sector}</span>
        </div>

        <div className="text-gray-700 space-y-1 mb-4">
          <p>{stockInfo.address}</p>
          <p>{stockInfo.city}, {stockInfo.country} {stockInfo.zip}</p>
          <p>Phone: {stockInfo.phone}</p>
          {stockInfo.full_time_employees && (
            <p>Employees: {stockInfo.full_time_employees.toLocaleString()}</p>
          )}
          {stockInfo.web_site && (
            <p>
              Website:{" "}
              <a
                href={stockInfo.web_site}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {stockInfo.web_site}
              </a>
            </p>
          )}
        </div>

        <div className="mt-6 text-gray-800 leading-relaxed">
          <h2 className="text-xl font-semibold mb-2">Business Summary</h2>
          <p>{stockInfo.long_business_summary}</p>
        </div>
      </div>
    </div>
    </>
    
  );
}
