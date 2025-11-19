"use client";

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

// for now i wont use it
// type StockWithPrice=UserStock &{
//     current_price:string;
//     marketValue:string;
// }

type OwnedStockRequestProp = {
  stocks: UserStock[];
  error: string;
  portfolioValue: number;
  investmentAmount: number;
};

export default function OwnedStocksTable({
  stocks,
  error,
  portfolioValue,
  investmentAmount,
}: OwnedStockRequestProp) {
  // const [stocks,setStocks]=useState<UserStock[]>([]);
  // const [error,setError]=useState("")
  // const [portfolioValue, setPortfolioValue]=useState(0)
  // const [investmentAmount, setInvestmentAmount]=useState(0)
  // useEffect(()=>{
  //     async function loadData(){
  //         try{
  //             const token=localStorage.getItem("token")
  //             const res=await fetch("http://localhost:8000/user-owned-stocks/get-stocks",{
  //                 method:"GET",
  //                 headers:{
  //                     Authorization:`Bearer ${token}`
  //                 }
  //             })
  //             if (!res.ok){
  //                 setError("Something went wrong!")
  //                 return;
  //             }
  //             const data=await res.json()
  //             setStocks(data.stocks)
  //         }catch{
  //             setError("Something went wrong")
  //         }
  //     }
  //     loadData();

  // },[])

  // useEffect(() => {
  //   const totalInvestment = stocks.reduce(
  //     (acc, stock) => acc + stock.avg_buy_price * Number(stock.shares),
  //     0
  //   );
  //   setInvestmentAmount(totalInvestment);

  //   const totalPortfolio = stocks.reduce(
  //     (acc, stock) => acc + stock.latest_close * Number(stock.shares),
  //     0
  //   );
  //   setPortfolioValue(totalPortfolio);
  // }, [stocks]);

  if (stocks.length === 0) {
    return (
      <p>
        No currently owned stocks! Search for a stock and buy one to see
        portfolio
      </p>
    );
  }

  return (
    <>
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="flex-1 p-4 bg-white rounded-xl border border-blue-100">
          <h3 className="text-gray-600 text-sm mb-1">Invested</h3>
          <p className="text-xl font-bold text-gray-900">
            ${investmentAmount.toFixed(2)}
          </p>
        </div>

        <div className="flex-1 p-4 bg-white rounded-xl border border-blue-100">
          <h3 className="text-gray-600 text-sm mb-1">Current Value</h3>
          <p className="text-xl font-bold text-gray-900">
            ${portfolioValue.toFixed(2)}
          </p>
        </div>
      </div>

      {error && <p className="text-red-500 mb-4 text-sm">{error}</p>}

      <div className="overflow-x-auto bg-white rounded-xl border border-blue-100">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-blue-50 text-left">
              {[
                "Stock",
                "Shares",
                "Last Transaction",
                "Avg Buy Price",
                "Latest Close",
                "Gain/Loss",
                "Gain/Loss %",
              ].map((col) => (
                <th key={col} className="px-4 py-3 font-semibold text-gray-700">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {stocks.map((stock) => (
              <tr
                key={stock.id}
                className="border-b border-gray-100 hover:bg-gray-50"
              >
                <td className="px-4 py-3 font-medium text-gray-900">
                  {stock.stock}
                </td>
                <td className="px-4 py-3 text-gray-700">
                  {stock.shares?.toFixed(2) ?? 0}
                </td>
                <td className="px-4 py-3 text-gray-600 text-xs">
                  {stock.date}
                </td>
                <td className="px-4 py-3 text-gray-700">
                  ${stock.avg_buy_price?.toFixed(2) ?? 0}
                </td>
                <td className="px-4 py-3 text-gray-700">
                  ${stock.latest_close?.toFixed(2) ?? 0}
                </td>

                <td className="px-4 py-3">
                  <span
                    className={`font-medium ${
                      stock.gain_loss > 0
                        ? "text-green-600"
                        : stock.gain_loss < 0
                        ? "text-red-600"
                        : "text-gray-600"
                    }`}
                  >
                    {stock.gain_loss > 0
                      ? `+${stock.gain_loss.toFixed(2)}`
                      : stock.gain_loss.toFixed(2)}
                  </span>
                </td>

                <td className="px-4 py-3">
                  <span
                    className={`font-medium ${
                      stock.gain_loss_pct > 0
                        ? "text-green-600"
                        : stock.gain_loss_pct < 0
                        ? "text-red-600"
                        : "text-gray-600"
                    }`}
                  >
                    {stock.gain_loss_pct > 0
                      ? `+${stock.gain_loss_pct.toFixed(2)}%`
                      : `${stock.gain_loss_pct.toFixed(2)}%`}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
