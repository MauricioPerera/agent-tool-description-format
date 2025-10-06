import { describe, it, expect, vi } from "vitest";

const loadDatabase = async () => {
  process.env.DATABASE_URL = ':memory:';
  vi.resetModules();
  const module = await import("../src/index");
  return module.db;
};

describe("database layer", () => {
  it("persists resources and filters by type", async () => {
    const db = await loadDatabase();

    const resource = {
      resourceId: "tool_reserve_flight",
      resourceType: "tool",
      description: "Book a flight with fare validation",
      whenToUse: "Use for airline reservations",
      metadata: { version: "1.2.3", tags: ["travel", "booking"], domain: "travel" },
      content: { endpoint: "https://api.flights" },
      tags: ["travel", "booking"],
      status: "published",
      version: "1.2.3",
    };

    const stored = db.upsertResource(resource);
    expect(stored.resourceId).toBe(resource.resourceId);
    expect(stored.tags).toEqual(["travel", "booking"]);

    const listing = db.listResources({ type: "tool", query: null, limit: 25 });
    expect(listing.total).toBe(1);
    expect(listing.resources[0].resourceType).toBe("tool");
    expect(listing.resources[0].metadata?.version).toBe("1.2.3");
  });

  it("records MCP sources and updates existing entries", async () => {
    const db = await loadDatabase();

    db.recordSourceSync("source-a", "https://mcp.server", "Primary");
    let sources = db.listSources();
    expect(sources).toHaveLength(1);
    expect(sources[0]).toMatchObject({ id: "source-a", baseUrl: "https://mcp.server", label: "Primary" });
    expect(sources[0].lastSyncAt).toBeTruthy();

    db.recordSourceSync("source-a", "https://mcp.server/v2");
    sources = db.listSources();
    expect(sources).toHaveLength(1);
    expect(sources[0].baseUrl).toBe("https://mcp.server/v2");
    expect(sources[0].label).toBe("https://mcp.server/v2");
  });
});