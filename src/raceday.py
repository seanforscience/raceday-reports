import re
import pandas as pd

class RaceDay():
    def __init__( self , excelFilePath ):
        
        self.excelFilePath = excelFilePath
        self.data = self.loadExcel()

        self.runner_id_columns = ["bib","first_name","last_name","city","state"]
        
        self.entrants = self.getEntrantsList(self.data)
        self.runnerSwag = self.getSwagList(self.data)
        self.swagTotals = self.getSwagTotals(self.data)
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
        entrants = data[self.runner_id_columns].copy()

        return(entrants)
    
    def getSwag( self , data ):

        # identify purchased items by price in the column name.
        shirtColumns = [c for c in data.columns if len(re.findall("[0-9][0-9].[0-9][0-9]",c)) > 0]
        
        shirts = data[ self.runner_id_columns + shirtColumns ].copy().fillna(0)

        totals = shirts[shirtColumns].sum()
        shirts.loc["totals"] = totals
    
        # clean up
        shirts[shirtColumns] = shirts[shirtColumns].applymap(int)
        shirts[self.runner_id_columns] = shirts[self.runner_id_columns].fillna("totals")


        # some helper functions for organizing swag into a list

        def imputeMe( field , trueValue , falseValue ):
            '''A little helper function.'''
            output = falseValue
            if field:
                output = trueValue
            return(output)

        def getSwagAsList( swagData , swagColumns ):
            swag = swagData[swagColumns].applymap(bool).copy()
            for item in swagColumns:
                swag[item] = swag[item].apply(lambda x : imputeMe(x,item,""))

            # concat items into list, remove blanks, convert list to string
            swag = swag.apply(list,axis=1).apply(lambda x : ",".join([c for c in x if c != ""]))
            return(swag)


        # append Swag List

        shirts["swag_list"] = getSwagAsList( shirts, shirtColumns )
        
        return(shirts)

    def getSwagList( self , data ):
        ''' Simple Swag export for the checkin staff'''
        swag = self.getSwag(data)
        output = swag[ self.runner_id_columns + ["swag_list"]]

        # remove totals
        output = output.loc[[i for i in output.index if i != "totals"]]
        return(output)

    def getSwagTotals( self , data ):
        ''' total of all swag requirements for race merch staff'''
        swag = self.getSwag(data)
        return(swag.loc[["totals"]])


    def getEmergency( self , data ):

        medicalColumns = self.runner_id_columns + ["age","emergency_name","emergency_phone","email","phone","any_medical_conditions_we_should_know_about"]

        medicalColumnDisambiguations = {}
        medicalColumnDisambiguations["phone"] = "runner_phone"
        medicalColumnDisambiguations["email"] = "runner_email"
        medicalColumnDisambiguations["any_medical_conditions_we_should_know_about"] = "medical_conditions"

        medicalData = data[medicalColumns].copy()
        medicalData.columns = [ medicalColumnDisambiguations.get(x,x) for x in medicalData.columns ]

        return(medicalData)



    def export( self , path ):
        
        def exportFile( data , name ):
            data.to_csv( path + name + ".csv" , index = None )

        exportFile( self.runnerSwag , "runner_swag" )
        exportFile( self.swagTotals , "swag_totals" )
        exportFile( self.entrants , "entrants" )
        exportFile( self.emergency , "emergency" )


