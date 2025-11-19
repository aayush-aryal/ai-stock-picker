"use client";
import { useEffect, useState } from "react";
import ChartComponent from "../components/Chart";
import OwnedStocksTable from "../components/OwnedStocksTable";
import TopPredictions from "@/app/components/TopPredictions";
import { useRouter } from "next/navigation";
import { useUser } from "../contexts/userContext";

type UserStock = {
  id: number;
  username: string;
  date: string;
  shares: string;
  stock: string;
  avg_buy_price: number;
  gain_loss: number;
  gain_loss_pct: number;
  latest_close: number;
};

export default function Dashboard() {
  const router = useRouter();
  const { user } = useUser();
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolio] = useState();
  const [stocks, setStocks] = useState<UserStock[]>([]);
  const [error, setError] = useState("");
  const [portfolioValue, setPortfolioValue] = useState(0);
  const [investmentAmount, setInvestmentAmount] = useState(0);
  useEffect(() => {
    const checkUserAndPortfolio = async () => {
      try {
        // Fetch logged-in user
        console.log("suna hai ta", user);

        const portfolioRes = await fetch(
          "http://localhost:8000/user-owned-stocks/get-portfolio",
          { credentials: "include" }
        );
        if (!portfolioRes.ok) {
          // router.push("/login");
        }
        const portfolioData = await portfolioRes.json();
        setPortfolio(portfolioData);

        // get the stock table
        const res = await fetch(
          "http://localhost:8000/user-owned-stocks/get-stocks",
          {
            method: "GET",
            credentials: "include",
          }
        );
        if (!res.ok) {
          setError("Something went wrong!");
          return;
        }
        const data = await res.json();
        console.log(data);
        setStocks(data.stocks);
      } catch (err) {
        router.push("/login");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    checkUserAndPortfolio();
  }, [router, user]);

  console.log("lamo mug", user);

  useEffect(() => {
    const totalInvestment = stocks.reduce(
      (acc, stock) => acc + stock.avg_buy_price * Number(stock.shares),
      0
    );
    setInvestmentAmount(totalInvestment);

    const totalPortfolio = stocks.reduce(
      (acc, stock) => acc + stock.latest_close * Number(stock.shares),
      0
    );
    setPortfolioValue(totalPortfolio);
  }, [stocks]);

  if (loading || !user) {
    // Show full-screen loading until both user and portfolio are ready
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-white">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-xl font-medium text-blue-800">
            Loading dashboard...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6 space-y-8 max-w-7xl mx-auto">
        {/* Top Predictions */}
        <section className="bg-white rounded-2xl shadow-lg border border-blue-100 p-6 transition-all duration-200 hover:shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-blue-900">
              Top Predictions
            </h2>
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
          </div>
          <TopPredictions />
        </section>

        {/* Owned Stocks */}
        <section className="flex-col items-center justify-center bg-white rounded-2xl shadow-lg border border-blue-100 p-6 transition-all duration-200 hover:shadow-xl">
          <div className="flex items-center justify-between mb-10">
            <h1 className="font-bold text-3xl text-blue-900">{`${user.username}'s Portfolio`}</h1>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-blue-400">Current Value</p>
                <p className="text-2xl font-bold text-blue-900">
                  ${portfolioValue?.toLocaleString() || "0.00"}
                </p>
              </div>
            </div>
          </div>

          <div className="mb-8">
            <ChartComponent
              data={portfolio || []}
              xKey="date"
              yKey="portfolio_value"
              yLabel="Value in dollars"
            />
          </div>

          <OwnedStocksTable
            error={error}
            stocks={stocks}
            portfolioValue={portfolioValue}
            investmentAmount={investmentAmount}
          />
        </section>
      </div>
    </div>
  );
}
