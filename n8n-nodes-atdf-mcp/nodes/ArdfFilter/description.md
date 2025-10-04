# ARDF Filter Node

Use the ARDF Filter node to narrow or rank Agent Resource Description Format (ARDF) resources before execution. It accepts a list of descriptors (from /resources, /tools, etc.) and outputs the subset that matches the configured goal, metadata filters, and ranking threshold.

## Inputs
- esources: Array of ARDF descriptors. The node also accepts objects with a esources array (e.g., MCP responses).

## Parameters
- **Operation**: Rank resources against a goal or apply metadata filters only.
- **Resource Types**: Optional whitelist of resource categories (	ool, prompt, workflow, etc.).
- **Domain / Tags**: Case-insensitive filters against metadata.domain and metadata.tags.
- **Language**: Favors localized descriptions when ranking.
- **Goal / Query**: Natural-language task used for ranking (only in Rank Resources).
- **Top Results / Threshold**: Limit the number of returned resources and minimum score.
- **Fallback to Original List**: When no matches are found, return the unfiltered payload.

## Outputs
- esources: Filtered or ranked subset.
- 	otal: Count of resources in the output.
- matched: Number of resources that passed filters.
- allback: Indicates whether the original list was returned.

Combine this node with HTTP Request (to call /resources) and downstream ATDF MCP Client or tool-execution nodes for dynamic agent orchestration.
