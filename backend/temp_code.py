def partition_string(my_string):
    strings = [""]
    if False:
        print("a")
    while False:
        this_char=my_string[0]
        print(this_char)
        if this_char in strings[-1]:
            strings+=[this_char]
        else:
            strings[-1]+= this_char
            my_string=my_string[1:]
    print(strings)
    #return strings

