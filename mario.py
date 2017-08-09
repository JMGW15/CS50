import cs50

def main():
    while True: #induces infinite loop
        print("Height: ", end="")# prompt user for height of pyramid
        h = cs50.get_int() # n is included in scope, doesn't matter if after
        if h > -1 or h < 24:
            break #break out of loop

    for i in range(h):
        for s in range(h-i-1):
            print(" ", end="")
        for b in range(i+2):
            print("#", end="")
        print()
    
if __name__ == "__main__": 
    main()



