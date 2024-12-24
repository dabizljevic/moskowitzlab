import pandas as pd 

def excel_to_txt(filename):
    #creates dataframe from excel file.
    dataframe = pd.read_excel(filename)

    #find first row
    row = 0
    while str(dataframe.iat[row, 0]) != 'Sample name':
        row += 1
    row += 1

    #opens up the text file to be written to.
    with open('geo_out.txt', 'w') as file:
        #loops through each row
        while True:
            #ends after all the samples are written
            end_string = str(dataframe.iat[row, 0])
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
                file.write('paired')
            else:
                file.write(',')
                file.write('single')

            file.write('\n')

            row += 1

excel_to_txt('/Users/sdabiz/Desktop/coding/python/xmlscript/geo.xlsx')
#paired /Users/sdabiz/Desktop/coding/python/xmlscript/geo_paired.xlsx
#single /Users/sdabiz/Desktop/coding/python/xmlscript/geo.xlsx