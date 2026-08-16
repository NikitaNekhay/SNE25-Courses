/**
*
* @Name : hash_fixed.h
*
* Fixed version with security hardening notes
**/
#ifndef __HASH_FIXED__
#define __HASH_FIXED__

    typedef struct {
        /* KEY_STRING_MAX = 255 bytes
           SECURITY FIX: Use strncpy(dest, src, KEY_STRING_MAX - 1) throughout code
           to prevent overflow. Always null-terminate manually: dest[KEY_STRING_MAX-1] = '\0'.
           Alternative: Use snprintf() for safer string formatting.
           See hash_fixed.c for correct strncmp() usage (BUG-5a fix). */
        #define KEY_STRING_MAX 255
		char KeyName[KEY_STRING_MAX];
		int  ValueCount;
        struct PairValue* Next;
	} PairValue;

	typedef struct {
        /* MAP_MAX = 128 buckets (indices 0–127)
           SECURITY FIX: HashIndex() now applies % MAP_MAX (see hash_fixed.c line ~22).
           This guarantees all indices fit within data[0..127] bounds. */
        #define MAP_MAX 128
		PairValue* data[MAP_MAX];
	} HashMap;

    HashMap* HashInit();
    void HashAdd(HashMap *map, PairValue *value);
    void HashDelete(HashMap *map, const char* key);
    PairValue* HashFind(HashMap *map, const char* key);
    void HashDump(HashMap *map);
#endif
