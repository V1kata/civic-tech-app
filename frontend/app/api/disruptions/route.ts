import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

interface Disruption {
  id: string;
  street: string;
  disruption_type: string;
  start_date: string;
  end_date: string;
  latitude: number;
  longitude: number;
  scraped_at: string;
}

interface DisruptionResponse {
  timestamp: string;
  count: number;
  disruptions: Disruption[];
}

/**
 * GET /api/disruptions
 * 
 * Returns current disruption data from the backend JSON file.
 * 
 * Query Parameters:
 *   - type: Filter by disruption type (optional)
 *   - limit: Limit results to N items (optional, default: 100)
 * 
 * Response:
 *   {
 *     "timestamp": "2024-05-15T10:00:00",
 *     "count": 3,
 *     "disruptions": [...]
 *   }
 */
export async function GET(request: NextRequest) {
  try {
    // Get query parameters
    const searchParams = request.nextUrl.searchParams;
    const typeFilter = searchParams.get("type");
    const limitParam = searchParams.get("limit");
    const limit = limitParam ? parseInt(limitParam, 10) : 100;

    // Path to the disruptions JSON file from the backend
    // In production, this might be a Supabase query instead
    const dataPath = path.join(
      process.cwd(),
      "..",
      "backend",
      "data",
      "disruptions.json"
    );

    // Check if file exists
    if (!fs.existsSync(dataPath)) {
      // Return empty response if file doesn't exist
      return NextResponse.json(
        {
          timestamp: new Date().toISOString(),
          count: 0,
          disruptions: [],
        },
        { status: 200 }
      );
    }

    // Read the JSON file
    const fileContent = fs.readFileSync(dataPath, "utf-8");
    let data: DisruptionResponse = JSON.parse(fileContent);

    // Filter by type if provided
    if (typeFilter) {
      data.disruptions = data.disruptions.filter(
        (d) => d.disruption_type.toLowerCase() === typeFilter.toLowerCase()
      );
      data.count = data.disruptions.length;
    }

    // Apply limit
    if (data.disruptions.length > limit) {
      data.disruptions = data.disruptions.slice(0, limit);
    }

    // Add cache headers
    const response = NextResponse.json(data, { status: 200 });
    response.headers.set("Cache-Control", "public, max-age=300, s-maxage=300"); // 5 minutes
    return response;
  } catch (error) {
    console.error("Error in GET /api/disruptions:", error);
    return NextResponse.json(
      {
        error: "Failed to fetch disruptions",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

/**
 * POST /api/disruptions
 * 
 * Used by the Python scraper to upload new disruption data.
 * In production, implement proper authentication here.
 * 
 * Request Body:
 *   {
 *     "disruptions": [...]
 *   }
 */
export async function POST(request: NextRequest) {
  try {
    // TODO: Add authentication check here
    // For now, this is open - secure it before production!

    const body = await request.json();

    if (!body.disruptions || !Array.isArray(body.disruptions)) {
      return NextResponse.json(
        { error: "Invalid request body. Expected: { disruptions: [...] }" },
        { status: 400 }
      );
    }

    const dataPath = path.join(
      process.cwd(),
      "..",
      "backend",
      "data",
      "disruptions.json"
    );

    // Ensure directory exists
    const directory = path.dirname(dataPath);
    if (!fs.existsSync(directory)) {
      fs.mkdirSync(directory, { recursive: true });
    }

    // Write data to file
    const responseData: DisruptionResponse = {
      timestamp: new Date().toISOString(),
      count: body.disruptions.length,
      disruptions: body.disruptions,
    };

    fs.writeFileSync(dataPath, JSON.stringify(responseData, null, 2));

    return NextResponse.json(
      {
        success: true,
        message: `Updated ${body.disruptions.length} disruptions`,
        timestamp: responseData.timestamp,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Error in POST /api/disruptions:", error);
    return NextResponse.json(
      {
        error: "Failed to update disruptions",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
