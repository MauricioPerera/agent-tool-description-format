import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeOperationError,
} from "n8n-workflow";

interface ArdfResource {
  resource_id?: string;
  resourceId?: string;
  resource_type?: string;
  resourceType?: string;
  description?: string;
  when_to_use?: string;
  whenToUse?: string;
  content?: Record<string, unknown>;
  metadata?: {
    domain?: string;
    tags?: string[];
    [key: string]: unknown;
  };
  localization?: Record<string, { description?: string; when_to_use?: string }>;
  [key: string]: unknown;
}

interface RankedResource extends ArdfResource {
  score: number;
}

const extractResources = (payload: unknown): ArdfResource[] | unknown => {
  if (Array.isArray(payload)) {
    return payload as ArdfResource[];
  }

  if (typeof payload !== "object" || payload === null) {
    return payload as unknown;
  }

  const typedPayload = payload as Record<string, unknown>;

  if (Array.isArray(typedPayload.resources)) {
    return typedPayload.resources as ArdfResource[];
  }

  if (
    typeof typedPayload.data === "object" &&
    typedPayload.data !== null &&
    Array.isArray((typedPayload.data as Record<string, unknown>).resources)
  ) {
    return ((typedPayload.data as Record<string, unknown>).resources ?? []) as ArdfResource[];
  }

  return typedPayload as unknown;
};

const parseList = (value: string): string[] => {
  const trimmed = value.trim();
  if (!trimmed) {
    return [];
  }

  try {
    const parsed = JSON.parse(trimmed);
    if (Array.isArray(parsed)) {
      return (parsed as unknown[])
        .map((entry) => {
          if (entry === null || entry === undefined) {
            return "";
          }
          return entry.toString().trim();
        })
        .filter((entry): entry is string => entry.length > 0);
    }
  } catch (error) {
    // ignore JSON parse errors; fallback to comma separated parsing
  }

  return trimmed
    .split(",")
    .map((entry) => entry.trim())
    .filter((entry) => entry.length > 0);
};

