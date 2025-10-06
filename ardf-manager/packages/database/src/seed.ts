import { db } from './index';

async function main() {
  db.upsertResource({
    resourceId: 'demo_prompt_coordinator',
    resourceType: 'prompt',
    description: 'Coordinates tools to handle general support queries.',
    whenToUse: 'Use when the agent must orchestrate multiple tools for support scenarios.',
    tags: ['demo', 'prompt'],
    status: 'published',
    version: '1.0.0',
    metadata: { version: '1.0.0', domain: 'support' },
    content: {
      type: 'prompt/template',
      data: {
        role: 'system',
        template_text: 'You are a support orchestrator. Use the available tools to fulfill the request.',
      },
    },
  });
}

main();
