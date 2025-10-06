module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2022: true,
  },
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  plugins: ['@typescript-eslint', '@next/next'],
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended', 'next/core-web-vitals'],
  ignorePatterns: ['**/dist/**', '**/.next/**', '**/coverage/**'],
  rules: {
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
  },
  settings: {
    next: {
      rootDir: ['apps/web'],
    },
  },
  overrides: [
    {
      files: ['apps/api/**/*.{ts,tsx}', 'packages/**/*.{ts,tsx}', 'scripts/**/*.{ts,tsx}'],
      env: {
        node: true,
      },
      rules: {
        '@next/next/no-html-link-for-pages': 'off',
        '@next/next/no-img-element': 'off',
      },
    },
  ],
};
