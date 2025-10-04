# n8n-nodes-ardf — Developer Guide

This guide complements the main README and explains how to extend the 
8n-nodes-ardf package with additional ARDF-aware capabilities. It is aimed at engineers who plan to add new nodes or enhance the existing set (Filter, Executor, Workflow Runner).

## ?? Project Layout

`
n8n-nodes-ardf/
+-- index.ts                 # Entry point exporting all node classes
+-- package.json             # Node package metadata and n8n manifest
+-- tsconfig.json            # Typescript configuration
+-- README.md                # User-facing documentation
+-- README.dev.md            # You are here
+-- nodes/
    +-- ArdfFilter/
    ¦   +-- ArdfFilter.node.ts
    +-- ArdfExecutor/
    ¦   +-- ArdfExecutor.node.ts
    +-- ArdfWorkflowRunner/
        +-- ArdfWorkflowRunner.node.ts
`

Build artifacts are emitted to dist/ when you run 
pm run build. During development you can run 
pm run watch to recompile on changes.

## ?? Build & Test

`ash
# install deps once
npm install

# compile TypeScript -> dist/
npm run build

# optional: watch mode while editing
npm run watch
`

To validate the generated JS, point an n8n instance to the repository and ensure the three nodes appear under the "ARDF" category. For automated regression, we recommend writing integration tests using the n8n CLI (
8n node-dev test) or a lightweight harness that mocks MCP endpoints.

## ? Adding New Nodes

1. **Create a folder** under 
odes/, e.g. 
odes/ArdfPolicyGuard/.
2. **Implement** the node in YourNode.node.ts. Follow the structure observable in the existing nodes and prefer:
   - Strong typing (interface/	ype) for request/response payloads.
   - NodeOperationError for surfacing user-facing failures.
   - Helper functions outside of the class for reusability.
3. **Export** the node from index.ts and update the package.json 
8n.nodes list if required.
4. **Document** the node in README.md (user scope) and add a technical blurb in this file.
5. **Build** and test in n8n.

Example snippet for index.ts extension:

`	s
import { ArdfPolicyGuard } from './nodes/ArdfPolicyGuard/ArdfPolicyGuard.node';
export const nodes = [
  ArdfFilter,
  ArdfExecutor,
  ArdfWorkflowRunner,
  ArdfPolicyGuard,
];
`

## ?? Suggested Extensions

| Node Idea | Purpose | Key Considerations |
|-----------|---------|--------------------|
| **ARDF Policy Validator** | Enforce policy/rules resources before executing tools/prompts | Resolve policy dependencies; expose failure details |
| **ARDF Model Tester** | Run health checks against model/spec resources (latency, accuracy) | Requires test datasets and scoring strategy |
| **ARDF Cache Loader** | Cache /resources payloads in Redis/SQLite for faster filtering | Invalidate cache on /catalog/reload events |
| **ARDF Feedback Logger** | Post execution outcomes to /feedback endpoints | Allow batching and retries |
| **ARDF Vector Ranker** | Call a semantic ranking service (OpenAI, Cohere, local embeddings) | Provide fallbacks and configurable similarity metric |

Each node should use the same MCP base URL parameter to keep configuration consistent.

## ?? Recommended Patterns

- **Shared Helpers:** Extract repeated logic (endpoint building, payload shaping) into utility modules if reused across nodes.
- **Error Surfaces:** Always provide actionable NodeOperationError messages (include the failing resource ID).
- **Context Propagation:** When running workflows, merge outputs carefully so keys do not overwrite critical context. Consider namespacing under step_<name> if collisions are likely.
- **Observability:** Expose optional logging (e.g. erbose boolean) that surfaces step-level telemetry via the node output.

## ?? Security & Stability

- Validate user-supplied URLs to prevent SSRF when running inside secured environments.
- Set reasonable HTTP timeouts and retry logic for long-running MCP executions.
- Sanitize/omit sensitive values when logging or returning context.

## ?? Publishing Checklist

1. Run 
pm run build.
2. Verify that dist/ contains compiled .js versions of all nodes.
3. Ensure package.json 
8n.nodes paths point to the compiled files (e.g. dist/nodes/... if you distribute the built package).
4. Bump the version number and tag your release in git.
5. Share installation instructions (N8N_CUSTOM_EXTENSIONS) with downstream teams.

Happy hacking!
