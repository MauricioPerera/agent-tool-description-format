import request from "supertest";
import {
  describe,
  it,
  expect,
  vi,
  beforeAll,
  beforeEach,
  afterEach,
} from "vitest";

const upsertResourceMock = vi.fn();
const recordSourceSyncMock = vi.fn();
const listResourcesMock = vi.fn(() => ({ resources: [], total: 0 }));
const listSourcesMock = vi.fn(() => []);

vi.mock("@ardf/database", () => ({
  db: {
    upsertResource: upsertResourceMock,
    recordSourceSync: recordSourceSyncMock,
    listResources: listResourcesMock,
    listSources: listSourcesMock,
  },
}));

const syncCatalogMock = vi.fn();

class FakeMcpManager {
  source;
  constructor(config: { id: string; baseUrl: string; label?: string }) {
    this.source = {
      id: config.id,
      baseUrl: config.baseUrl,
      label: config.label ?? config.baseUrl,
    };
  }

  async syncCatalog() {
    return syncCatalogMock();
  }
}

vi.mock("@ardf/mcp", () => ({ McpManager: FakeMcpManager }));

let app: any;

beforeAll(async () => {
  ({ app } = await import("../src/main"));
});

beforeEach(() => {
  process.env.ARDF_EMBEDDING_PROVIDER = "identity";
  upsertResourceMock.mockReset();
  recordSourceSyncMock.mockReset();
  listResourcesMock.mockReset();
  listSourcesMock.mockReset();
  syncCatalogMock.mockReset();
});

afterEach(() => {
  delete process.env.ARDF_EMBEDDING_PROVIDER;
});

describe("POST /api/mcp/sync", () => {
  it("returns 400 when baseUrl is missing", async () => {
    const response = await request(app).post("/api/mcp/sync").send({});

    expect(response.status).toBe(400);
    expect(response.body).toEqual({ message: "baseUrl is required" });
    expect(syncCatalogMock).not.toHaveBeenCalled();
  });

  it("syncs catalog resources and persists them", async () => {
    const first = {
      resource_id: "tool_alpha",
      resource_type: "tool",
      description: "Alpha tool",
      when_to_use: "When alpha is needed",
      metadata: { tags: ["alpha"], version: "1.0.0" },
      status: "published",
    };
    const second = {
      resource_id: "policy_beta",
      resource_type: "policy",
      description: "Beta policy",
      metadata: { domain: "compliance" },
    };

    syncCatalogMock.mockResolvedValue({ resources: [first, second] });

    const response = await request(app)
      .post("/api/mcp/sync")
      .send({ baseUrl: "https://mcp.local", label: "Local" });

    expect(response.status).toBe(200);
    expect(response.body).toEqual({ status: "ok", synced: { resources: 2 } });
    expect(upsertResourceMock).toHaveBeenCalledTimes(2);
    expect(upsertResourceMock).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        resourceId: "tool_alpha",
        resourceType: "tool",
        description: "Alpha tool",
        whenToUse: "When alpha is needed",
        status: "published",
        tags: ["alpha"],
        version: "1.0.0",
      }),
    );
    expect(upsertResourceMock).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        resourceId: "policy_beta",
        resourceType: "policy",
        description: "Beta policy",
        domain: "compliance",
      }),
    );
    expect(recordSourceSyncMock).toHaveBeenCalledWith("https://mcp.local", "https://mcp.local", "Local");
  });

  it("returns 500 when synchronization fails", async () => {
    syncCatalogMock.mockRejectedValue(new Error("boom"));

    const response = await request(app)
      .post("/api/mcp/sync")
      .send({ baseUrl: "https://broken" });

    expect(response.status).toBe(500);
    expect(response.body.message).toBe("sync failed");
  });
});