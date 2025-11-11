"use client";
import { useState, useEffect } from "react";


type UserStock={
    id:number;
    username:string;
    date:string;
    shares:string;
    stock:string;
    avg_buy_price:number;
    gain_loss:number;
    gain_loss_pct:number;
    latest_close:number;
}

// for now i wont use it 
// type StockWithPrice=UserStock &{
//     current_price:string;
//     marketValue:string;
// }


export default function OwnedStocksTable(){
    const [stocks,setStocks]=useState<UserStock[]>([]);
    const [error,setError]=useState("")
    const [portfolioValue, setPortfolioValue]=useState(0)
    const [investmentAmount, setInvestmentAmount]=useState(0)
    useEffect(()=>{
        async function loadData(){
            try{
                const token=localStorage.getItem("token")
                const res=await fetch("http://localhost:8000/user-owned-stocks/get-stocks",{
                    method:"GET",
                    headers:{
                        Authorization:`Bearer ${token}`
                    }
                })
                if (!res.ok){
                    setError("Something went wrong!")
                    return;
                }
                const data=await res.json()
                setStocks(data.stocks)
                console.log(data)
            }catch{
                setError("Something went wrong")
            }
        }
        loadData();
      

    },[])

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

 
if (stocks.length === 0) {
  return <p>Loading portfolio...</p>;
}

return (
  <>
    <div className="flex flex-wrap gap-6 mb-6">
  <div className="flex-1 min-w-[150px] p-4 bg-white rounded-2xl shadow border border-gray-200">
    <h3 className="text-gray-500 text-sm mb-1">Invested</h3>
    <p className="text-xl font-bold">${investmentAmount.toFixed(2)}</p>
  </div>

  <div className="flex-1 min-w-[150px] p-4 bg-white rounded-2xl shadow border border-gray-200">
    <h3 className="text-gray-500 text-sm mb-1">Current Value</h3>
    <p className="text-xl font-bold">${portfolioValue.toFixed(2)}</p>
  </div>
  </div>

    <p>{error}</p>
    <div className="p-4 bg-white rounded-xl shadow border border-gray-300">
      <table className="w-full text-sm text-gray-700">
        <thead>
          <tr className="bg-gray-50 text-left">
            <th className="px-4 py-2 font-semibold">Stock</th>
            <th className="px-4 py-2 font-semibold">Shares</th>
            <th className="px-4 py-2 font-semibold">Last Transaction</th>
            <th className="px-4 py-2 font-semibold">Avg Buy Price</th>
            <th className="px-4 py-2 font-semibold">Latest Close</th>
            <th className="px-4 py-2 font-semibold">Gain/Loss</th>
            <th className="px-4 py-2 font-semibold">Gain/Loss %</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => (
            <tr key={stock.id} className="border-b border-gray-200">
              <td className="px-4 py-2">{stock.stock}</td>
              <td className="px-4 py-2">{stock.shares?Number(stock.shares).toFixed(2):stock.shares}</td>
              <td className="px-4 py-2">{stock.date}</td>
              <td className="px-4 py-2">{stock.avg_buy_price?.toFixed(2)}</td>
              <td className="px-4 py-2">{stock.latest_close?.toFixed(2)}</td>
              
              <td className={`px-4 py2 ${stock.gain_loss>0? 
                "text-green-500 font-medium": stock.gain_loss<0? 
                "text-red-600 font-medium":"text-gray-500"}`}>
                                    <span>{stock.gain_loss > 0 ? " ▲ ": stock.gain_loss < 0? " ▼ ": " — "}</span>{stock.gain_loss?.toFixed(2)}</td>
              <td className={`px-4 py2 ${stock.gain_loss>0? 
                "text-green-500 font-medium": stock.gain_loss<0? 
                "text-red-600 font-medium":"text-gray-500"}`}>    
                <span>{stock.gain_loss > 0 ? " ▲ ": stock.gain_loss < 0? " ▼ ": " — "}
                </span>{stock.gain_loss_pct?.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </>
);

}