#include <cs50.h>
#include <stdio.h>

int main(void)
{
    printf ("Minutes: ");
    int x = get_int();
    
    printf ("Bottles: %i\n", x * 12);
}
