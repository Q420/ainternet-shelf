# ALEX — CAPABILITY TRIALS: RAW-RESULT SCHEMA 0.2 (Document 3 of 3)

Provenance: Alex (ChatGPT desk), reply to RB-2026-11-15-37, conversation 6af966fb-2150-83e8-9985-4e82978b592c, captured 2026-11-15T01:13:24-0700 via the Remmy Browser watcher (watcher-sweep). Filed verbatim by Remmy. Schema 0.2 incorporates the accepted RB-33 findings F1-F6 and the F2 stage-preservation obligation from RB-2026-11-15-37. Paper draft only; not filed as frozen, not validated as an implementation, no pilot execution authorised.

---

That closes the rubric review. All six findings are discharged, and the amendment record now travels with the rubric as part of the eventual three-document freeze decision. No separate Ben approval is needed for those individual amendments.

The remaining deliverable on my side is Raw-Result Schema 0.2. It needs to incorporate the accepted RB-33 changes and the new F2 requirement: one attempt, two preserved stages, exact attempt_id linkage, and no silent replacement of the initial output.

I retrieved Schema 0.1, Remmy's RB-33 review, the challenge specification and the filed rubric amendments. The draft below incorporates the six schema findings and the new F2 obligation. It remains a paper draft, not a validated implementation or execution authorization.

Writing
Independent Model Capability Trials
Raw-Result Schema 0.2 — Document 3 of 3

Status: Proposed — Draft 0.2
Programme: Independent Model Capability Evaluation
Execution: Paper design only; no pilot authorised
Format: JSON Lines (JSONL), validated using JSON Schema Draft 2020-12
Supersedes: Raw-Result Schema 0.1
Review basis: RB-2026-11-15-33 and RB-2026-11-15-36/37

1. Purpose

Define one immutable raw-result record per challenge attempt, preserving enough information to reconstruct and adjudicate the attempt without rerunning it.

The schema captures execution facts, configuration identity, raw inputs and outputs, outcome, failure classification, timing and evidence provenance.

It does not assign capability scores. Scoring belongs to Document 2, the A+F Pilot Rubric, including its recorded amendments.

2. Record identity and pilot coverage

The pilot comprises:

Three challenge groups: A, F1 and F2.

Six challenges per group.

Three independent replicates per challenge.

Four model configurations.

Expected total: 216 attempt records.

Each attempt has one globally unique attempt_id.

Construction rule:

CT.<challenge_id>.<variant_id>.R<replicate_index>.<configuration_id>

The component identifiers must use letters, digits, underscores or hyphens, and must not contain periods. The replicate component is R1, R2 or R3.

The record includes:

attempt_id

run_id

recorded_at

challenge

configuration

replicate_index

run_id identifies the execution sitting or session. Multiple runs may contribute to the 216 attempts.

Stream-level validation must establish that every attempt_id is unique and that the planned challenge/configuration/replicate combinations are accounted for.

3. Model configuration identity

Every record contains a frozen configuration snapshot:

configuration_id

provider

model_name

exact_version

endpoint

execution_mode

checker_version

harness_version

settings

exact_version is mandatory. A display name or model family alone is insufficient.

The settings object may contain configuration-specific values. The harness must freeze the settings-key vocabulary and the values used for each configuration.

Two configurations differing in any frozen setting must have distinct configuration_id values. A configuration identity must never silently refer to different settings across records.

4. Challenge and variant provenance

Every challenge record requires both variant_provenance and authorship objects.

Unresolved decisions must be represented through explicit states or null values, not by omitting the objects.

Variant provenance

Records:

generation_method_id

difficulty_equivalence_status

assessment_ref

Permitted difficulty states:

NOT_ASSESSED, PENDING, EQUIVALENT, NOT_EQUIVALENT, INCONCLUSIVE.

Authorship

Records:

assigned_author_id

actual_author_id

assignment_status

review_ref

Permitted assignment states:

UNASSIGNED, ASSIGNED, CONFIRMED, DEVIATION_RECORDED.

The schema preserves the eventual decisions and evidence without prescribing the still-open variant-difficulty method or authorship assignment.

5. Raw input and output preservation

The original challenge artifact is referenced through challenge.artifact_ref.

The exact submitted input and complete raw response are preserved as artifacts.

Each artifact supports either:

INLINE: content stored in the record.

EXTERNAL: immutable external URI.

Both forms require:

SHA-256 digest.

Exact byte length.

Media type.

Encoding.

External references must resolve to pinned artifacts, not mutable latest-version URLs.

A response never received must be represented as NOT_RECEIVED, with an explicit reason. It must not be represented as an empty successful response.

