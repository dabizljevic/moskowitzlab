import pandas as pd 

def mrsheet_to_chipseq(filename):
    #creates dataframe from mr sheet.
    dataframe = pd.read_excel(filename)

    print(dataframe.iat[2, 21])

    #find first row
    row = 0
    while str(dataframe.iat[row, 0]) != 'Sample 1':
        row += 1
    
    #opens up the text file to be written to.
    with open('chipseq_out.txt', 'w') as file:
        #loops through each row
        while True:
            #ends after all the samples are written
            end_string = str(dataframe.iat[row, 6])
            if end_string == "nan":
                break

            #writes out a single line
            file.write(str(dataframe.iat[row, 6]))
            file.write(',')
            file.write(str(dataframe.iat[row, 32]))
            file.write(',')
            if str(dataframe.iat[row, 34]) != "nan":
                file.write(str(dataframe.iat[row, 34]))
            file.write(',')

            #gets antibody
            control_string = str(dataframe.iat[row, 21]).split(" ")
            if control_string[0] != "none":
                file.write(control_string[0])
            file.write(",")

            #what is control???

            file.write('\n')

            row += 1

mrsheet_to_chipseq('/Users/sdabiz/Desktop/coding/python/chipseq_script/mrsheet.xlsx')
