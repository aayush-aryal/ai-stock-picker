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
          useEffect(() => {
              const token = localStorage.getItem("token");
              if (!token) {
              router.push("/login");
              return;
              }
      
              fetch("http://localhost:8000/auth/users/me", {
              headers: { Authorization: `Bearer ${token}` },
              })
              .then((res) => {
                  if (!res.ok) {
                  localStorage.removeItem("token");
                  router.push("/login");
                  throw new Error("Unauthorized");
                  }
                  return res.json();
              })
              .then(setUser)
              .catch(console.error)
              .finally(()=>setLoading(false));
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
    <ChartComponent/>
    <OwnedStocksTable/>
  </section>
</div>
      </div>

    )
}


