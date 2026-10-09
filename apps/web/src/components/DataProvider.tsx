"use client";
import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { API_CLIENT, MODE_A_SUPPLIERS, MODE_A_MATERIALS, MODE_A_ALERTS, SupplierSummary, MaterialExposure, AlertItem } from "@/lib/api";
type WorkspaceData = {suppliers:SupplierSummary[];materials:MaterialExposure[];alerts:AlertItem[];refresh:()=>Promise<void>;updateAlert:(id:string,status:AlertItem["status"])=>Promise<void>};
const Context=createContext<WorkspaceData|null>(null);
export function DataProvider({children}:{children:React.ReactNode}) {
  const [suppliers,setSuppliers]=useState(MODE_A_SUPPLIERS);const [materials,setMaterials]=useState(MODE_A_MATERIALS);const [alerts,setAlerts]=useState(MODE_A_ALERTS);
  const refresh=useCallback(async()=>{const [s,m,a]=await Promise.all([API_CLIENT.getSuppliers(),API_CLIENT.getMaterials(),API_CLIENT.getAlerts()]);setSuppliers(s);setMaterials(m);setAlerts(a);},[]);
  useEffect(()=>{void refresh();},[refresh]);
  async function updateAlert(id:string,status:AlertItem["status"]) {const updated=await API_CLIENT.updateAlert(id,status);setAlerts(previous=>previous.map(a=>a.id===id?updated:a));}
  return <Context.Provider value={{suppliers,materials,alerts,refresh,updateAlert}}>{children}</Context.Provider>;
}
export function useData() {const data=useContext(Context);if(!data)throw new Error("Workspace data is unavailable");return data;}
