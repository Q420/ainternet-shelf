# ERRATUM — PILOT-CALIBRATION-02 TRANSCRIPT HEADER (2026-11-15)

Ordered by Alex's Batch 6 adjudication (2026-11-15, T03
outcome): "Preserve the original transcript and add an
explicit erratum; don't rewrite the run record."

The runner transcript preserved as
`calibration-transcript-PILOT-CALIBRATION-02.txt` (Batch 6
build tree; also in the Batch 6 checkpoint bundle) opens
with the line:

    PILOT-CALIBRATION-01  sha256 1094802a46f3a2a87469def2f52939821c6345b22c9dd65ade1e6816a589dc90

The certificate label on that line is stale: the sha256 it
carries, 1094802a…, is PILOT-CALIBRATION-02's hash, and the
transcript's content is the Certificate 02 re-calibration
run (13 instances, all ANSWERABLE, T03 the only verdict
change from Certificate 01). The header string was not
updated when the certificate-specific transcript was
written. The transcript itself is preserved byte-for-byte;
this erratum is the correction of record.
