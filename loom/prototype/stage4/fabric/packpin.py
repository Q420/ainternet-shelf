"""The pinned Stage 4 validation authority — Vane's examiner pack V2.

Stage 4 (2026-11-21): the examiner validation pack is pinned by the
formal pin record on the shelf (commit f69f3d7d). A run opened under
Stage 4 binds this exact pack in its RUN_OPENED payload (VP-55):
identifier, version, and the SHA-256 over the pack file's exact
bytes. A missing or different digest blocks run opening — the run
cannot silently substitute a later pack revision.

This module holds only the pin constants and the binding payload
shape; it imports nothing from the fabric package, so the engine
can depend on it without a cycle.
"""

PACK_ID = "VANE-STAGE4-EXAMINER-VALIDATION-PACK"
PACK_VERSION = "v2"
PACK_SHA256 = "cce27ee70d6041955364169a6b46f59fe98153f2fe2a30dc315ce0a015eead71"
PACK_BLOB = "02e47728a2aa998280de7b9c0f21fda6a7361b2b"

SPEC_ID = "loom-spec-v0.1-rev9"
AMENDMENT_A1 = "A1"


def stage4_binding(pack_sha256=PACK_SHA256) -> dict:
    """The RUN_OPENED binding for a run opened under Stage 4: the
    authority set (Rev 9 and Amendment A1, separately identified)
    and the exact validation pack. The fold reads the authority set
    (VP-15); the seal regime reads the whole binding (notes I-1)."""
    return {
        "authority_set": {"spec": SPEC_ID, "amendments": [AMENDMENT_A1]},
        "validation_pack": {"id": PACK_ID, "version": PACK_VERSION,
                            "sha256": pack_sha256},
    }


def binding_is_stage4(payload: dict) -> bool:
    """True when a RUN_OPENED payload binds the pinned Stage 4 pack
    exactly — the seal regime's activation condition (notes I-1)."""
    if not isinstance(payload, dict):
        return False
    pack = payload.get("validation_pack")
    if not isinstance(pack, dict):
        return False
    return (pack.get("id") == PACK_ID
            and pack.get("version") == PACK_VERSION
            and pack.get("sha256") == PACK_SHA256)
