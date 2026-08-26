import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: '../../docs/knowledge-graph/10-openapi.yaml',
  output: 'src',
  plugins: ['@hey-api/typescript'],
});
