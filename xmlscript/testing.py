import pandas as pd 

#creates dataframe from excel file.
dataframe = pd.read_excel('/Users/sdabiz/Desktop/coding/python/xmlscript/geo.xlsx')

print(str(dataframe.iat[35,0]))


