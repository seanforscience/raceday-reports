import pandas as pd

class RaceDay():
    def __init__( self , excelFilePath ):
        
        self.excelFilePath = excelFilePath
        self.data = self.loadExcel()
        
        self.entrants = self.getEntrantsList(self.data)
        self.shirts = self.getShirts(self.data)
        self.emergency = self.getEmergency(self.data)
    
    def loadExcel( self ):

        standardize = lambda text : text.lower().replace("  "," ").replace("  "," ").replace(" ","_")
    
        rawExport = pd.read_excel( self.excelFilePath )
        rawExport.columns = [standardize(column) for column in rawExport.columns]

        # impute blank for missing bibs. fix python autoconvert int-strings to float-strings by lopping off the decimal
        rawExport["bib"] = rawExport["bib"].fillna("").apply(str).apply(lambda x : x.split(".")[0])
    
        return(rawExport)
    
    def getEntrantsList( self , data ):
        '''return list of entrants. I'm worried we might have to do this for a subset of the data in the future, so for now data is an explicit argument.'''    
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

    def getEmergency( self , data ):

        medicalColumns = ["last_name","first_name","bib","age","city","state","emergency_name","emergency_phone","email","phone"]

        medicalColumnDisambiguations = {}
        medicalColumnDisambiguations["phone"] = "runner_phone"
        medicalColumnDisambiguations["email"] = "runner_email"

        medicalData = data[medicalColumns].copy()
        medicalData.columns = [ medicalColumnDisambiguations.get(x,x) for x in medicalData.columns ]

        return(medicalData)



    def export( self , path ):
        
        self.shirts.to_csv( path + "shirts.csv")
        self.entrants.to_csv( path + "entrants.csv")
        self.emergency.to_csv( path + "emergency.csv")


