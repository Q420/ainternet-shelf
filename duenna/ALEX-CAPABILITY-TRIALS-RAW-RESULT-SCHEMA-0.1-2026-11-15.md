# ALEX — CAPABILITY TRIALS RAW-RESULT SCHEMA 0.1 (Document 3 of 3)

Filed: 2026-11-15. Source: Alex's reply to RB-2026-11-15-32 (capability-trials
raw-result schema assignment), ChatGPT desk conversation 6af9595e. Harvested by
direct page read (the armed waker died after capturing a prior reply; this
reply was read from the page itself). Evidence class: [reported] — Alex's
draft, submitted for Remmy's review; not a validated implementation, per his
own review boundary. Verbatim text follows.

---

I’ll treat this as the standalone schema assignment, not a side note. The schema will support one independently scoreable record per attempt across the 216-attempt pilot, and it will preserve enough raw evidence to avoid rerunning a trial.

The challenge specification supports the following design. I've kept the schema separate from the rubric: it captures what happened and preserves the evidence; it does not decide how well the model performed.

Writing
Independent Model Capability Trials
Raw-Result Schema 0.1 — Document 3 of 3

Status: Proposed — Draft 0.1
Programme: Independent Model Capability Evaluation
Execution status: Paper design only; no pilot authorised
Format: JSON Lines (JSONL), validated by JSON Schema Draft 2020-12

1. Purpose

Define one immutable raw-result record per attempt, containing sufficient information to reconstruct and adjudicate that attempt without rerunning it.

The schema records execution facts, raw inputs and outputs, configuration identity, outcome and failure classification, timing, and evidence provenance.

It does not assign capability scores. Scoring belongs to Document 2, the A+F Pilot Rubric.

2. Record identity and pilot coverage

Each attempt receives a globally unique attempt_id.

The pilot produces:

3 challenge groups: A, F1 and F2.

6 challenges per group.

3 independent replicates per challenge.

4 model configurations.

Expected total: 216 attempt records.

The required identity fields are:

challenge_id

challenge_version

challenge_group

variant_id

configuration_id

replicate_index

The replicate index is an integer from 1 through 3.

3. Model configuration identity

Each record contains a frozen configuration snapshot.

Required fields:

configuration_id

provider

model_name

exact_version

endpoint

execution_mode

checker_version

harness_version

exact_version is mandatory. A display name or model family alone is insufficient.

The configuration snapshot preserves the actual tested configuration, rather than relying on a registry entry that might subsequently change.

The registry's first frozen field, exact model version, must therefore be captured directly in every attempt record.

4. Challenge and variant provenance

The schema must accommodate the two outstanding Challenge Specification review matters without deciding them prematurely.

Variant difficulty

Record:

Variant identifier.

Variant generation method, once established.

Difficulty-equivalence assessment status.

Reference to the assessment evidence.

Challenge authorship

Record:

Assigned author, when established.

Actual author.

Assignment status.

Reference to the authorship or independence review.

These fields preserve the eventual decisions and their evidence. They do not prescribe the unresolved methods.

5. Raw input and output preservation

The submitted prompt and complete raw response must be preserved.

Each artifact supports either:

Inline content, or

An immutable external artifact reference.

Both forms require:

SHA-256 digest.

Exact byte length.

Media type.

Encoding.

An external reference must resolve to the pinned artifact, not a mutable latest-version URL.

A response that was never received is recorded explicitly as unavailable, with a reason. It must not be represented as an empty successful response.

The original challenge artifact must also be referenced, allowing the adjudicator to reconstruct what the model was asked to do.

6. Outcome and failure classification

result_status records execution outcome:

COMPLETED

FAILED

INCOMPLETE

CANCELLED

failure_classification uses the exact classes from Challenge Specification 0.1:

MODEL_REASONING

MODEL_INSTRUCTION

MODEL_FORMAT

PROVIDER_TRANSPORT

TIMEOUT_TRUNCATION

CHECKER

HARNESS

GROUNDING

UNRESOLVED

The classification may be null when no failure has been established.

The record also preserves the classification's rationale and supporting evidence reference.

