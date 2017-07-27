#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef uint8_t  BYTE;

int main(int argc, char *argv[])
{
     // ensure proper usage
    if (argc != 2)
    {
        fprintf(stderr, "Usage: ./recover file.raw\n");
        return 1;
    }

    // remember filenames
    char *raw = argv[1];
    
    
    FILE *inptr = fopen(raw, "r");
    if (inptr == NULL)
    {
        fclose(inptr); 
        fprintf(stderr, "Could not open file");
        return 2;
    }
    
    // set a counter
    int count = 0; 
   
    // declare a buffer of 512 bytes
    BYTE buffer[512];
   
    // set output file name
    char fileo[10]; 
   
    // create an output file
    FILE* output = NULL; 
    
    // until end of file is reached
    while (!feof(inptr))
    {
       
        // check first four bites of buffer for jpg sequence
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] == 0xe0 || buffer[3] == 0xe1))
        {
            // if the sequence occurs but a file is already open, then close it
            if (output != NULL)
            {
                fclose(output);
                
            }
            
            // label the new file
            sprintf(fileo, "%03d.jpg", count);
            
            // create a new file again
            output = fopen(fileo, "w");
            
            // increase the counter
            count++;
            
            // write the jpg buffer to the output file
            fwrite(buffer, sizeof(buffer), 1, output);
        }
        else 
        //if the counter is already going
        if (count > 0)
        {
            // put jpg buffer into the output file, as the jpg spanned multiple buffers
            fwrite(buffer, sizeof(buffer), 1, output);            
            
        }
        //
        fread(buffer, sizeof(buffer), 1, inptr);
        
    }
  
    
    // close the file
    fclose(inptr);

    // close program happily
    return 0;
}
  