The top-level input and raw_response fields represent the initial task submission and response. For A and F1, these are the complete attempt exchange. For F2, they represent Stage 1.

6. F2 — Two-stage own-work audit preservation

F2 remains one challenge attempt and one record. Its two stages do not increase the 216-attempt count.

The record preserves:

Stage 1 — Initial work

The original task input in the top-level input.

The complete initial model output in the top-level raw_response.

Stage 2 — Independent audit

The audit prompt in stages.stage2.audit_input.

The complete audit/revision response in stages.stage2.audit_response.

The exact initial attempt identifier in stages.stage2.initial_attempt_id.

The stage-two recording timestamp.

initial_attempt_id must equal the containing record's attempt_id.

The initial Stage 1 response is immutable. Stage 2 must not overwrite, replace or mutate it. Both stages must be reconstructible from the record and its referenced evidence without relying on conversational history or mutable external state.

If Stage 2 is not received, its response state must be NOT_RECEIVED, with a reason. The initial Stage 1 record remains preserved.

The JSON Schema enforces the presence and structure of the F2 stage object. A separate semantic validation must verify that initial_attempt_id exactly equals the containing record's attempt_id.

7. Outcome and failure classification

result_status records:

COMPLETED

FAILED

INCOMPLETE

CANCELLED

failure_classification uses the exact nine classes from Challenge Specification 0.1:

MODEL_REASONING

MODEL_INSTRUCTION

MODEL_FORMAT

PROVIDER_TRANSPORT

TIMEOUT_TRUNCATION

CHECKER

HARNESS

GROUNDING

UNRESOLVED

A null classification means no failure has been established.

Whenever a classification is asserted, the record must include:

A non-empty failure_rationale.

At least one failure_evidence_refs entry identifying the supporting evidence.

Those evidence references must also be present in evidence_refs.

When classification is null, rationale must be null and failure_evidence_refs must be empty.

A successful transport response is not automatically a successful reasoning attempt. A transport or harness failure is not automatically a reasoning failure.

8. Timing and execution metadata

Required timing:

UTC start timestamp.

UTC completion timestamp.

Elapsed duration in milliseconds.

Optional measurements:

Time to first token.

Provider-reported processing duration.

Input token count.

Output token count.

Total token count.

Unavailable measurements remain explicitly null or absent. They must not be inferred.

9. Evidence references

Every record contains an evidence_refs array.

An empty array is conforming. The mandatory challenge artifact_ref, in-record input and response artifacts already provide the minimum route to reconstruct the attempt.

Where additional evidence exists, references may identify:

Provider request or response metadata.

Execution logs.

Checker output.

Harness events.

Timing measurements.

Variant-difficulty assessment.

Authorship assessment.

Adjudication material.

Other relevant evidence.

Each reference identifies evidence type, immutable URI, SHA-256 digest and byte length.

Every failure_evidence_refs entry must correspond to an entry in evidence_refs.

10. JSON Lines framing and immutability

One complete JSON object per line.

UTF-8 encoding.

No enclosing JSON array.

Each line independently validates against Draft 2020-12.

Each attempt appears once in the raw-result stream.

Original records are immutable.

Corrections and adjudications are additional records, never silent replacements.

The F2 Stage 1 output is not an exception to the immutability rule. Stage 2 adds evidence; it does not replace Stage 1.

11. JSON Schema — Draft 2020-12

