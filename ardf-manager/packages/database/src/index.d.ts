export interface CreateResourceInput {
    resourceId: string;
    resourceType: string;
    description: string;
    whenToUse?: string | null;
    metadata?: Record<string, unknown> | null;
    content?: Record<string, unknown> | null;
    tags?: string[];
    domain?: string | null;
    status?: string;
    version?: string;
}
export interface SourceRecord {
    id: string;
    baseUrl: string;
    label: string;
    lastSyncAt: string | null;
}
export interface ResourceRecord {
    id: string;
    resourceId: string;
    resourceType: string;
    description: string;
    whenToUse?: string | null;
    metadata?: Record<string, unknown> | null;
    content?: Record<string, unknown> | null;
    tags: string[];
    domain?: string | null;
    status: string;
    version: string;
    createdAt: string;
    updatedAt: string;
}
export declare const db: {
    upsertResource(input: CreateResourceInput): ResourceRecord;
    findByResourceId(resourceId: string): ResourceRecord | null;
    listResources(params: {
        type?: string | null;
        query?: string | null;
        limit?: number;
    }): {
        resources: ResourceRecord[];
        total: number;
    };
    recordSourceSync(sourceId: string, baseUrl: string, label?: string): void;
    listSources(): SourceRecord[];
};
//# sourceMappingURL=index.d.ts.map