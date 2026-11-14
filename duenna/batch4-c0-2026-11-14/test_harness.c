/* Test harness programme for the launcher acceptance
 * suite: the fixed exec target of the TEST build. Records
 * the descriptors it was exec'd with, its ids, and an
 * EXECUTED marker, into a result file named by the run
 * identifier (argv[1]) under the test-results tree, then
 * exits 42. If this file ever appears for a run, the
 * child reached execution. */
#define _GNU_SOURCE
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc != 2) return 99;
    /* enumerate the descriptors FIRST: the result file's own
     * descriptor must not appear in the list */
    char fdlist[256] = "";
    DIR *d = opendir("/proc/self/fd");
    if (d) {
        int dfd = dirfd(d);
        struct dirent *de;
        size_t off = 0;
        while ((de = readdir(d)) != NULL) {
            if (de->d_name[0] == '.') continue;
            int fd = atoi(de->d_name);
            if (fd == dfd) continue;
            off += (size_t)snprintf(fdlist + off, sizeof fdlist - off, " %d", fd);
        }
        closedir(d);
    }
    char path[512];
    snprintf(path, sizeof path,
             "/srv/nemotron-pilot/batch4/test-results/%s.txt", argv[1]);
    FILE *f = fopen(path, "w");
    if (!f) return 98;
    fprintf(f, "EXECUTED uid=%d gid=%d\n", (int)getuid(), (int)getgid());
    fprintf(f, "fds:%s\n", fdlist);
    fclose(f);
    return 42;
}
