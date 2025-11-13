"use client"
import { useEffect, useState } from "react";
import ChartComponent from "../components/Chart";
import OwnedStocksTable from "../components/OwnedStocksTable";
import TopPredictions from "@/app/components/TopPredictions";
import NavBar from "../components/Navbar";
import { useRouter } from "next/navigation";
import { UserDTO } from "../definitions";
export default function Dashboard(){
          const router=useRouter();
          const [user,setUser]=useState<UserDTO| null>(null);
          const [loading, setLoading] = useState(true);
          const [portfolio,setPortfolio]=useState()
useEffect(() => {
  const checkUserAndPortfolio = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    try {
      // Fetch logged-in user
      const userRes = await fetch("http://localhost:8000/auth/users/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!userRes.ok) {
        localStorage.removeItem("token");
        router.push("/login");
        throw new Error("Unauthorized");
      }
      const userData = await userRes.json();
      setUser(userData);

      // Fetch portfolio after user is fetched
      const portfolioRes = await fetch(
        "http://localhost:8000/user-owned-stocks/get-portfolio",
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!portfolioRes.ok) throw new Error("Failed to fetch portfolio");
      const portfolioData = await portfolioRes.json();
      setPortfolio(portfolioData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  checkUserAndPortfolio();
}, [router]);

    if (loading) {
      return (
        <div className="flex items-center justify-center h-screen">
          <p>Loading dashboard...</p>
        </div>
      );
    }
      if (!user) {
    // user not found even after loading -> redirect to login
    router.push("/login");
    return null;
  }
    return (
      <div>
        <NavBar user={user}/>
               <div className="p-6 space-y-8">
  {/* Top Predictions */}
  <section className="bg-white rounded-xl shadow p-4">
    <TopPredictions />
  </section>

    {/* Owned Stocks */}
  <section className="flex-col items-center justify-center bg-white rounded-xl shadow p-4">
    
    <h1 className="font-bold text-3xl mb-10">{`${user?.username}'s Portfolio`}</h1>
    <ChartComponent data={portfolio||[]} 
      xKey="date" 
      yKey="portfolio_value" 
      yLabel="Value in dollars"
      />
    <OwnedStocksTable/>
  </section>
</div>
      </div>

    )
}


