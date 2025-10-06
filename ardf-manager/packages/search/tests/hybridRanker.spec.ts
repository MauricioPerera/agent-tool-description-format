import { describe, it, expect, vi, afterEach } from 'vitest';
import type { EmbeddingProvider } from '../src';
import {
  HybridRanker,
  IdentityEmbeddingProvider,
  createEmbeddingProvider,
} from '../src';

class MockEmbeddingProvider implements EmbeddingProvider {
  name = 'mock';

  constructor(private readonly embeddings: number[][], private readonly shouldFail = false) {}

  async embed(texts: string[]): Promise<number[][]> {
    if (this.shouldFail) {
      throw new Error('embedding failed');
    }

    if (this.embeddings.length < texts.length) {
      throw new Error('insufficient embeddings configured for test');
    }

    return this.embeddings.slice(0, texts.length);
  }
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe('HybridRanker', () => {
  it('combines lexical and semantic scores when embeddings are available', async () => {
    const provider = new MockEmbeddingProvider([
      [1, 0], // query
      [1, 0], // candidate 1 (high semantic alignment)
      [0, 1], // candidate 2 (low semantic alignment)
    ]);
    const ranker = new HybridRanker(provider);

    const candidates = [
      { description: 'Book a flight with flexible fares' },
      { description: 'Order a pizza from local restaurants' },
    ];

    const result = await ranker.rank('Help me book a flight', candidates, { limit: 2 });

    expect(result).toHaveLength(2);
    expect(result[0].item.description).toContain('flight');
    expect(result[0].semantic ?? 0).toBeGreaterThan(result[1].semantic ?? 0);
  });

  it('falls back to lexical ranking when embeddings fail', async () => {
    const provider = new MockEmbeddingProvider([], true);
    const ranker = new HybridRanker(provider);

    const candidates = [
      { description: 'Find the cheapest flight to Madrid' },
      { description: 'Suggest hotel recommendations' },
    ];

    const result = await ranker.rank('flight flight booking', candidates, { limit: 2 });

    expect(result[0].item.description).toContain('flight');
    expect(result[0].lexical ?? 0).toBeGreaterThan(result[1].lexical ?? 0);
  });
});

describe('createEmbeddingProvider', () => {
  it('returns identity provider by default', () => {
    const provider = createEmbeddingProvider();
    expect(provider).toBeInstanceOf(IdentityEmbeddingProvider);
  });

  it('initialises an OpenAI-compatible provider with custom fetch', async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({ data: [[0.1, 0.2], [0.3, 0.4]] }),
    })) as unknown as typeof fetch;

    const provider = createEmbeddingProvider({
      provider: 'openai',
      apiUrl: 'https://mock.openai.local/v1',
      apiKey: 'secret',
      model: 'custom-embedding',
      fetchImpl: fetchMock as unknown as typeof fetch,
    });

    const vectors = await provider.embed(['first', 'second']);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('https://mock.openai.local/v1/embeddings');
    expect(init?.method).toBe('POST');
    expect(init?.headers).toMatchObject({
      Authorization: 'Bearer secret',
      'Content-Type': 'application/json',
    });
    expect(JSON.parse(String(init?.body))).toEqual({ model: 'custom-embedding', input: ['first', 'second'] });
    expect(vectors).toEqual([
      [0.1, 0.2],
      [0.3, 0.4],
    ]);
  });
});


