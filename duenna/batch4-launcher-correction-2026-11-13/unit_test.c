/* Unit tests for the corrected launcher's pure functions:
 * the run-ID validator (finding 1) and the file-capability
 * check (finding 4). Built with -DPILOT_UNIT_TESTS
 * -DPILOT_TEST_HOOKS against launcher.c; run under ASan. */
#define PILOT_UNIT_TESTS 1
#include "launcher.c"

static int fails = 0, total = 0;
static void chk(const char *name, int cond) {
    total++;
    printf("[%s] %s\n", cond ? "PASS" : "FAIL", name);
    if (!cond) fails++;
}

int main(void) {
    /* Finding 1 — the valid path FIRST (the draft's smoke
     * test never exercised it; that is how the offset bug
     * passed) */
    chk("runid valid canonical", run_id_valid("PILOT-20261113-001") == 1);
    chk("runid valid battery len 1", run_id_valid("A-20261113-001") == 1);
    {
        char buf[128];
        memset(buf, 'B', 64);
        buf[64] = '\0';
        strcat(buf, "-20261113-999");
        chk("runid valid battery len 64, counter 999", run_id_valid(buf) == 1);
        strcat(buf, "X");
        chk("runid invalid over-long", run_id_valid(buf) == 0);
    }
    chk("runid valid leap date 20280229", run_id_valid("PILOT-20280229-001") == 1);
    chk("runid invalid counter 000", run_id_valid("PILOT-20261113-000") == 0);
    chk("runid invalid counter 2 digits", run_id_valid("PILOT-20261113-01") == 0);
    chk("runid invalid counter 4 digits", run_id_valid("PILOT-20261113-0001") == 0);
    chk("runid invalid month 00", run_id_valid("PILOT-20260013-001") == 0);
    chk("runid invalid month 13", run_id_valid("PILOT-20261313-001") == 0);
    chk("runid invalid day 00", run_id_valid("PILOT-20261100-001") == 0);
    chk("runid invalid day 32", run_id_valid("PILOT-20261132-001") == 0);
    chk("runid invalid Feb 29 non-leap 2027", run_id_valid("PILOT-20270229-001") == 0);
    chk("runid invalid Feb 30", run_id_valid("PILOT-20280230-001") == 0);
    chk("runid invalid Apr 31", run_id_valid("PILOT-20260431-001") == 0);
    chk("runid valid Apr 30", run_id_valid("PILOT-20260430-001") == 1);
    chk("runid invalid separator inside date", run_id_valid("PILOT-2026-113-001") == 0);
    chk("runid invalid missing separator", run_id_valid("PILOT20261113-001") == 0);
    chk("runid invalid battery leading dash", run_id_valid("-PILOT-20261113-001") == 0);
    chk("runid invalid battery trailing dash", run_id_valid("PILOT--20261113-001") == 0);
    chk("runid invalid battery bad char", run_id_valid("PI_LOT-20261113-001") == 0);
    chk("runid invalid empty", run_id_valid("") == 0);
    chk("runid invalid two chars (no OOB)", run_id_valid("a-") == 0);
    chk("runid invalid short junk (no OOB)", run_id_valid("x-y") == 0);
    chk("runid invalid date letters", run_id_valid("PILOT-2026AA13-001") == 0);

    /* Finding 4 — file capability check */
    {
        char tmpl[] = "/tmp/captestXXXXXX";
        int fd = mkstemp(tmpl);
        chk("caps: fixture created", fd >= 0);
        if (fd >= 0) close(fd);
        chk("caps: plain file (ENODATA) is empty", file_caps_empty(tmpl) == 0);
        /* crafted nonzero capability set via the raw xattr,
         * in the kernel's real layout: magic_etc, then
         * permitted/inheritable word pairs (20 bytes) */
        struct {
            uint32_t magic_etc;
            struct { uint32_t permitted, inheritable; } d[2];
        } cap;
        memset(&cap, 0, sizeof cap);
        cap.magic_etc = 0x02000000u;              /* VFS_CAP_REVISION_2 */
        cap.d[0].permitted = (1u << 13);          /* CAP_NET_RAW */
        ssize_t r = setxattr(tmpl, "security.capability", &cap, sizeof cap, 0);
        if (r == 0) {
            chk("caps: nonzero capability set fails", file_caps_empty(tmpl) == -1);
            /* and an all-zero rev2 set reads as empty */
            memset(&cap, 0, sizeof cap);
            cap.magic_etc = 0x02000000u;
            r = setxattr(tmpl, "security.capability", &cap, sizeof cap, 0);
            chk("caps: all-zero rev2 set is empty", r == 0 && file_caps_empty(tmpl) == 0);
            /* effective vector alone (inside magic_etc) fails */
            cap.magic_etc = 0x02000000u | 1u;
            r = setxattr(tmpl, "security.capability", &cap, sizeof cap, 0);
            chk("caps: effective-only set fails", r == 0 && file_caps_empty(tmpl) == -1);
        } else {
            printf("[SKIP] caps: setxattr unavailable in this context (errno %d)\n", errno);
        }
        /* an error other than ENODATA fails closed */
        setenv("PILOT_HOOK_XATTR_ERROR", "95", 1); /* ENOTSUP */
        chk("caps: ENOTSUP fails closed", file_caps_empty(tmpl) == -1);
        setenv("PILOT_HOOK_XATTR_ERROR", "5", 1); /* EIO */
        chk("caps: EIO fails closed", file_caps_empty(tmpl) == -1);
        unsetenv("PILOT_HOOK_XATTR_ERROR");
        chk("caps: missing file fails", file_caps_empty("/nonexistent-xyz") == -1);
        unlink(tmpl);
    }

    printf("unit: %d/%d PASS\n", total - fails, total);
    return fails ? 1 : 0;
}
