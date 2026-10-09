"use client";
import { useEffect, useRef, useState, useId } from "react";
import { BalancePoint } from "@/lib/simulation";
export function InventoryChart({base,stress,unit}:{base:BalancePoint[];stress:BalancePoint[];unit:string}) {
  const ref=useRef<HTMLDivElement>(null);const [width,setWidth]=useState(600);const [day,setDay]=useState<number|null>(null);const id=useId().replace(/:/g,"");
  useEffect(()=>{const element=ref.current;if(!element)return;const observer=new ResizeObserver(([entry])=>setWidth(entry.contentRect.width));observer.observe(element);return()=>observer.disconnect();},[]);
  const height=250,left=52,right=12,top=24,bottom=34,w=Math.max(100,width-left-right),h=height-top-bottom;
  const values=[...base,...stress].map(p=>p.balance),min=Math.min(0,...values),max=Math.max(1,...values),padding=(max-min)*.08,lo=min-padding,hi=max+padding;
  const x=(d:number)=>left+d/30*w,y=(v:number)=>top+(hi-v)/(hi-lo)*h;
  const path=(points:BalancePoint[])=>points.map((p,i)=>`${i?"L":"M"}${x(p.day)},${y(p.balance)}`).join(" ");
  const ticks=width<400?[0,10,20,30]:[0,5,10,15,20,25,30];
  const active=day===null?null:{base:base.find(p=>p.day===day),stress:stress.find(p=>p.day===day)};
  return <><div ref={ref} className="chart-shell"><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`30-day inventory simulation in ${unit}; scheduled and delayed receipts. Negative balances indicate unmet demand.`}>
    <defs><clipPath id={id}><rect x={left} y={top} width={w} height={h}/></clipPath></defs>
    {[0,1,2,3].map(i=>{const value=lo+(hi-lo)*i/3;return <g key={i}><line x1={left} x2={width-right} y1={y(value)} y2={y(value)} stroke="#e9eddf"/><text x={left-10} y={y(value)+4} textAnchor="end">{Math.round(value).toLocaleString()}</text></g>;})}
    <text x={left} y={12}>{unit}</text><line x1={left} x2={width-right} y1={y(0)} y2={y(0)} stroke="#d6b18b" strokeDasharray="4 4"/>
    {ticks.map(d=><text key={d} x={x(d)} y={height-10} textAnchor={d===0?"start":d===30?"end":"middle"}>{d===0?"Today":`Day ${d}`}</text>)}
    <g clipPath={`url(#${id})`}><path d={path(base)} fill="none" stroke="#a9ba91" strokeWidth={2} strokeDasharray="5 4"/><path d={path(stress)} fill="none" stroke="#718959" strokeWidth={2.5}/>{day!==null&&<><line x1={x(day)} x2={x(day)} y1={top} y2={height-bottom} stroke="#d5dfc7"/>{active?.stress&&<circle cx={x(day)} cy={y(active.stress.balance)} r={4} fill="#718959"/>}{active?.base&&<circle cx={x(day)} cy={y(active.base.balance)} r={3} fill="#a9ba91"/>}</>}</g>
    <rect x={left} y={top} width={w} height={h} fill="transparent" onPointerMove={e=>{const bounds=e.currentTarget.ownerSVGElement!.getBoundingClientRect();setDay(Math.max(0,Math.min(30,Math.round(((e.clientX-bounds.left)*width/bounds.width-left)/w*30))));}} onPointerLeave={()=>setDay(null)} onPointerDown={e=>{const bounds=e.currentTarget.ownerSVGElement!.getBoundingClientRect();setDay(Math.max(0,Math.min(30,Math.round(((e.clientX-bounds.left)*width/bounds.width-left)/w*30))));}}/>
  </svg></div><div className="chart-tooltip">{day!==null?`Day ${day}: scheduled ${active?.base?.balance.toLocaleString()} ${unit} · delayed ${active?.stress?.balance.toLocaleString()} ${unit}`:"Negative balance = unmet demand. One scheduled receipt; constant daily consumption."}</div></>;
}

