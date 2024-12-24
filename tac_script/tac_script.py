import pandas as pd 
import re 

def excel_to_txt(filename):
    #creates dataframe from excel file.
    dataframe = pd.read_excel(filename)

    #creates dictionary for replicates
    dictionary = {
        "example": 0
    }

    #find first row
    row = 0
    while str(dataframe.iat[row, 0]) != 'Sample name':
        row += 1
    row += 1

    #opens up the text file to be written to.
    with open('tac_out.txt', 'w') as file:
        #loops through each row
        while True:
            #ends after all the samples are written
            end_string = str(dataframe.iat[row, 1])
            if end_string == "nan":
                break

            #creates proper string for title
            title = str(dataframe.iat[row, 1]).replace(" ", "_")

            #writes out a single line
            file.write(title)
            file.write(',')
            file.write(str(dataframe.iat[row, 12]))
            file.write(',')

            if str(dataframe.iat[row, 13]) != "nan":
                file.write(str(dataframe.iat[row, 13]))
            file.write(',')

            replicate_string = re.split("[_123456789 ]", str(dataframe.iat[row, 12]))[0]
            if replicate_string in dictionary.keys():
                dictionary[replicate_string] += 1
            else:
                dictionary[replicate_string] = 1
            file.write(str(dictionary[replicate_string]))

            file.write('\n')

            row += 1
    
    print(dictionary)

excel_to_txt('/Users/sdabiz/Desktop/coding/python/tac_script/tacsheet.xlsx')