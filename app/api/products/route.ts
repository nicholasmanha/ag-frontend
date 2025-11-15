import { NextResponse } from "next/server";
import products from "@/app/data/sample/products.json"; // adjust path as needed

// Handle GET requests (return all products)
export async function GET() {
  return NextResponse.json(products);
}

// Optional: Handle POST (e.g., filter, simulate accept)
export async function POST(req: { json: () => any; }) {
  const body = await req.json();
  const filtered = products.filter(p =>
    p.title.toLowerCase().includes(body.query?.toLowerCase() || "")
  );
  return NextResponse.json(filtered);
}
