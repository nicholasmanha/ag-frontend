import { NextResponse } from "next/server";
import products from "@/app/data/sample/products.json";

// We’ll keep a temporary list of launched campaigns in memory
let campaigns: any[] = [];

export async function POST(req: { json: () => any; }) {
  try {
    const body = await req.json();
    const { product_id } = body;

    // Find the product
    const product = products.find(p => p.id === product_id);
    if (!product) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 });
    }

    // Simulate launching a campaign
    const campaign = {
      id: `c_${Date.now()}`,
      product_id,
      status: "launched",
      creative_url: `https://cdn.example.com/creatives/${product_id}.jpg`,
      profit: Math.round(product.price * product.margin * 100) / 100,
      timestamp: new Date().toISOString()
    };

    // Store campaign in memory
    campaigns.push(campaign);

    return NextResponse.json({
      message: "Campaign launched successfully",
      campaign
    });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}

// Optional: expose campaigns for GET requests
export async function GET() {
  return NextResponse.json(campaigns);
}
