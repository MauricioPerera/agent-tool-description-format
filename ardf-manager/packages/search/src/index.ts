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

export class HybridRanker<T extends { description?: string }> {
  constructor(private readonly embedder: EmbeddingProvider) {}

  async rank(query: string, candidates: T[], options: HybridRankingOptions = {}): Promise<RankedCandidate<T>[]> {
    const alpha = options.alpha ?? 0.6;
    const limit = options.limit ?? 10;

    const lexicalScores = candidates.map((candidate) => this.lexicalScore(query, candidate.description ?? ''));
    const texts = [query, ...candidates.map((candidate) => candidate.description ?? '')];
    const embeddings = await this.embedder.embed(texts);
    const queryEmbedding = embeddings[0];
    const candidateEmbeddings = embeddings.slice(1);

    const semanticScores = candidateEmbeddings.map((embedding) => this.cosineSimilarity(queryEmbedding, embedding));

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
    const dot = a.reduce((sum, value, index) => sum + value * b[index], 0);
    const normA = Math.sqrt(a.reduce((sum, value) => sum + value * value, 0));
    const normB = Math.sqrt(b.reduce((sum, value) => sum + value * value, 0));
    if (normA === 0 || normB === 0) return 0;
    return dot / (normA * normB);
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

