/* Nemotron pilot — setuid-viability probe (Stage 5 Build Spec §3.5 point 2;
 * SE-7 demonstration (vii); run at Batch 0 by the operator, Spec §4).
 *
 * This is a PROBE of the setuid mechanism on the build host, not the
 * launcher (the launcher is built at Batch 4 against the Batch 0
 * interface freeze). Installed root-owned, setuid-root, mode 4710,
 * group pilot-supervisor — the launcher's ownership/mode shape — and
 * invoked as pilot-supervisor. It reports the identity it observes
 * inside its own process and its inherited no_new_privs flag.
 *
 * Exit 0 iff effective uid 0 was observed inside the privileged
 * window; exit 1 otherwise. It does nothing else: no arguments, no
 * file access beyond /proc/self/status, no network, no children.
 */
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

int main(void) {
    uid_t ruid = getuid(), euid = geteuid();
    gid_t rgid = getgid(), egid = getegid();
    char line[256];
    FILE *f;

    printf("probe: ruid=%d euid=%d rgid=%d egid=%d\n",
           (int)ruid, (int)euid, (int)rgid, (int)egid);
    f = fopen("/proc/self/status", "r");
    if (f) {
        while (fgets(line, sizeof(line), f)) {
            if (strncmp(line, "NoNewPrivs:", 11) == 0)
                printf("probe: %s", line);
            if (strncmp(line, "Uid:", 4) == 0)
                printf("probe: %s", line);
        }
        fclose(f);
    }
    if (euid == 0) {
        printf("probe: PRIVILEGED WINDOW OBSERVED (euid 0)\n");
        return 0;
    }
    printf("probe: NO PRIVILEGE OBSERVED (euid != 0) — setuid did not elevate\n");
    return 1;
}
