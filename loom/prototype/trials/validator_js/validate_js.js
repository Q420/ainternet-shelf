#!/usr/bin/env node
/* Validator 2 (Node lineage): Ajv Draft 2020-12 + ajv-formats with format
 * validation enabled, implementing the Annex A gate-schema contract and the
 * Rev 4 SS4 gate-validation profile independently of the Python validator.
 * No shared custom validation code. Operates on the RAW response text.
 * Usage: node validate_js.js <response-file>  -> one JSON verdict line. */
"use strict";
const fs = require("fs");
const path = require("path");
const Ajv2020 = require("ajv/dist/2020");
const addFormats = require("ajv-formats");

const schema = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "instruments", "gate_schema.json"), "utf8")
);
const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
const validateSchema = ajv.compile(schema);

const REGIONS = new Set(["alpha", "beta"]);
const ACTIVE_DEPENDENCIES = new Set(["alpha|beta|uses"]); // the one Annex A displays

function crossFieldErrors(c) {
  // Rev 4 SS4: (i)-(iv) applied; (v) not applied; (vi) verification not applied.
  const errs = [];
  const read = c.read_set, write = c.write_set;
  const readS = new Set(read), writeS = new Set(write);
  for (const w of writeS) if (!readS.has(w)) { errs.push("(i) write_set not a subset of read_set"); break; }
  const bvKeys = new Set(Object.keys(c.base_versions));
  if (bvKeys.size !== readS.size || [...bvKeys].some((k) => !readS.has(k)))
    errs.push("(ii) base_versions keys != read_set");
  for (const k of bvKeys) if (!REGIONS.has(k)) errs.push("(iv) base_versions key outside frozen set: " + JSON.stringify(k));
  const contentOps = {};
  for (const op of c.operations) {
    if (op.kind === "replace_content" || op.kind === "append_content") {
      if (!writeS.has(op.region_id)) errs.push("(iii) content op region " + JSON.stringify(op.region_id) + " not in write_set");
      contentOps[op.region_id] = (contentOps[op.region_id] || 0) + 1;
      if (contentOps[op.region_id] > 1) errs.push("(iii) more than one content op on region " + JSON.stringify(op.region_id));
    } else if (op.kind === "add_dependency") {
      const d = op.dependency;
      for (const ep of [d.source, d.target])
        if (!readS.has(ep) || !writeS.has(ep))
          errs.push("(iii) add_dependency endpoint " + JSON.stringify(ep) + " not in read_set and write_set");
      if (ACTIVE_DEPENDENCIES.has(d.source + "|" + d.target + "|" + d.kind))
        errs.push("(iii) add_dependency duplicates the active dependency");
    } else if (op.kind === "remove_dependency") {
      // Dependency-identity edge (Rev 4 SS4): no identity is supplied by the
      // instrument, so the operation cannot pass the scope check.
      errs.push("(iii) remove_dependency cannot be grounded: the instrument supplies no dependency identity");
    } else if (op.kind === "raise_tension") {
      for (const r of op.tension.regions)
        if (!readS.has(r)) errs.push("(iii) raise_tension region " + JSON.stringify(r) + " not in read_set");
    }
  }
  return errs;
}

function validate(rawText) {
  let doc;
  try { doc = JSON.parse(rawText); }
  catch (e) { return { valid: false, schema_errors: ["response is not a single JSON value"], profile_errors: [] }; }
  if (doc === null || typeof doc !== "object" || Array.isArray(doc))
    return { valid: false, schema_errors: ["response is not a JSON object"], profile_errors: [] };
  const ok = validateSchema(doc);
  const schemaErrors = ok ? [] : (validateSchema.errors || []).map((e) => (e.instancePath || "/") + " " + e.message);
  let profileErrors = [];
  if (ok && doc.action === "contribute") profileErrors = crossFieldErrors(doc.contribution);
  return { valid: ok && profileErrors.length === 0, schema_errors: schemaErrors, profile_errors: profileErrors };
}

if (require.main === module) {
  const raw = fs.readFileSync(process.argv[2], "utf8");
  console.log(JSON.stringify(validate(raw)));
}
module.exports = { validate };
