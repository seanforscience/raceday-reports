import pandas as pd

class RaceDay():
    def __init__( self , excelFilePath ):
        
        self.excelFilePath = excelFilePath
        self.data = self.loadExcel()
        
        self.entrants = self.getEntrantsList(self.data)
        self.shirts = self.getShirts(self.data)
    
    def loadExcel( self ):

        standardize = lambda text : text.lower().replace("  "," ").replace("  "," ").replace(" ","_")
    
        rawExport = pd.read_excel( self.excelFilePath )
        rawExport.columns = [standardize(column) for column in rawExport.columns]
        rawExport["bib"] = rawExport["bib"].fillna(-1).apply(int)
    
        return(rawExport)
    
    def getEntrantsList( self , data ):
    
        entrants = data[["bib","first_name","last_name","city","state"]].copy()
    
        return(entrants)
    
    def getShirts( self , data ):

        shirtColumns = [c for c in data.columns if "mens" in c]
        nameColumns = ["bib","first_name","last_name"]
        shirts = data[ nameColumns + shirtColumns].copy().fillna(0)

    
        totals = shirts[shirtColumns].sum()
        shirts.loc["totals"] = totals
    
        # clean up
        shirts[shirtColumns] = shirts[shirtColumns].applymap(int)
        shirts[nameColumns] = shirts[nameColumns].fillna("totals")

    
        return(shirts)

    def export( self , path ):
        
        self.shirts.to_csv( path + "shirts.csv")
        self.entrants.to_csv( path + "entrants.csv")        