export class ArdfFilter implements INodeType {
  description: INodeTypeDescription = {
    displayName: "ARDF Filter",
    name: "ardfFilter",
    icon: "fa:filter",
    group: ["transform"],
    version: 1,
    description: "Rank or filter ARDF resources against an agent goal",
    defaults: {
      name: "ARDF Filter",
    },
    inputs: ["main"],
    outputs: ["main"],
    properties: [
      {
        displayName: "Operation",
        name: "operation",
        type: "options",
        noDataExpression: true,
        options: [
          {
            name: "Rank Resources",
            value: "rank",
            action: "Rank ARDF resources",
          },
          {
            name: "Filter Resources",
            value: "filter",
            action: "Filter ARDF resources",
          },
        ],
        default: "rank",
      },
      {
        displayName: "Resource Types",
        name: "resourceTypes",
        type: "multiOptions",
        options: [
          { name: "Tool", value: "tool" },
          { name: "Prompt", value: "prompt" },
          { name: "Document", value: "document" },
          { name: "Workflow", value: "workflow" },
          { name: "Policy", value: "policy" },
          { name: "Model", value: "model" },
          { name: "Dataset", value: "dataset" },
          { name: "Connector", value: "connector" },
          { name: "Custom", value: "custom" },
        ],
        default: [],
        description: "Restrict results to selected resource types",
      },
      {
        displayName: "Domain",
        name: "domain",
        type: "string",
        default: "",
        description: "Filter by metadata.domain (case-insensitive)",
      },
      {
        displayName: "Tags",
        name: "tags",
        type: "string",
        default: "",
        placeholder: "policy, compliance",
        description: "Comma-separated list or JSON array of required metadata tags",
      },
      {
        displayName: "Language",
        name: "language",
        type: "string",
        default: "",
        description: "Language code to prioritize localized descriptions (e.g. en, es)",
      },
      {
        displayName: "Goal / Query",
        name: "query",
        type: "string",
        default: "",
        description: "Natural language goal to rank resources against",
        displayOptions: {
          show: {
            operation: ["rank"],
          },
        },
      },
      {
        displayName: "Top Results",
        name: "topN",
        type: "number",
        typeOptions: {
          minValue: 1,
          maxValue: 50,
        },
        default: 3,
        description: "Maximum number of resources to return",
        displayOptions: {
          show: {
            operation: ["rank"],
          },
        },
      },
      {
        displayName: "Score Threshold",
        name: "scoreThreshold",
        type: "number",
        typeOptions: {
          minValue: 0,
        },
        default: 0,
        description: "Minimum score required to include a ranked resource",
        displayOptions: {
          show: {
            operation: ["rank"],
          },
        },
      },
      {
        displayName: "Fallback to Original List",
        name: "fallbackToAll",
        type: "boolean",
        default: true,
        description: "Return the original resource list when no matches are found",
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    for (let itemIndex = 0; itemIndex < items.length; itemIndex++) {
      const rawPayload = items[itemIndex].json;
      const resources = extractResources(rawPayload);

      if (!Array.isArray(resources)) {
        throw new NodeOperationError(
          this.getNode(),
          "Expected an array of ARDF resources in the incoming item",
          { itemIndex },
        );
      }

      const operation = this.getNodeParameter("operation", itemIndex, "rank") as
        | "rank"
        | "filter";
      const selectedTypes = ((this.getNodeParameter(
        "resourceTypes",
        itemIndex,
        [],
      ) as string[]) || []).map((entry: string) => entry.toLowerCase());
      const domain = (this.getNodeParameter("domain", itemIndex, "") as string).trim().toLowerCase();
      const tagList = parseList(this.getNodeParameter("tags", itemIndex, "") as string).map(
        (entry: string) => entry.toLowerCase(),
      );
      const language = (this.getNodeParameter("language", itemIndex, "") as string)
        .trim()
        .toLowerCase();
      const fallbackToAll = this.getNodeParameter("fallbackToAll", itemIndex, true) as boolean;

      let filtered = resources.filter((resource) => {
        const resourceType = (resource.resource_type || resource.resourceType || "").toString().toLowerCase();
        if (selectedTypes.length && !selectedTypes.includes(resourceType)) {
          return false;
        }

        if (domain) {
          const resourceDomain = (resource.metadata?.domain || "").toString().toLowerCase();
          if (resourceDomain !== domain) {
            return false;
          }
        }

        if (tagList.length) {
          const metadataTags = Array.isArray(resource.metadata?.tags)
            ? (resource.metadata?.tags as unknown[])
            : [];
          const resourceTags = metadataTags
            .map((tag) => {
              if (tag === null || tag === undefined) {
                return "";
              }
              return tag.toString().toLowerCase();
            })
            .filter((tag): tag is string => tag.length > 0);
          const hasAllTags = tagList.every((tag) => resourceTags.includes(tag));
          if (!hasAllTags) {
            return false;
          }
        }

        return true;
      });

      if (operation === "rank") {
        const query = (this.getNodeParameter("query", itemIndex, "") as string)
          .toLowerCase()
          .trim();
        const topN = this.getNodeParameter("topN", itemIndex, 3) as number;
        const scoreThreshold = this.getNodeParameter("scoreThreshold", itemIndex, 0) as number;

        const tokens = query ? query.split(/\s+/).filter(Boolean) : [];
        type RankedWithIndex = RankedResource & { _originalIndex: number };

        const ranked: RankedWithIndex[] = filtered.map((resource, index) => {
          const textBlocks: string[] = [];
          if (resource.description) {
            textBlocks.push(resource.description.toString());
          }
          if (resource.when_to_use || (resource as { whenToUse?: string }).whenToUse) {
            const value = resource.when_to_use || (resource as { whenToUse?: string }).whenToUse || "";
            textBlocks.push(value.toString());
          }
          if (Array.isArray(resource.metadata?.tags)) {
            textBlocks.push(resource.metadata?.tags?.join(" ") ?? "");
          }
          if (language && resource.localization?.[language]?.description) {
            textBlocks.push(resource.localization[language].description ?? "");
          }

          const haystack = textBlocks.join(" ").toLowerCase();
          const score = tokens.length
            ? tokens.reduce((accumulator, token) => (haystack.includes(token) ? accumulator + 1 : accumulator), 0)
            : 0;

          return { ...resource, score, _originalIndex: index } as RankedWithIndex;
        });

        ranked.sort((a, b) => {
          if (b.score === a.score) {
            return a._originalIndex - b._originalIndex;
          }
          return b.score - a.score;
        });

        filtered = ranked
          .filter((resource) => resource.score >= scoreThreshold)
          .slice(0, topN)
          .map(({ _originalIndex, ...resource }) => resource);
      }

      if (!filtered.length) {
        if (fallbackToAll) {
          returnData.push({
            json: {
              resources,
              total: resources.length,
              matched: 0,
              fallback: true,
            },
          });
        }
        continue;
      }

      returnData.push({
        json: {
          resources: filtered,
          total: filtered.length,
          matched: filtered.length,
          fallback: false,
        },
      });
    }

    return this.prepareOutputData(returnData);
  }
}
