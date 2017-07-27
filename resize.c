/**
 * Copies a BMP piece by piece, just because.
 */
       
#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./copy factor infile outfile\n");
        return 1;
    }

    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];
    
    // remember resize factor
    int n = atoi(argv[1]);

    // open input file 
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER and set a new structure for outptr
    BITMAPFILEHEADER bf;
    BITMAPFILEHEADER bfresize;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);
    
    bfresize = bf;

    // read infile's BITMAPINFOHEADER and set a new structure for the outptr
    BITMAPINFOHEADER bi;
    BITMAPINFOHEADER biresize;
    
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);
    
    biresize = bi;

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 || 
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    // calculate new height and width for biresize
    biresize.biWidth = bi.biWidth * n;
    biresize.biHeight = bi.biHeight * n;
    
    // determine padding for scanlines for biresize
    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int paddingresize = (4 - (biresize.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

  //  bfresize.bfSize = 54 + (biresize.biWidth * sizeof(RGBTRIPLE) + paddingresize) * abs(biresize.biHeight);
//    biresize.biSizeImage = bfresize.bfSize - 54;
    
    bi.biSizeImage = (bi.biWidth * sizeof (RGBTRIPLE) + paddingresize) * abs(biresize.biHeight);
    bf.bfSize = (bi.biSizeImage) + 54;
    
    // write outfile's BITMAPFILEHEADER
    fwrite(&bfresize, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&biresize, sizeof(BITMAPINFOHEADER), 1, outptr);

    // iterate over infile's scanlines
    for (int i = 0, biHeight = abs(biresize.biHeight); i < biHeight; i++)
    {
        // each row will be printed out factor times
        int rowcounter = 0;
         
        while (rowcounter < n)
        {
             
            // iterate over pixels in scanline
            for (int j = 0; j < bi.biWidth; j++)
            {
                // temporary storage
                RGBTRIPLE triple;
                 
                // each pixel will be printed out factor times
                int pixelcounter = 0;
 
                // read RGB triple from infile
                fread(&triple, sizeof(RGBTRIPLE), 1, inptr);
             
                // write RGB triple to outfile
                while (pixelcounter < n)
                {
                    fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);
                    pixelcounter++;
                }
            }
             
            // add new padding
            for (int k = 0; k < paddingresize; k++)
                fputc(0x00, outptr);
             
            // seek back to the beginning of row in input file, but not after iteration of printing
            if (rowcounter < (n-1))
                fseek(inptr, -(long int)(bi.biWidth * sizeof(RGBTRIPLE)), SEEK_CUR);
             
            rowcounter++;
        }
         
        // skip over padding, if any
        fseek(inptr, padding, SEEK_CUR);
    }
     
    // close infile
    fclose(inptr);
 
    // close outfile
    fclose(outptr);
 
    return 0;
}