/**
*
* @Name : hash_fixed.c
*
* Fixed version with corrections to all identified security vulnerabilities
**/
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "hash_fixed.h"

unsigned HashIndex(const char* key) {
    unsigned sum = 0;
    /* FIX for BUG-1: Changed loop condition from 'c' (pointer) to '*c != '\0''
       (dereferenced character comparison). This ensures the loop terminates at
       the null terminator and reads only valid string memory.
       WHY THIS FIXES IT: Pointer is never NULL by definition, but a character
       can be '\0'. Loop now exits at string boundary. */
    for (const char* c = key; *c != '\0'; c++){
        sum += *c;
    }

    /* FIX for BUG-2: Apply modulo operation to ensure index stays within bounds.
       WHY THIS FIXES IT: sum % MAP_MAX produces values 0–127, fitting within
       the data[128] array bounds. Prevents OOB memory access. */
    return sum % MAP_MAX;
}

HashMap* HashInit() {
	/* FIX for BUG-3: Use calloc() instead of malloc().
       calloc() allocates memory AND zero-initializes it (all bytes = 0).
       WHY THIS FIXES IT: All pointers in data[0..127] are initialized to NULL.
       Safe to iterate and dereference without encountering garbage pointers. */
	return calloc(1, sizeof(HashMap));
}

void HashAdd(HashMap *map, PairValue *value) {
    unsigned idx = HashIndex(value->KeyName);

    if (map->data[idx])
        /* FIX for BUG-4: Prepend correctly by linking value to the current head,
           not to the head's next. This maintains the full collision chain.
           WHY THIS FIXES IT: value->Next = map->data[idx] ensures value becomes
           the new head, with all previous nodes still reachable via value->Next->Next.
           No nodes are lost; no memory leak. */
        value->Next = map->data[idx];
    map->data[idx] = value;
}

PairValue* HashFind(HashMap *map, const char* key) {
    unsigned idx = HashIndex(key);

    for( PairValue* val = map->data[idx]; val != NULL; val = val->Next ) {
        /* FIX for BUG-5a: Replace strcpy() with strncmp() for key comparison.
           strncmp(a, b, len) compares strings and returns 0 if equal (a valid comparison).
           Use strncmp() with KEY_STRING_MAX to prevent buffer overrun during comparison.
           WHY THIS FIXES IT: strncmp() is the correct comparison function (returns int,
           not pointer). It respects KEY_STRING_MAX boundary, preventing buffer overflow.
           Only returns true (0) for actual matching keys. */
        if (strncmp(val->KeyName, key, KEY_STRING_MAX) == 0)
            return val;
    }

    return NULL;
}

void HashDelete(HashMap *map, const char* key) {
    unsigned idx = HashIndex(key);

    for( PairValue* val = map->data[idx], *prev = NULL; val != NULL; prev = val, val = val->Next ) {
        /* FIX for BUG-5b: Use strncmp() instead of strcpy() for correct comparison,
           and add 'break' statement after deletion to exit the loop.
           WHY THIS FIXES IT: strncmp() correctly identifies matching key. Break prevents
           continuing iteration with stale prev pointer and prevents attempting to delete
           multiple nodes (only one node per key should exist). */
        if (strncmp(val->KeyName, key, KEY_STRING_MAX) == 0) {
            if (prev)
                prev->Next = val->Next;
            else
                map->data[idx] = val->Next;
            /* FIX for BUG-5c: Add break to exit loop after deletion. */
            break;
        }
    }
}

void HashDump(HashMap *map) {
    for( unsigned i = 0; i < MAP_MAX; i++ ) {
        for( PairValue* val = map->data[i]; val != NULL; val = val->Next ) {
            /* FIX for BUG-6: Replace printf(val->KeyName) with printf("%s", val->KeyName).
               This passes val->KeyName as data, not as a format string.
               WHY THIS FIXES IT: The format string is now a literal "%s" (controlled by code),
               not user-controlled key name. Any format specifiers in KeyName are printed
               as literal characters, not interpreted. Eliminates format string attack. */
            printf("%s", val->KeyName);
        }
    }
}
