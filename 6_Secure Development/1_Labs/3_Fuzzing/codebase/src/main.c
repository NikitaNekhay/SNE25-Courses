#include <stdio.h>
#include <stdlib.h>
#include "../include/network.h"
#include "../include/file_handling.h"
#include "../include/crypto.h"
#include "../include/data_processing.h"
#include "../include/authentication.h"

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <module_id> <input>\n", argv[0]);
        printf("Module IDs:\n");
        printf("1 - Network Module\n");
        printf("2 - File Handling Module\n");
        printf("3 - Crypto Module\n");
        printf("4 - Data Processing Module\n");
        printf("5 - Authentication Module\n");
        return 1;
    }

    int module_id = atoi(argv[1]);
    char *input = argv[2];

    switch (module_id) {
        case 1:
            network_handler(input);
            break;
        case 2:
            file_handler(input);
            break;
        case 3:
            crypto_handler(input);
            break;
        case 4:
            data_processor(input);
            break;
        case 5:
            authenticate(input);
            break;
        default:
            printf("Invalid module ID\n");
            break;
    }

    return 0;
}
