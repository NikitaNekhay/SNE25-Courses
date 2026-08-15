# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Secure Coding Lab 2** project: a C implementation of a Hash Map (hash table) data structure. The codebase is intentionally vulnerable and designed to teach secure coding practices by identifying and analyzing security flaws.

**Files:**
- `hash.h` - Hash table interface definition
- `hash.c` - Hash table implementation with intentional vulnerabilities
- Lab reports and documentation in `report_template/`

## Build & Test Commands

Since there are no build scripts, use GCC directly to compile and test:

```bash
# Compile the hash implementation
gcc -c hash.c -o hash.o

# Create a test program (you'll need to write test.c separately)
gcc -c test.c -o test.o
gcc hash.o test.o -o hash_test

# Run tests
./hash_test

# Compile with security warnings enabled (to highlight issues)
gcc -Wall -Wextra -std=c11 -c hash.c -o hash.o

# Memory checking with valgrind (if available)
valgrind --leak-check=full ./hash_test
```

## Code Architecture

### Hash Table Structure
The implementation consists of two main components:

1. **PairValue** (hash.h:9-14) - Represents a key-value pair in the hash table
   - `KeyName[255]` - The key (string with max length 255)
   - `ValueCount` - Associated value count
   - `Next` - Pointer for collision chaining (separate chaining strategy)

2. **HashMap** (hash.h:16-19) - The hash table container
   - `data[128]` - Array of 128 buckets (each is a linked list of PairValue)
   - Uses separate chaining for collision resolution

### Core Operations
- `HashInit()` - Allocates and returns a new HashMap
- `HashAdd()` - Adds a key-value pair (inserts at bucket head)
- `HashFind()` - Searches for a key in the table
- `HashDelete()` - Removes a key-value pair
- `HashDump()` - Prints all keys in the table
- `HashIndex()` - Internal hash function that maps keys to bucket indices

## Known Security Vulnerabilities

This codebase intentionally contains vulnerabilities for educational purposes:

1. **HashIndex() infinite loop (lines 12-19)**: The loop condition checks `c` (pointer) instead of `*c` (dereferenced character). After the first iteration, `c` points past the string boundary, accessing undefined memory until a null pointer is encountered.

2. **HashIndex() missing bounds check (line 18)**: Returns raw hash sum without applying `% MAP_MAX`, causing array indices outside the valid range [0, 127], leading to out-of-bounds memory access.

3. **String comparison misuse (lines 37, 48)**: Uses `strcpy()` (which copies and returns pointer) instead of `strcmp()` (which compares and returns int). The condition is always true for valid strings, breaking search/delete logic and enabling key mismatches.

4. **HashAdd() collision chain corruption (line 29)**: Sets `value->Next = map->data[idx]->Next` instead of `value->Next = map->data[idx]`, skipping the head node and breaking the collision chain.

5. **HashDelete() incomplete traversal (lines 48-53)**: Uses `strcpy()` instead of `strcmp()`, and doesn't break after deletion, causing potential double-deletion or memory corruption.

6. **Uninitialized memory (line 22)**: `malloc()` returns uninitialized memory with garbage values in the HashMap array, causing undefined behavior on first access.

7. **Unsafe format string (line 60)**: `printf(val->KeyName)` directly passes user data as format string, enabling format string attacks if keys contain format specifiers.

## Analysis Guidelines

When analyzing this code:
- **Memory safety**: Trace pointer arithmetic and identify out-of-bounds access points (HashIndex, HashInit)
- **String operations**: Compare unsafe functions (strcpy, printf with format strings) vs. safe alternatives (strcmp, printf with "%s")
- **Data structure integrity**: Follow collision chain traversal and identify where node linking is broken
- **Loop conditions**: Examine pointer dereferencing in loop conditions and termination logic
- **Control flow**: Identify unreachable code and premature exits in search/delete operations
- **Exploit scenarios**: Consider how each vulnerability could be triggered and what memory corruption results
- This is a teaching tool—vulnerabilities are intentional for secure coding education

## Testing Vulnerable Code

When writing test cases for this code, focus on triggering specific vulnerabilities:

```bash
# Compile with debug symbols for easier analysis
gcc -g -Wall -Wextra -std=c11 hash.c test.c -o hash_test

# Run under debugger to observe crashes
gdb ./hash_test

# Use valgrind to detect memory errors
valgrind --leak-check=full --show-leak-kinds=all ./hash_test
```

**Test scenarios to expose vulnerabilities:**
- **Long key strings** → Trigger infinite loop in HashIndex (accesses beyond null terminator)
- **Multiple collisions** → Expose broken chain linking in HashAdd and HashDelete
- **Search after add** → Demonstrate strcpy() returning true for any string (false positives)
- **Format string payloads** → If HashDump() is modified to accept user input, test "%x" sequences
- **NULL/uninitialized checks** → Verify that HashInit() doesn't zero-initialize array

## Lab Context

This is part of SNE-25 Secure Development training. The lab emphasizes:
- Understanding common C security pitfalls (buffer overflow, infinite loops, unsafe string functions)
- How hash table implementations can be exploited
- The importance of proper bounds checking, initialization, and string safety
- Connecting individual bugs to potential exploit chains and memory corruption
