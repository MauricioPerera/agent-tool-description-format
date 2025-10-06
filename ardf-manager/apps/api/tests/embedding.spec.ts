import { describe, it, expect, vi, beforeEach } from 'vitest';
import { parseAdditionalHeaders, resolveEmbeddingProvider } from '../src/embedding';

type Logger = Pick<Console, 'info' | 'warn'>;

const createEmbeddingProviderMock = vi.hoisted(() => vi.fn());

vi.mock('@ardf/search', async () => {
  const actual = await vi.importActual<typeof import('@ardf/search')>('@ardf/search');
  return {
    ...actual,
    createEmbeddingProvider: createEmbeddingProviderMock,
  };
});

beforeEach(() => {
  createEmbeddingProviderMock.mockReset();
});

describe('parseAdditionalHeaders', () => {
  it('parses valid JSON into a flat header map', () => {
    const result = parseAdditionalHeaders('{"X-Test": "123", "Flag": true}');
    expect(result).toEqual({ 'X-Test': '123', Flag: 'true' });
  });

  it('returns undefined when JSON is invalid', () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    expect(parseAdditionalHeaders('{invalid')).toBeUndefined();
    expect(warnSpy).toHaveBeenCalled();
    warnSpy.mockRestore();
  });
});

describe('resolveEmbeddingProvider', () => {
  it('delegates to createEmbeddingProvider with environment values', () => {
    const fakeProvider = { name: 'openai-compatible', embed: vi.fn() } as any;
    createEmbeddingProviderMock.mockReturnValue(fakeProvider);
    const infoSpy = vi.fn();
    const env = {
      ARDF_EMBEDDING_PROVIDER: 'openai',
      ARDF_EMBEDDING_API_URL: 'https://mock.endpoint',
      ARDF_EMBEDDING_API_KEY: 'token',
      ARDF_EMBEDDING_MODEL: 'model-id',
      ARDF_EMBEDDING_ORG: 'org-id',
      ARDF_EMBEDDING_API_HEADERS: '{"X-App": "ardf"}',
    } as NodeJS.ProcessEnv;

    const provider = resolveEmbeddingProvider(env, { logger: { info: infoSpy, warn: vi.fn() } as Logger });

    expect(provider).toBe(fakeProvider);
    expect(createEmbeddingProviderMock).toHaveBeenCalledWith({
      provider: 'openai',
      apiUrl: 'https://mock.endpoint',
      apiKey: 'token',
      model: 'model-id',
      organization: 'org-id',
      additionalHeaders: { 'X-App': 'ardf' },
      fallbackToIdentity: true,
    });
    expect(infoSpy).toHaveBeenCalledWith("Using 'openai-compatible' embedding provider for ranking.");
  });

  it('falls back to identity provider when factory throws', () => {
    createEmbeddingProviderMock.mockImplementation(() => {
      throw new Error('boom');
    });
    const warnSpy = vi.fn();

    const provider = resolveEmbeddingProvider({}, { logger: { warn: warnSpy, info: vi.fn() } as Logger });

    expect(provider.name).toBe('identity');
    expect(warnSpy).toHaveBeenCalledTimes(1);
  });
});