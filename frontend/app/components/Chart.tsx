"use client";
import { useEffect } from 'react';
import { CartesianGrid, Line, LineChart, Tooltip, XAxis, YAxis  } from 'recharts';
import { useState } from 'react';

type Portfolio = {
    date: string;
    portfolio_value:number;
};



export default function ChartComponent(){
    const [portfolio, setPortfolio]=useState<Portfolio[]>()
    useEffect(()=>{
        async function loadData(){
            const token=localStorage.getItem("token")
            const res=await fetch("http://localhost:8000/user-owned-stocks/get-portfolio",
                {
                    headers:{Authorization:`Bearer ${token}`}
                }
            )
            const data=await res.json()
            setPortfolio(data)
        }
        loadData();
    },[])
  return (
    <LineChart
      style={{ width: '100%', aspectRatio: 1.618, maxWidth: 600 }}
      responsive
      data={portfolio}
      margin={{
        top: 20,
        right: 20,
        bottom: 5,
        left: 0,
      }}
    >
      <CartesianGrid stroke="#aaa" strokeDasharray="5 5" />
      <Line type="monotone" dataKey="portfolio_value" stroke="#90EE90" strokeWidth={2} name="Portfolio Value" dot={false} />
      <XAxis dataKey="date" tick={false} />
      <YAxis width="auto" label={{ value: 'Portfolio Worth', position: 'insideLeft', angle: -90 }} />
      <Tooltip labelFormatter={(label) => new Date(label).toLocaleDateString()} formatter={(value: number) => `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}  />
    </LineChart>
  );
}