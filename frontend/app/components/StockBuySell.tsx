import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useUser } from "../contexts/userContext";

type StockBuySellProp = {
  user: string;
  ticker: string;
};

type StockBuyRequest = {
  ticker: string;
  amount: number;
  stockname: string;
};

type StockSellRequest = {
  ticker: string;
  share: number;
  stockname: string;
};

export default function StockBuySell({ ticker }: StockBuySellProp) {
  const [value, setValue] = useState<number | "">("");
  const { user, setUser } = useUser();
  const [shares, setShares] = useState(0);
  const [message, setMessage] = useState("");
  const router = useRouter();

  // Fetch shares
  useEffect(() => {
    async function loadData() {
      const resp = await fetch(
        `http://localhost:8000/user-owned-stocks/get-stock?ticker=${ticker}`,
        {
          credentials: "include",
          headers: { "Content-Type": "application/json" },
        }
      );

      if (resp.ok) {
        const data = await resp.json();
        if (data.stock?.shares > 0) {
          setShares(Number(data.stock.shares));
        }
      }
    }

    loadData();
  }, [ticker]);

  async function handleSubmit(action: string) {
    setMessage("");

    if (value === "") return;

    if (action === "buy") {
      const body: StockBuyRequest = {
        ticker,
        stockname: ticker,
        amount: value,
      };

      const resp = await fetch(`http://localhost:8000/user-owned-stocks/buy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(body),
      });

      if (resp.ok) {
        console.log("after buying");
        const data = await resp.json();

        if (user) {
          setUser({ ...user, total_capital: user.total_capital - value });
        }
        console.log("data", data);
        setShares(Number(data.shares));
        setMessage("Stock bought successfully!");
        setValue("");
      } else if (resp.status === 401) {
        router.push("/login");
      } else {
        setMessage("Something went wrong...");
      }
    }

    if (action === "sell") {
      const body: StockSellRequest = {
        ticker,
        stockname: ticker,
        share: value,
      };

      const resp = await fetch(`http://localhost:8000/user-owned-stocks/sell`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(body),
      });

      if (resp.ok) {
        const data = await resp.json();
        setUser(data.user);
        setShares((prev) => prev - value);
        setMessage("Stock sold successfully!");
        setValue("");
      } else if (resp.status === 401) {
        router.push("/login");
      } else {
        setMessage("Something went wrong...");
      }
    }
  }

  if (!user) return null;

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-xl border border-gray-200 mt-6">
      <h1 className="text-xl font-bold text-gray-900 mb-4">Trade {ticker}</h1>

      <div className="space-y-3 mb-4">
        <p className="text-sm text-gray-700">
          Capital available:{" "}
          <span className="font-semibold">
            ${user.total_capital.toFixed(2)}
          </span>
        </p>
        <p className="text-sm text-gray-700">
          Owned shares:{" "}
          <span className="font-semibold">{shares.toFixed(2)}</span>
        </p>
      </div>

      {/* Input */}
      <div className="mb-4">
        <input
          type="number"
          step="0.01"
          placeholder="Enter value"
          value={value}
          onChange={(e) => {
            const v = e.target.value;
            if (v === "") {
              setValue("");
              return;
            }
            setValue(Number(v));
          }}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />

        <p className="text-xs text-gray-500 mt-1">
          Buy = amount in dollars, Sell = number of shares
        </p>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => handleSubmit("buy")}
          className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          disabled={value === "" || value <= 0 || value > user.total_capital}
        >
          Buy
        </button>

        <button
          onClick={() => handleSubmit("sell")}
          className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          disabled={value === "" || value <= 0 || value > shares}
        >
          Sell
        </button>
      </div>

      {message && (
        <p className="text-gray-700 text-sm mt-3 text-center">{message}</p>
      )}
    </div>
  );
}
