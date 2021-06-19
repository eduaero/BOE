import os
import pandas as pd

provincias = pd.read_excel("provincias.xlsx")
for i, p in enumerate(provincias.Provincia):
    path = "Output/" + str(p)
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s " % path)