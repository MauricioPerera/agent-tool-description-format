export interface EmbeddingProvider {
  embed(texts: string[]): Promise<number[][]>;
  name: string;
}

export interface HybridRankingOptions {
  limit?: number;
  alpha?: number;
}

export interface RankedCandidate<T> {
  item: T;
  score: number;
  lexical?: number;
  semantic?: number;
}

export interface OpenAICompatibleEmbeddingConfig {
  apiUrl?: string;
  apiKey?: string;
  model?: string;
  organization?: string;
  additionalHeaders?: Record<string, string>;
  fetchImpl?: typeof fetch;
}

export interface EmbeddingProviderFactoryConfig extends OpenAICompatibleEmbeddingConfig {
  provider?: string | null;
  fallbackToIdentity?: boolean;
}

const DEFAULT_OPENAI_BASE_URL = 'https://api.openai.com/v1';
const DEFAULT_OPENAI_MODEL = 'text-embedding-3-small';

export class HybridRanker<T extends { description?: string }> {
  constructor(private readonly embedder: EmbeddingProvider) {}

  async rank(query: string, candidates: T[], options: HybridRankingOptions = {}): Promise<RankedCandidate<T>[]> {
    const alpha = options.alpha ?? 0.6;
    const limit = options.limit ?? 10;

    const lexicalScores = candidates.map((candidate) => this.lexicalScore(query, candidate.description ?? ''));

    if (!query.trim() || candidates.length === 0) {
      return candidates
        .map((candidate, index) => ({ item: candidate, score: lexicalScores[index], lexical: lexicalScores[index], semantic: 0 }))
        .sort((a, b) => b.score - a.score)
        .slice(0, limit);
    }

    const texts = [query, ...candidates.map((candidate) => candidate.description ?? '')];

    let embeddings: number[][] = [];
    try {
      embeddings = await this.embedder.embed(texts);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn(`Embedding provider '${this.embedder.name}' failed. Falling back to lexical ranking.`, error);
    }

    const hasSemanticSignals = Array.isArray(embeddings) && embeddings.length === texts.length;
    const candidateEmbeddings = hasSemanticSignals ? embeddings.slice(1) : [];
    const queryEmbedding = hasSemanticSignals ? embeddings[0] : [];

    const semanticScores = hasSemanticSignals
      ? candidateEmbeddings.map((embedding) => this.cosineSimilarity(queryEmbedding, embedding))
      : candidates.map(() => 0);

    return candidates
      .map((candidate, index) => {
        const lexical = lexicalScores[index];
        const semantic = semanticScores[index];
        const score = alpha * semantic + (1 - alpha) * lexical;
        return { item: candidate, score, lexical, semantic };
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }

  private lexicalScore(query: string, text: string): number {
    if (!query || !text) return 0;
    const tokens = query.toLowerCase().split(/\s+/).filter(Boolean);
    const haystack = text.toLowerCase();
    return tokens.reduce((score, token) => (haystack.includes(token) ? score + 1 : score), 0);
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    const length = Math.min(a.length, b.length);
    if (!length) return 0;

    let dot = 0;
    let normA = 0;
    let normB = 0;

    for (let index = 0; index < length; index += 1) {
      const valueA = a[index] ?? 0;
      const valueB = b[index] ?? 0;
      dot += valueA * valueB;
      normA += valueA * valueA;
      normB += valueB * valueB;
    }

    if (normA === 0 || normB === 0) {
      return 0;
    }

    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}

export class IdentityEmbeddingProvider implements EmbeddingProvider {
  name = 'identity';

  async embed(texts: string[]): Promise<number[][]> {
    return texts.map((text) => {
      const tokens = text.toLowerCase().split(/\s+/).filter(Boolean);
      const unique = Array.from(new Set(tokens));
      return unique.map((token) => (tokens.includes(token) ? 1 : 0));
    });
  }
}

export class OpenAICompatibleEmbeddingProvider implements EmbeddingProvider {
  name = 'openai-compatible';

  private readonly endpoint: string;

  private readonly fetchImpl: typeof fetch;

  private readonly apiKey?: string;

  private readonly organization?: string;

  private readonly additionalHeaders?: Record<string, string>;

  private readonly model: string;

  constructor(configuration: OpenAICompatibleEmbeddingConfig = {}) {
    const base = (configuration.apiUrl ?? DEFAULT_OPENAI_BASE_URL).replace(/\/$/, '');
    this.endpoint = base.endsWith('/embeddings') ? base : `${base}/embeddings`;
    this.fetchImpl = configuration.fetchImpl ?? fetch;
    this.apiKey = configuration.apiKey;
    this.organization = configuration.organization;
    this.additionalHeaders = configuration.additionalHeaders;
    this.model = configuration.model ?? DEFAULT_OPENAI_MODEL;
  }

  async embed(texts: string[]): Promise<number[][]> {
    if (!texts.length) {
      return [];
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...this.additionalHeaders,
    };

    if (this.apiKey) {
      headers.Authorization = `Bearer ${this.apiKey}`;
    }

    if (this.organization) {
      headers['OpenAI-Organization'] = this.organization;
    }

    const response = await this.fetchImpl(this.endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        model: this.model,
        input: texts,
      }),
    });

    if (!response.ok) {
      const detail = await safeReadText(response);
      throw new Error(`OpenAI-compatible embeddings request failed (${response.status} ${response.statusText}): ${detail}`);
    }

    const payload = (await response.json()) as { data?: unknown };
    const rawData = payload?.data;
    if (!Array.isArray(rawData)) {
      throw new Error('Invalid embeddings response: missing data array.');
    }

    if (rawData.length !== texts.length) {
      throw new Error('Embedding response count does not match requested inputs.');
    }

    return rawData.map((entry) => {
      if (Array.isArray(entry)) {
        return entry.map((value) => Number(value) || 0);
      }

      if (entry && typeof entry === 'object') {
        const candidate = entry as { embedding?: unknown; data?: unknown };
        const vector = candidate.embedding ?? candidate.data;
        if (Array.isArray(vector)) {
          return vector.map((value) => Number(value) || 0);
        }
      }

      throw new Error('Embedding entry is not an array.');
    });
  }
}

export const createEmbeddingProvider = (configuration: EmbeddingProviderFactoryConfig = {}): EmbeddingProvider => {
  const requestedProvider = configuration.provider?.trim().toLowerCase();
  const wantsOpenAI =
    requestedProvider === 'openai' ||
    requestedProvider === 'openai-compatible' ||
    requestedProvider === 'openai_compatible' ||
    requestedProvider === 'openai-compatible-provider';

  const hasExplicitOpenAIConfig = Boolean(
    configuration.apiUrl || configuration.apiKey || configuration.model || configuration.organization,
  );

  if (!requestedProvider || requestedProvider === 'identity') {
    if (wantsOpenAI || hasExplicitOpenAIConfig) {
      return new OpenAICompatibleEmbeddingProvider(configuration);
    }
    return new IdentityEmbeddingProvider();
  }

  if (wantsOpenAI || hasExplicitOpenAIConfig) {
    return new OpenAICompatibleEmbeddingProvider(configuration);
  }

  if (configuration.fallbackToIdentity) {
    return new IdentityEmbeddingProvider();
  }

  throw new Error(
    `Unsupported embedding provider '${configuration.provider}'. ` +
      "Supported values: 'identity', 'openai-compatible'.",
  );
};

async function safeReadText(response: Response): Promise<string> {
  try {
    return await response.text();
  } catch (error) {
    return `failed to read body: ${String(error)}`;
  }
}
