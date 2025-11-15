import { NextResponse } from "next/server";

let agentParams = {
  version: 1,
  weight_trend: 0.6,
  weight_margin: 0.4
};

export async function POST() {
  // simple evolve logic
  agentParams.version += 1;
  agentParams.weight_trend = Math.min(1, agentParams.weight_trend + 0.05);
  agentParams.weight_margin = Math.max(0, agentParams.weight_margin - 0.05);

  console.log(`[Agent] Strategy evolved to version ${agentParams.version}`);

  return NextResponse.json({
    message: "Strategy updated",
    new_params: agentParams
  });
}

// optional GET if you want to check current params
export async function GET() {
  return NextResponse.json(agentParams);
}
