import type { EmbeddingProvider } from '@ardf/search';
import { createEmbeddingProvider, IdentityEmbeddingProvider } from '@ardf/search';

export const parseAdditionalHeaders = (
  value: string | undefined,
): Record<string, string> | undefined => {
  if (!value) {
    return undefined;
  }

  try {
    const parsed = JSON.parse(value);
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return Object.entries(parsed as Record<string, unknown>).reduce<Record<string, string>>(
        (accumulator, [key, entryValue]) => {
          if (
            typeof key === 'string' &&
            (typeof entryValue === 'string' ||
              typeof entryValue === 'number' ||
              typeof entryValue === 'boolean')
          ) {
            accumulator[key] = String(entryValue);
          }
          return accumulator;
        },
        {},
      );
    }
  } catch (error) {
    // eslint-disable-next-line no-console
    console.warn('Failed to parse ARDF_EMBEDDING_API_HEADERS. Ignoring value.', error);
  }

  return undefined;
};

interface ResolveOptions {
  logger?: Pick<Console, 'info' | 'warn'>;
}

export const resolveEmbeddingProvider = (
  env: NodeJS.ProcessEnv,
  options: ResolveOptions = {},
): EmbeddingProvider => {
  const logger = options.logger ?? console;
  const additionalHeaders = parseAdditionalHeaders(env.ARDF_EMBEDDING_API_HEADERS);

  try {
    const provider = createEmbeddingProvider({
      provider: env.ARDF_EMBEDDING_PROVIDER,
      apiUrl: env.ARDF_EMBEDDING_API_URL,
      apiKey: env.ARDF_EMBEDDING_API_KEY,
      model: env.ARDF_EMBEDDING_MODEL,
      organization: env.ARDF_EMBEDDING_ORG,
      additionalHeaders,
      fallbackToIdentity: true,
    });

    logger.info(`Using '${provider.name}' embedding provider for ranking.`);
    return provider;
  } catch (error) {
    logger.warn('Failed to configure embedding provider. Falling back to identity.', error);
    return new IdentityEmbeddingProvider();
  }
};




