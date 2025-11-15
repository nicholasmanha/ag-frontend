// app/api/message/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const name = searchParams.get('name') || 'Guest';
  
  return NextResponse.json({
    message: `Hello, ${name}!`,
    timestamp: new Date().toISOString(),
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, email } = body;
    
    // Simulate some processing
    const response = {
      success: true,
      message: `Received data for ${name}`,
      data: {
        name,
        email,
        id: Math.random().toString(36).substr(2, 9),
      },
    };
    
    return NextResponse.json(response);
  } catch (error) {
    return NextResponse.json(
      { success: false, message: 'Invalid request' },
      { status: 400 }
    );
  }
}