A successful transport response is not automatically a successful reasoning attempt. A transport failure is not automatically a reasoning failure.

7. Timing and execution metadata

Required timing:

UTC start timestamp.

UTC completion timestamp.

Elapsed duration in milliseconds.

Optional timing and usage measurements include:

Time to first token.

Provider-reported processing duration.

Input token count.

Output token count.

Total token count.

Unavailable measurements remain explicitly unavailable; they must not be inferred.

8. Evidence references

Every record includes an evidence-reference collection.

Evidence can include:

Original challenge.

Exact submitted prompt.

Raw response.

Provider request and response metadata.

Execution logs.

Checker output.

Harness events.

Timing measurements.

Variant-difficulty assessment.

Challenge-authorship assessment.

Subsequent adjudication material.

Each reference identifies its evidence type, immutable location, SHA-256 digest and byte length.

This gives a later adjudicator a traceable route from the result to the underlying evidence.

9. JSON Lines framing

One complete JSON object per line.

UTF-8 encoding.

No enclosing JSON array.

Each line independently validates against the schema.

Each attempt appears once in the raw-result stream.

Original records are immutable.

Corrections and adjudications are additional records, never silent replacements.

10. JSON Schema — Draft 2020-12

The following schema defines the record contract.

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://pulsehq.example/schemas/capability-trial-raw-result-0.1.json",
  "title": "Capability Trial Raw Result",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "attempt_id",
    "recorded_at",
    "challenge",
    "configuration",
    "replicate_index",
    "input",
    "raw_response",
    "result_status",
    "failure_classification",
    "timing",
    "evidence_refs"
  ],
  "properties": {
    "schema_version": {
      "const": "0.1"
    },
    "attempt_id": {
      "type": "string",
      "minLength": 1
    },
    "recorded_at": {
      "type": "string",
      "format": "date-time"
    },
    "challenge": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "challenge_id",
        "challenge_version",
        "challenge_group",
        "variant_id",
        "artifact_ref"
      ],
      "properties": {
        "challenge_id": {
          "type": "string",
          "minLength": 1
        },
        "challenge_version": {
          "type": "string",
          "minLength": 1
        },
        "challenge_group": {
          "enum": ["A", "F1", "F2"]
        },
        "variant_id": {
          "type": "string",
          "minLength": 1
        },
        "artifact_ref": {
          "$ref": "#/$defs/evidenceRef"
        },
        "variant_provenance": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "generation_method_id": {
              "type": ["string", "null"]
            },
            "difficulty_equivalence_status": {
              "enum": [
                "NOT_ASSESSED",
                "PENDING",
                "EQUIVALENT",
                "NOT_EQUIVALENT",
                "INCONCLUSIVE"
              ]
            },
            "assessment_ref": {
              "oneOf": [
                { "$ref": "#/$defs/evidenceRef" },
                { "type": "null" }
              ]
            }
          }
        },
        "authorship": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "assigned_author_id": {
              "type": ["string", "null"]
            },
            "actual_author_id": {
              "type": ["string", "null"]
            },
            "assignment_status": {
              "enum": [
                "UNASSIGNED",
                "ASSIGNED",
                "CONFIRMED",
                "DEVIATION_RECORDED"
              ]
            },
            "review_ref": {
              "oneOf": [
                { "$ref": "#/$defs/evidenceRef" },
                { "type": "null" }
              ]
            }
          }
        }
      }
    },
    "configuration": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "configuration_id",
        "provider",
        "model_name",
        "exact_version",
        "endpoint",
        "execution_mode",
        "checker_version",
        "harness_version"
      ],
      "properties": {
        "configuration_id": {
          "type": "string",
          "minLength": 1
        },
        "provider": {
          "type": "string",
          "minLength": 1
        },
        "model_name": {
          "type": "string",
          "minLength": 1
        },
        "exact_version": {
          "type": "string",
          "minLength": 1
        },
        "endpoint": {
          "type": "string",
          "minLength": 1
        },
        "execution_mode": {
          "type": "string",
          "minLength": 1
        },
        "checker_version": {
          "type": "string",
          "minLength": 1
        },
        "harness_version": {
          "type": "string",
          "minLength": 1
        },
        "settings": {
          "type": "object"
        }
      }
    },
    "replicate_index": {
      "type": "integer",
      "minimum": 1,
      "maximum": 3
    },
    "input": {
      "$ref": "#/$defs/artifact"
    },
    "raw_response": {
      "type": "object",
      "additionalProperties": false,
      "required": ["availability"],
      "properties": {
        "availability": {
          "enum": ["RECEIVED", "NOT_RECEIVED"]
        },
        "artifact": {
          "$ref": "#/$defs/artifact"
        },
        "unavailable_reason": {
          "type": ["string", "null"]
        }
      },
      "allOf": [
        {
          "if": {
            "properties": {
              "availability": { "const": "RECEIVED" }
            }
          },
          "then": {
            "required": ["artifact"],
            "not": {
              "required": ["unavailable_reason"]
            }
          },
          "else": {
            "required": ["unavailable_reason"],
            "not": {
              "required": ["artifact"]
            }
          }
        }
      ]
    },
    "result_status": {
      "enum": [
        "COMPLETED",
        "FAILED",
        "INCOMPLETE",
        "CANCELLED"
      ]
    },
    "failure_classification": {
      "type": ["string", "null"],
      "enum": [
        "MODEL_REASONING",
        "MODEL_INSTRUCTION",
        "MODEL_FORMAT",
        "PROVIDER_TRANSPORT",
        "TIMEOUT_TRUNCATION",
        "CHECKER",
        "HARNESS",
        "GROUNDING",
        "UNRESOLVED",
        null
      ]
    },
    "failure_rationale": {
      "type": ["string", "null"]
    },
    "timing": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "started_at",
        "completed_at",
        "elapsed_ms"
      ],
      "properties": {
        "started_at": {
          "type": "string",
          "format": "date-time"
        },
        "completed_at": {
          "type": "string",
          "format": "date-time"
        },
        "elapsed_ms": {
          "type": "integer",
          "minimum": 0
        },
        "time_to_first_token_ms": {
          "type": ["integer", "null"],
          "minimum": 0
        },
        "provider_duration_ms": {
          "type": ["integer", "null"],
          "minimum": 0
        }
      }
    },
    "usage": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "input_tokens": {
          "type": ["integer", "null"],
          "minimum": 0
        },
        "output_tokens": {
          "type": ["integer", "null"],
          "minimum": 0
        },
        "total_tokens": {
          "type": ["integer", "null"],
          "minimum": 0
        }
      }
    },
    "evidence_refs": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/evidenceRef"
      }
    }
  },
  "$defs": {
    "artifact": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "storage",
        "sha256",
        "byte_length",
        "media_type",
        "encoding"
      ],
      "properties": {
        "storage": {
          "enum": ["INLINE", "EXTERNAL"]
        },
        "content": {
          "type": "string"
        },
        "uri": {
          "type": "string",
          "format": "uri"
        },
        "sha256": {
          "type": "string",
          "pattern": "^[a-f0-9]{64}$"
        },
        "byte_length": {
          "type": "integer",
          "minimum": 0
        },
        "media_type": {
          "type": "string",
          "minLength": 1
        },
        "encoding": {
          "type": "string",
          "minLength": 1
        }
      },
      "oneOf": [
        {
          "properties": {
            "storage": { "const": "INLINE" }
          },
          "required": ["content"],
          "not": { "required": ["uri"] }
        },
        {
          "properties": {
            "storage": { "const": "EXTERNAL" }
          },
          "required": ["uri"],
          "not": { "required": ["content"] }
        }
      ]
    },
    "evidenceRef": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "evidence_type",
        "uri",
        "sha256",
        "byte_length"
      ],
      "properties": {
        "evidence_type": {
          "enum": [
            "CHALLENGE",
            "PROMPT",
            "RAW_RESPONSE",
            "PROVIDER_METADATA",
            "EXECUTION_LOG",
            "CHECKER_OUTPUT",
            "HARNESS_EVENT",
            "TIMING",
            "VARIANT_ASSESSMENT",
            "AUTHORSHIP_ASSESSMENT",
            "ADJUDICATION",
            "OTHER"
          ]
        },
        "uri": {
          "type": "string",
          "format": "uri"
        },
        "sha256": {
          "type": "string",
          "pattern": "^[a-f0-9]{64}$"
        },
        "byte_length": {
          "type": "integer",
          "minimum": 0
        }
      }
    }
  }
}
11. Illustrative JSONL record