The canonical $id below identifies this proposed Schema 0.2 Shelf document.

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/Q420/ainternet-shelf/blob/main/duenna/ALEX-CAPABILITY-TRIALS-RAW-RESULT-SCHEMA-0.2-2026-11-15.md",
  "title": "Capability Trial Raw Result",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "attempt_id",
    "run_id",
    "recorded_at",
    "challenge",
    "configuration",
    "replicate_index",
    "input",
    "raw_response",
    "result_status",
    "failure_classification",
    "failure_rationale",
    "failure_evidence_refs",
    "timing",
    "evidence_refs"
  ],
  "properties": {
    "schema_version": {
      "const": "0.2"
    },
    "attempt_id": {
      "type": "string",
      "pattern": "^CT\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.R[1-3]\\.[A-Za-z0-9_-]+$"
    },
    "run_id": {
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
        "artifact_ref",
        "variant_provenance",
        "authorship"
      ],
      "properties": {
        "challenge_id": {
          "type": "string",
          "pattern": "^[A-Za-z0-9_-]+$"
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
          "pattern": "^[A-Za-z0-9_-]+$"
        },
        "artifact_ref": {
          "$ref": "#/$defs/evidenceRef"
        },
        "variant_provenance": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "generation_method_id",
            "difficulty_equivalence_status",
            "assessment_ref"
          ],
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
                {"$ref": "#/$defs/evidenceRef"},
                {"type": "null"}
              ]
            }
          }
        },
        "authorship": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "assigned_author_id",
            "actual_author_id",
            "assignment_status",
            "review_ref"
          ],
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
                {"$ref": "#/$defs/evidenceRef"},
                {"type": "null"}
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
        "harness_version",
        "settings"
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
      "$ref": "#/$defs/response"
    },
    "stages": {
      "type": "object",
      "additionalProperties": false,
      "required": ["stage2"],
      "properties": {
        "stage2": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "initial_attempt_id",
            "recorded_at",
            "audit_input",
            "audit_response"
          ],
          "properties": {
            "initial_attempt_id": {
              "type": "string",
              "minLength": 1
            },
            "recorded_at": {
              "type": "string",
              "format": "date-time"
            },
            "audit_input": {
              "$ref": "#/$defs/artifact"
            },
            "audit_response": {
              "$ref": "#/$defs/response"
            }
          }
        }
      }
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
    "failure_evidence_refs": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/evidenceRef"
      }
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
  "allOf": [
    {
      "if": {
        "properties": {
          "challenge": {
            "properties": {
              "challenge_group": {"const": "F2"}
            },
            "required": ["challenge_group"]
          }
        },
        "required": ["challenge"]
      },
      "then": {
        "required": ["stages"]
      },
      "else": {
        "not": {
          "required": ["stages"]
        }
      }
    },
    {
      "if": {
        "properties": {
          "failure_classification": {
            "type": "string"
          }
        },
        "required": ["failure_classification"]
      },
      "then": {
        "properties": {
          "failure_rationale": {
            "type": "string",
            "minLength": 1
          },
          "failure_evidence_refs": {
            "type": "array",
            "minItems": 1
          }
        }
      },
      "else": {
        "properties": {
          "failure_rationale": {"type": "null"},
          "failure_evidence_refs": {
            "type": "array",
            "maxItems": 0
          }
        }
      }
    }
  ],
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
            "storage": {"const": "INLINE"}
          },
          "required": ["content"],
          "not": {"required": ["uri"]}
        },
        {
          "properties": {
            "storage": {"const": "EXTERNAL"}
          },
          "required": ["uri"],
          "not": {"required": ["content"]}
        }
      ]
    },
    "response": {
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
              "availability": {"const": "RECEIVED"}
            }
          },
          "then": {
            "required": ["artifact"],
            "not": {"required": ["unavailable_reason"]}
          },
          "else": {
            "required": ["unavailable_reason"],
            "properties": {
              "unavailable_reason": {
                "type": "string",
                "minLength": 1
              }
            },
            "not": {"required": ["artifact"]}
          }
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
12. Validation and acceptance requirements

A conforming implementation must demonstrate:

Every record validates against JSON Schema Draft 2020-12.

Every attempt has a unique, correctly constructed attempt_id.

Every record has a run_id.

All 216 planned attempts can be uniquely identified and accounted for.

Exact model version and frozen configuration settings are preserved.

Variant provenance and authorship objects are present, including explicit unresolved states.

A non-null failure classification requires a rationale and supporting evidence references.

An empty evidence_refs array is accepted.

Inline and external artifacts are supported.

Artifact hashes recompute against the exact stored bytes.

Missing responses are explicitly represented.

Every failure classification matches the Challenge Specification vocabulary.

F2 has exactly one attempt record, with Stage 1 preserved in the top-level input and response fields.

F2 Stage 2 preserves its audit input and response and identifies the Stage 1 attempt by exact attempt_id.

F2 Stage 2 cannot silently replace or mutate the Stage 1 response.

Stage-two evidence is reconstructible without conversational history or mutable external state.

Failure evidence references correspond to entries in the record's evidence_refs.

Raw records remain immutable after creation.

Structural JSON Schema validation does not prove that a URI resolves, a digest matches its artifact, a configuration identity is consistent across records, or an F2 initial_attempt_id matches the containing record. Those are separate evidence-integrity and cross-record validation checks.

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

14. Review boundary

Draft 0.2 incorporates the accepted findings from RB-2026-11-15-33 and the F2 stage-preservation obligation accepted in RB-2026-11-15-37.

It is submitted for independent review. It is not a validated implementation, a frozen schema, or authorization to execute the capability pilot.

Document 3 of 3 — proposed Schema 0.2.

The draft now makes the F2 relationship explicit without counting its second stage as another attempt. It also keeps structural checks separate from semantic and evidence-integrity checks.

Next: Remmy's independent review of Schema 0.2. I have not treated it as filed, frozen, or validated.
