export function validateFeed(data) {
  const fail = reason => ({ ok: false, version: null, reason });
  if (!data || typeof data !== "object" || Array.isArray(data)) return fail("feed must be an object");
  if (data.kind !== "aivory-state-feed") return fail("unexpected feed kind");

  const version = data.schema_version === undefined ? 0 : data.schema_version;
  if (version !== 0 && version !== 1) return fail("unsupported schema version");

  if (version === 1) {
    if (!data.job || typeof data.job !== "object" || Array.isArray(data.job)) return fail("job object is required");
    if (typeof data.generated_at !== "string" || Number.isNaN(Date.parse(data.generated_at))) return fail("missing or invalid generated_at");
    if (!Array.isArray(data.offices)) return fail("offices collection is required");
    if (!Array.isArray(data.historical_runs)) return fail("historical_runs collection is required");
    if (!Array.isArray(data.artifacts)) return fail("artifacts collection is required");
    if (!Array.isArray(data.decisions)) return fail("decisions collection is required");
  }

  const runs = version === 1 ? data.historical_runs : data.runs;
  if (!Array.isArray(runs)) return fail("historical run collection is missing");
  for (const run of runs) {
    if (!run || typeof run.run !== "string" || typeof run.outcome !== "string") return fail("historical run identity/outcome is malformed");
    for (const field of ["iterations", "events", "dispatches"]) {
      if (!Number.isFinite(run[field]) || run[field] < 0) return fail("historical run counter is malformed: " + field);
    }
  }

  if (version === 1) {
    for (const office of data.offices) {
      if (!office || typeof office.id !== "string" || typeof office.role !== "string" || typeof office.status !== "string") return fail("current office identity/status is malformed");
      if (office.occupant !== undefined && office.occupant !== null && typeof office.occupant !== "string") return fail("office occupant is malformed");
      if (office.journal !== undefined && !Array.isArray(office.journal)) return fail("office journal is malformed");
      if (office.transcript !== undefined && !Array.isArray(office.transcript)) return fail("office transcript is malformed");
      if (office.record !== undefined && (!office.record || typeof office.record !== "object" || Array.isArray(office.record))) return fail("office record is malformed");
      for (const ref of ["journal_ref", "record_ref", "transcript_ref", "briefcase_folder"]) {
        if (office[ref] !== undefined && typeof office[ref] !== "string") return fail("office source reference is malformed: " + ref);
      }
    }
    for (const artifact of data.artifacts) {
      if (!artifact || typeof artifact.path !== "string") return fail("artifact path is malformed");
      if (artifact.bytes !== undefined && (!Number.isFinite(artifact.bytes) || artifact.bytes < 0)) return fail("artifact byte size is malformed");
    }
    for (const decision of data.decisions) {
      if (!decision || typeof decision.id !== "string" || typeof decision.title !== "string" || typeof decision.status !== "string") return fail("decision record is malformed");
    }
  }

  if (data.job?.sources !== undefined) {
    if (!Array.isArray(data.job.sources) || !data.job.sources.every(source =>
      source && typeof source.path === "string" && Number.isFinite(source.bytes) && source.bytes >= 0)) {
      return fail("job source inventory is malformed");
    }
  }
  return { ok: true, version, reason: null };
}
