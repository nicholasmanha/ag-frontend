// app/api/linkup/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { LinkupClient } from 'linkup-sdk';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, depth = 'standard', outputType = 'searchResults' } = body;
    
    console.log('Received request:', { query, depth, outputType });
    
    if (!query) {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      );
    }

    const apiKey = process.env.LINKUP_API_KEY;
    
    if (!apiKey) {
      console.error('API key not found in environment');
      return NextResponse.json(
        { error: 'LINKUP_API_KEY not configured' },
        { status: 500 }
      );
    }

    console.log('Initializing Linkup client...');
    
    // Initialize Linkup client
    const client = new LinkupClient({ apiKey });

    console.log('Calling Linkup search...');
    
    // Call Linkup search
    const response = await client.search({
      query,
      depth,
      outputType,
    });

    console.log('Linkup response received:', response);

    return NextResponse.json({
      success: true,
      data: response,
    });
    
  } catch (error: any) {
    console.error('Linkup API error:', error);
    console.error('Error details:', error.message, error.stack);
    return NextResponse.json(
      { 
        error: 'Failed to fetch from Linkup API', 
        details: error.message || String(error) 
      },
      { status: 500 }
    );
  }
}