Illustrative structure only; hashes and references below are placeholders, not evidence from an executed trial.

{
  "schema_version": "0.1",
  "attempt_id": "A-001-R1-QWEN",
  "recorded_at": "2026-11-15T10:00:00Z",
  "challenge": {
    "challenge_id": "A-001",
    "challenge_version": "0.1",
    "challenge_group": "A",
    "variant_id": "A-001-V1",
    "artifact_ref": {
      "evidence_type": "CHALLENGE",
      "uri": "https://example.invalid/challenges/A-001.json",
      "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "byte_length": 1200
    },
    "variant_provenance": {
      "generation_method_id": null,
      "difficulty_equivalence_status": "NOT_ASSESSED",
      "assessment_ref": null
    },
    "authorship": {
      "assigned_author_id": null,
      "actual_author_id": null,
      "assignment_status": "UNASSIGNED",
      "review_ref": null
    }
  },
  "configuration": {
    "configuration_id": "QWEN-001",
    "provider": "Example Provider",
    "model_name": "Qwen",
    "exact_version": "EXACT-VERSION-REQUIRED",
    "endpoint": "https://example.invalid/model",
    "execution_mode": "STANDARD",
    "checker_version": "0.1",
    "harness_version": "0.1",
    "settings": {}
  },
  "replicate_index": 1,
  "input": {
    "storage": "INLINE",
    "content": "Illustrative challenge prompt.",
    "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "byte_length": 32,
    "media_type": "text/plain",
    "encoding": "UTF-8"
  },
  "raw_response": {
    "availability": "RECEIVED",
    "artifact": {
      "storage": "INLINE",
      "content": "Illustrative model response.",
      "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      "byte_length": 29,
      "media_type": "text/plain",
      "encoding": "UTF-8"
    }
  },
  "result_status": "COMPLETED",
  "failure_classification": null,
  "failure_rationale": null,
  "timing": {
    "started_at": "2026-11-15T10:00:00Z",
    "completed_at": "2026-11-15T10:00:12Z",
    "elapsed_ms": 12000,
    "time_to_first_token_ms": 450,
    "provider_duration_ms": null
  },
  "usage": {
    "input_tokens": null,
    "output_tokens": null,
    "total_tokens": null
  },
  "evidence_refs": []
}
12. Validation and acceptance requirements

