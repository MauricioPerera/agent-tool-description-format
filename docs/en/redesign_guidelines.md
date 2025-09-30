# ATDF Redesign Guidelines

## Purpose
Guidance for defining a next-generation version of the Agent Tool Description Format (ATDF) without breaking interoperability for existing agent ecosystems.

## Topics to Cover
- **Protocol Scope**: Problem statement, supported scenarios, relationship with existing standards (JSON Schema, OpenAPI, MCP, etc.).
- **Data Model**: Mandatory fields, optional extensions, aliases, typing rules, parameter schemas, conditional inputs.
- **Usage Semantics**: when_to_use, how_to_use, input/output conventions, version negotiation, capability discovery.
- **Error Model**: Standard payload structure, diagnostic context, remediation hints, mapping to transport or execution errors.
- **Lifecycle & Versioning**: Publishing flow, semantic versioning policy, deprecation timelines, backward-compatibility expectations.
- **Security & Permissions**: Indicators for required scopes, rate limits, risk level, consent prompts.
- **Extensibility**: Mechanism for vendor-specific metadata, namespacing rules, registration process for community extensions.
- **Tooling & Support**: Validators, SDKs, examples, reference servers, conformance suites.
- **Governance**: Decision process, change control, documentation obligations, multilingual requirements.

## Pitfalls to Avoid
- **Over-Specification**: Baking in assumptions about runtimes or transport layers that limit adoption.
- **Under-Specification**: Leaving key behaviors ambiguous, especially for optional fields or defaults.
- **Breaking Changes Without Migration Paths**: Removing or renaming fields without aliases or ignoring semantic versioning.
- **Embedding Business Logic**: Allowing executable logic or dynamic state inside descriptors instead of declarative metadata.
- **Redundant or Conflicting Fields**: Introducing overlapping concepts that confuse agent implementations.
- **Neglecting Validation**: Shipping without linting tools, schema validation, or conformance suites.
- **Ignoring Localization**: Failing to define how translations for descriptions and guidance should be delivered.
- **Security Blind Spots**: Omitting ways to express permissions, audit needs, or privacy considerations.

## Recommended Process
1. Draft a reference model covering the topics above and collect feedback from integrators.
2. Prototype schema updates and refresh validators, SDKs, and documentation in parallel.
3. Provide migration guides, worked examples, and automated tests before declaring the redesign stable.
4. Establish governance artifacts (roadmap, RFC process, changelog) to guide future revisions.
