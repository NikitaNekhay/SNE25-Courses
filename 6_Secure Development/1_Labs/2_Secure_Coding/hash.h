/**
*
* @Name : hash.h
*
**/
#ifndef __HASH__
#define __HASH__

    typedef struct {
        /* KEY_STRING_MAX = 255 bytes
           SECURITY NOTE: Fixed-size buffer is vulnerable to buffer overflow if
           code uses strcpy() or other unbounded copy operations (see hash.c lines 37, 48).
           Should use strncpy() or validate input length. */
        #define KEY_STRING_MAX 255
		char KeyName[KEY_STRING_MAX];
		int  ValueCount;
        struct PairValue* Next;
	} PairValue;

	typedef struct {
        /* MAP_MAX = 128 buckets (indices 0–127)
           SECURITY NOTE: Hash function in hash.c line 18 returns sum without % MAP_MAX,
           allowing indices far outside this range, causing OOB memory access. */
        #define MAP_MAX 128
		PairValue* data[MAP_MAX];
	} HashMap;

    HashMap* HashInit();
    void HashAdd(HashMap *map, PairValue *value);
    void HashDelete(HashMap *map, const char* key);
    PairValue* HashFind(HashMap *map, const char* key);
    void HashDump(HashMap *map);
#endif
