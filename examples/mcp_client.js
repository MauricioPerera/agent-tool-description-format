#!/usr/bin/env node
// Minimal MCP client that lists ARDF resources by type.

const MCP_URL = process.env.MCP_URL || "http://localhost:8000";

async function fetchJSON(path) {
  const response = await fetch(`${MCP_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function listResources(type, path) {
  const data = await fetchJSON(path);
  const count = data.count ?? data.total ?? data.resources?.length ?? 0;
  console.log(`\n?? ${type.toUpperCase()} (${count})`);
  for (const resource of data.resources ?? []) {
    console.log(`- ${resource.resource_id}: ${resource.description}`);
  }
}

async function main() {
  try {
    const manifest = await fetchJSON("/manifest");
    console.log(`?? MCP Manifest: ${manifest.name} ${manifest.version}`);

    for (const entry of manifest.resources ?? []) {
      await listResources(entry.type, entry.path);
    }
  } catch (error) {
    console.error("? MCP client error:", error.message);
    process.exitCode = 1;
  }
}

main();
