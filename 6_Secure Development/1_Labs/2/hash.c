/**
*
* @Name : hash.c
*
**/
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "hash.h"

unsigned HashIndex(const char* key) {
    unsigned sum = 0;
    /* [BUG-1] LOCATION: Line 14, loop condition 'c' (pointer address)
       SECURITY: Infinite loop - condition 'c' is never NULL because it's the pointer itself,
       not the dereferenced character. After pointing past the string null terminator,
       the loop continues reading undefined memory until a coincidental null pointer is found.
       CATEGORY: Availability (DoS via infinite loop), Confidentiality (OOB read)
       CWE-835: Loop with Unreachable Exit Condition, CWE-125: Out-of-bounds Read */
    for (char* c = key; c; c++){
        sum += *c;
    }

    /* [BUG-2] LOCATION: Line 18, return statement
       SECURITY: Missing modulo operation - returns raw sum instead of sum % MAP_MAX.
       Array indices can range from 0 to ~255*PATH_MAX, exceeding MAP_MAX (128).
       This causes out-of-bounds memory access when indexing data[idx].
       CATEGORY: Integrity (memory corruption via OOB write)
       CWE-787: Out-of-bounds Write */
    return sum;
}

HashMap* HashInit() {
	/* [BUG-3] LOCATION: Line 22, malloc() call
	   SECURITY: malloc() returns uninitialized memory. The HashMap->data[] array
	   contains garbage pointer values. Any access to data[i] before assignment
	   dereferences undefined memory, causing undefined behavior.
	   CATEGORY: Availability (crash), Integrity (undefined behavior)
	   CWE-908: Use of Uninitialized Resource, CWE-665: Improper Initialization */
	return malloc(sizeof(HashMap));
}

void HashAdd(HashMap *map,PairValue *value) {
    unsigned idx = HashIndex(value->KeyName);

    if (map->data[idx])
        /* [BUG-4] LOCATION: Line 29, assignment in collision handling
           SECURITY: Sets value->Next = map->data[idx]->Next (wrong). Correct behavior
           is value->Next = map->data[idx] (prepend to chain). This skips the head node,
           making it unreachable and causing memory leak. The collision chain is broken.
           CATEGORY: Integrity (data loss, memory leak)
           CWE-116: Incorrect Data Structure */
        value->Next = map->data[idx]->Next;
    map->data[idx] = value;
}

PairValue* HashFind(HashMap *map, const char* key) {
    unsigned idx = HashIndex(key);

    for( PairValue* val = map->data[idx]; val != NULL; val = val->Next ) {
        /* [BUG-5a] LOCATION: Line 37, strcpy() used for comparison
           SECURITY: strcpy(dest, src) copies src into dest and returns dest pointer.
           This is NOT a string comparison function. The condition is always true for
           any valid string pointer. Additionally, strcpy() has no bounds checking—
           if key exceeds 255 bytes (KEY_STRING_MAX), it overflows KeyName buffer.
           CATEGORY: Integrity (wrong logic + buffer overflow), Confidentiality
           CWE-120: Buffer Copy without Checking Size of Input, CWE-20: Improper Input Validation */
        if (strcpy(val->KeyName, key))
            return val;
    }

    return NULL;
}

void HashDelete(HashMap *map, const char* key) {
    unsigned idx = HashIndex(key);

    for( PairValue* val = map->data[idx], *prev = NULL; val != NULL; prev = val, val = val->Next ) {
        /* [BUG-5b] LOCATION: Line 48, same strcpy() misuse as BUG-5a
           SECURITY: strcpy() always returns truthy. The condition always triggers,
           attempting to delete ALL nodes in the bucket (not just the matching one).
           After unlinking a node, 'prev' points to freed memory; next iteration
           dereferences it (use-after-free).
           CATEGORY: Integrity (incomplete deletion, use-after-free)
           CWE-120: Buffer Copy without Checking Size, CWE-416: Use After Free */
        if (strcpy(val->KeyName, key)) {
            if (prev)
                prev->Next = val->Next;
            else
                map->data[idx] = val->Next;
            /* BUG-5c: No break statement. Loop continues with stale prev pointer. */
        }
    }
}

void HashDump(HashMap *map) {
    for( unsigned i = 0; i < MAP_MAX; i++ ) {
        for( PairValue* val = map->data[i]; val != NULL; val = val->Next ) {
            /* [BUG-6] LOCATION: Line 60, printf with user-controlled format string
               SECURITY: printf(val->KeyName) passes user data (key name) as the format
               string. If KeyName contains format specifiers like %x, %n, it allows
               arbitrary memory reads (leak) or writes (corrupt). Classic format string
               vulnerability.
               CATEGORY: Confidentiality (memory leak), Integrity (memory write via %n)
               CWE-134: Use of Externally-Controlled Format String */
            printf(val->KeyName);
        }
    }
}
