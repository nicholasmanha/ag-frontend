import { NextResponse } from "next/server";

// quick static list; you can replace these later with DB data
const metrics = [
  { campaign_id: "c_1", cost: 20.0, revenue: 50.0, profit: 30.0 },
  { campaign_id: "c_2", cost: 15.0, revenue: 40.0, profit: 25.0 },
  { campaign_id: "c_3", cost: 10.0, revenue: 25.0, profit: 15.0 }
];

export async function GET() {
  return NextResponse.json(metrics);
}
