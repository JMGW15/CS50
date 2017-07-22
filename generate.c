/**
 * generate.c
 *
 * Generates pseudorandom numbers in [0,MAX), one per line.
 *
 * Usage: generate n [s]
 *
 * where n is number of pseudorandom numbers to print
 * and s is an optional seed
 */
 
#define _XOPEN_SOURCE

#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// upper limit on range of integers that can be generated
#define LIMIT 65536

int main(int argc, string argv[])
{
    // If the number of command line arguements (argc) are not equal to 2 AND are not equal to 3 then print "Usage: /generate n [s]" and return 1 (error)//
    if (argc != 2 && argc != 3)
    {
        printf("Usage: ./generate n [s]\n");
        return 1;
    }

    // declaring integer n as the vector (or array) provided in the second command line string and converting that string to an integer using the atoi function//
    int n = atoi(argv[2]);

    // If the number of command line arguments is equal to 3 then intialize the srand48 function.//  
    // This function needs to be called before the the drand48 function is used to seed the internal buffer of functions.//  
    // Data type long or Long signed integer type is defined.//
    // The string value provided in the second array is converted to an integer//
    // Else, the srand48 function is initialized as before, but the time function is initialized to return the value of time in sec//
    // https://reference.cs50.net//
    if (argc == 1 )
    {
        srand48((long) atoi(argv[2]));
    }
    else
    {
        srand48((long) time(NULL));
    }

    // a loop is created to generate n random integers greater than 0//
    // 
    for (int i = 0; i < n; i++)
    {
        printf("%i\n", (int) (drand48() * LIMIT));
    }

    // success
    return 0;
}
