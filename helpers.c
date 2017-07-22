/**
 * helpers.c
 *
 * Helper functions for Problem Set 3.
 */
 
#include <cs50.h>
#include <math.h>
#include "helpers.h"

/**
 * Returns true if value is in array of n values, else false.
 */
bool search(int value, int values[], int n)
{
    if (value < 0)
    {
        return false;
    }
    int left = 0; 
    int right = n - 1;

    while (n > 0)
    {
        int mid= (right - left) / 2 + left;
        if (values[mid] == value)
        {
            return true;
        }
        if (values[mid] > value)
        {
            right = mid - 1;
        }
        if (values[mid] < value)
        {
            left = mid + 1;
        }
        n = right - left + 1;
    }
    return false;
}
/**
 * Sorts array of n values.
 */
void sort(int values[], int n)
{
    for (int i=0; i<(n-2); i++)
    {
        if (values[i]>values[i+1])
        {
            int temp1 = values[i];
            int temp2 = values[i+1];
            values[i] = temp2;
            values[i+1] = temp1;
        }
    }
    return;
}
