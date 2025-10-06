import request from "supertest";
import {
  describe,
  it,
  expect,
  vi,
  beforeEach,
  afterEach,
  beforeAll,
} from "vitest";

const listResourcesMock = vi.fn();
const rankSpy = vi.fn();
const createEmbeddingProviderMock = vi.fn(() => ({
  name: "identity",
  embed: vi.fn(async () => []),
}));

class FakeHybridRanker {
  async rank(query: string, resources: any[], options: any) {
    return rankSpy(query, resources, options);
  }
}

class FakeIdentityProvider {
  name = "identity";
  async embed(): Promise<number[][]> {
    return [];
  }
}

vi.mock("@ardf/database", () => ({
  db: {
    listResources: listResourcesMock,
    listSources: vi.fn(() => []),
    upsertResource: vi.fn(),
    recordSourceSync: vi.fn(),
  },
}));

vi.mock("@ardf/search", () => ({
  createEmbeddingProvider: createEmbeddingProviderMock,
  IdentityEmbeddingProvider: FakeIdentityProvider,
  HybridRanker: FakeHybridRanker,
}));

let app: any;

beforeAll(async () => {
  ({ app } = await import("../src/main"));
});

beforeEach(() => {
  process.env.ARDF_EMBEDDING_PROVIDER = "identity";
  listResourcesMock.mockReset();
  rankSpy.mockReset();
  createEmbeddingProviderMock.mockClear();
});

afterEach(() => {
  delete process.env.ARDF_EMBEDDING_PROVIDER;
});

describe("POST /api/recommend", () => {
  it("returns 400 when query is missing", async () => {
    const response = await request(app).post("/api/recommend").send({});
    expect(response.status).toBe(400);
    expect(response.body).toEqual({ message: "query is required" });
  });

  it("returns ranked results when query is provided", async () => {
    const resources = [
      { resourceId: "tool_a", description: "Flight booking assistant", resourceType: "tool" },
      { resourceId: "doc_a", description: "Documentation", resourceType: "document" },
    ];
    listResourcesMock.mockReturnValue({ resources, total: resources.length });
    rankSpy.mockResolvedValue([
      { item: resources[0], score: 0.9, lexical: 2, semantic: 0.7 },
      { item: resources[1], score: 0.2, lexical: 0.5, semantic: 0.1 },
    ]);

    const response = await request(app)
      .post("/api/recommend")
      .send({ query: "book a flight", limit: 2 });

    expect(response.status).toBe(200);
    expect(listResourcesMock).toHaveBeenCalledWith({ type: undefined, query: undefined, limit: 200 });
    expect(rankSpy).toHaveBeenCalledWith("book a flight", resources, { limit: 2 });
    expect(response.body).toEqual({
      totalCandidates: resources.length,
      recommended: [
        {
          resource: resources[0],
          score: 0.9,
          lexical: 2,
          semantic: 0.7,
        },
        {
          resource: resources[1],
          score: 0.2,
          lexical: 0.5,
          semantic: 0.1,
        },
      ],
    });
  });
});
