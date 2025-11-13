"use client";

import { CartesianGrid, Line, LineChart, Tooltip, XAxis, YAxis  } from 'recharts';


type ChartProps<T>={
  data:T[],
  xKey: keyof T;
  yKey?: keyof T;
  title?:string;
  color?:string;
  yLabel?:string;
}

export default function ChartComponent<T extends object>({
  data,
  xKey,
  yKey,
  color = "#4CAF50",
  yLabel = "Value",

}:ChartProps<T>){
    if (!data || data.length==0) return <p>No data available</p>
    const lineColor = (() => {
  if (!data || data.length === 0 || !yKey) return color; // fallback
  const first = data[0][yKey] as unknown as number;
  const last = data[data.length - 1][yKey] as unknown as number;
  return last >= first ? "#90EE90" : "red";
})();
  return (
    <div className='w-full flex justify-center'>
          <LineChart
      style={{ width: '100%', aspectRatio: 1.618, maxWidth: 600 }}
      responsive
      data={data}
      margin={{
        top: 20,
        right: 20,
        bottom: 5,
        left: 0,
      }}
    >
      <CartesianGrid stroke="#aaa" strokeDasharray="5 5" />
      <Line type="monotone" dataKey={yKey as string} stroke={lineColor} strokeWidth={2} name="Portfolio Value" dot={false} />
      <XAxis dataKey={xKey as string} tick={false} />
      <YAxis width="auto" label={{ value: yLabel as string, position: 'insideLeft', angle: -90 }} />
      <Tooltip labelFormatter={(label) => new Date(label).toLocaleDateString()} formatter={(value: number) => `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}  />
    </LineChart>
    </div>

  );
}