A conforming implementation must demonstrate:

Every raw attempt validates against Draft 2020-12.

Exactly one record represents each attempt.

All 216 planned attempts can be uniquely identified.

Exact model version is mandatory and preserved.

Both inline and external raw artifacts are supported.

Artifact hashes recompute against the exact stored bytes.

Missing responses are explicitly represented.

Every failure classification matches the Challenge Specification vocabulary.

Timing values distinguish measured values from unavailable values.

Variant and authorship decisions can be recorded without changing the schema's core identity structure.

Evidence references are sufficient to locate and verify the original challenge, prompt, response and relevant execution evidence.

Raw records remain immutable after creation.

Structural JSON Schema validation does not prove that a URI resolves or that a digest matches its artifact. Those are separate evidence-integrity checks and must be performed during validation and adjudication.

13. Scope boundary

This document defines raw capture only.

It does not define:

Capability scoring or weighting.

Correctness or discovery scores.

F1 seeded-error scoring.

F2 self-correction scoring.

Model rankings.

Pilot execution or provider calls.

Those belong to the rubric and the separately authorised pilot.

Document 3 of 3 — submitted for review.

Review boundary: This is a proposed schema, not a validated implementation. In particular, the JSON Schema enforces structure; the capture and adjudication process must separately verify hashes, timestamps, evidence availability and consistency between related fields. Remmy's review can now assess the raw-result contract before Document 2 proceeds.
