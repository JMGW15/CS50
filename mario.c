#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int x = 0;
    do {
	    printf("Height:");
	    x = GetInt();
	   }
	while (x < -1 || x > 23); // if false, proceed to following code //
	   
	for(int i = 0; i < x; i++) // # of rows to publish based on user input or x integer, first row is initialized at 0 //
	    {
        for(int s = 0; s < x-i-1; s++) // # of spaces to publish based on the current row, or "i", and the user input, or x integer //
            {
            printf("%s", " ");
            }
        for(int h = 0; h < i+2; h++)  // # of hashes to publish based on the current row, or "i", and the user input, or x integer //
		    {
			printf("#");
		    }
	    printf("\n"); // prints output of inner loops //
	    }	
}
