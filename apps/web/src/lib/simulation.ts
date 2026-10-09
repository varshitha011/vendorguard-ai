import { MaterialExposure } from "./api";
export interface BalancePoint {day:number;balance:number}
// Recover scheduled receipt quantities from the supplied base trajectory.
// Negative balances represent unmet demand carried forward, not physical stock.
export function simulateMaterial(material:MaterialExposure,delay:number) {
  let previous=material.available_stock;
  const receipts=new Map<number,number>();
  for(const point of material.trajectory_base) {
    // Some source trajectories clamp depleted inventory to zero. Do not
    // interpret that floor as a daily replenishment after stock is exhausted.
    const receipt=point.balance===0&&previous===0?0:Math.max(0,point.balance-previous+material.daily_consumption);
    if(receipt>0)receipts.set(point.day,receipt);
    previous=point.balance;
  }
  function trajectory(extra:number):BalancePoint[] {
    let balance=material.available_stock;
    const points:BalancePoint[]=[{day:0,balance}];
    for(let day=1;day<=30;day++) {balance+=(receipts.get(day-extra)||0)-material.daily_consumption;points.push({day,balance});}
    return points;
  }
  const base=trajectory(0),stress=trajectory(delay);
  const firstReceipt=Array.from(receipts.keys())[0]??null;
  const stockout=stress.find(p=>p.balance<0)?.day??null;
  const arrival=firstReceipt===null?null:firstReceipt+delay;
  const gap=arrival===null?null:Math.max(0,arrival-material.coverage_days);
  return {base,stress,stockout,arrival,gap,firstReceipt};
}
