import os
import util.akdb as akdb
import util.util as util
import requests # type: ignore
import json
import pandas as pd # type: ignore
import pathlib

class FeedbackData:
    
    def exportAllAuslaenderwesen(self):
        self.exportServiceFeedbackRaw("at-erwerbstaetigkeit")
        self.exportServiceFeedbackRaw("at-ausbildung")
        self.exportServiceFeedbackRaw("at-familiennachzug")
        self.exportServiceFeedbackRaw("at-nebenbestimmungen")
        self.exportServiceFeedbackRaw("at-niederlassungserlaubnis")
        self.exportServiceFeedbackRaw("aw-beschaeftigungserlaubnis")
        self.exportServiceFeedbackRaw("at-germany-for-ukraine")
        self.exportServiceFeedbackRaw("at-fachkraefteverfahren")
        self.exportServiceFeedbackRaw("aw-aufenthaltskarte")
        self.exportServiceFeedbackRaw("at-humanitaere-gruende")
        

    def exportServiceFeedbackRaw(self,pService):
        print(f"Moin Ausländerwesen Raw: {akdb.urlV2}")
        
        # Die GraphQL-Abfrage
        query = """
            query ServiceFeedback(
                $service: String!, 
                $filter: FeedbackFilter!, 
                $after: String, 
                $first: Int, 
                $before: String, 
                $last: Int) {
            service(id: $service) {
                feedback(filter: $filter) {
                cursor(after: $after, first: $first, before: $before, last: $last) {
                    edges {
                    node {
                        communeName
                        ags
                        text
                        rating
                        language
                        createdAt
                        approved
                    }
                    cursor
                    }
                    pageInfo {
                    startCursor
                    endCursor
                    hasPreviousPage
                    hasNextPage
                    __typename
                    }
                    __typename
                }
                __typename
                }
                __typename
            }
            }
        """
        
        numberPerPage = 10000
        # Zusätzliche Variablen (wenn notwendig)
        variables = {
            "service": pService,
            "filter": {
                # "approved" : False,
                "withComment" : True,
                "asc" : False,
                "sortBy": "DATE"
            },
            "first": numberPerPage
        }
        
        dataFrame, pageDataFrame = self.getServiceFeedbackPage(query, variables, numberPerPage)
        
        # Optimierung der Ausgabe:
        dataFrame["node.date"] = pd.to_datetime(dataFrame["node.createdAt"].astype("float")/1000, unit='s')
        dataFrame["node.ratingCalc"] = (dataFrame["node.rating"] // 50) + 3
        dataFrame = dataFrame.fillna('NULL')
        dataFrame = dataFrame[
            (dataFrame["node.rating"] != 0) &
            (dataFrame["node.rating"] != 1) &
            (dataFrame["node.rating"] != -1)
        ]
        dataFrame["node.text"] = dataFrame["node.text"].str.replace('\n', ' ', regex=False)

        dataFrame.columns = ["cursor","commune","ags","text","rating","language","createdAt","approved","date","ratingcalc"]
        print(dataFrame.head())
        
        # Ausgabe in Excel
        output_dir = pathlib.Path(__file__).parents[2] / 'output'
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, f"outputFeedbacksAuslaenderwesen_{variables['service']}.xlsx")
        dataFrame.to_excel(output_filename, index=False)

        
    def getServiceFeedbackPage(self, query, variables, numberPerPage):
        json_data = util.graphql_post(akdb.urlV2, query, variables, akdb.headers)
        if json_data is None: 
            print("json_data is None - keine Daten aus GraphQL-Request...")
            return pd.DataFrame()
        
        df = pd.json_normalize(json_data['data']['service']['feedback']['cursor']['edges'])
        page_df = pd.json_normalize(json_data['data']['service']['feedback']['cursor']['pageInfo'])
        
        hasNextPage = page_df["hasNextPage"].values[0]
        lastCursorPostion = page_df["endCursor"].values[0]
        print(f'next-page exists= {hasNextPage}, after= {lastCursorPostion}')    

        next_df = pd.DataFrame()
        if hasNextPage:
            variables["first"] = numberPerPage
            variables["after"] = lastCursorPostion
            
            try:
                next_df, next_page_df = self.getServiceFeedbackPage(query, variables, numberPerPage)
            except TypeError as e:
                print(f"TypeError aufgetreten: {e}")
                print(f"Fehlertyp: {type(e).__name__}")
                print(f"Fehler TypeError: {variables} ")
            print("____")
            
            df = pd.concat([df, next_df])
            #df.info()
                    
        return df, page_df

    def exportRaw(self):
        print(f"Moin Raw: {akdb.urlV2}")
            
        # Die GraphQL-Abfrage
        query = """
            query Feedback(
                $filter: FeedbackFilter!
                $after: String
                $before: String
                $first: Int
                $last: Int
            ) {
                feedback(filter: $filter) {
                    cursor(after: $after, before: $before, first: $first, last: $last) {
                        edges {
                            node {
                                service
                                ags
                                communeName
                                rating
                                text
                                createdAt
                            }
                            cursor
                        }
                        pageInfo {
                            startCursor
                            endCursor
                            hasPreviousPage
                            hasNextPage
                        }
                    }
                }
            }

            """

        numberPerPage = 10000
        # Zusätzliche Variablen (wenn notwendig)
        variables = {
            "filter": {
                # "approved" : False,
                "asc" : False
            },
            "first": numberPerPage
        }

        dataFrame, pageDataFrame = self.getFeedbackPage(query,variables,numberPerPage)
        
        # Optimierung der Ausgabe:
        dataFrame["node.date"] = pd.to_datetime(dataFrame["node.createdAt"].astype("float")/1000, unit='s')
        dataFrame["node.ratingCalc"] = (dataFrame["node.rating"] // 50) + 3
        dataFrame = dataFrame.fillna('NULL')
        dataFrame = dataFrame[
            (dataFrame["node.rating"] != 0) &
             (dataFrame["node.rating"] != 1) &
             (dataFrame["node.rating"] != -1)
        ]
        dataFrame["node.text"] = dataFrame["node.text"].str.replace('\n', ' ', regex=False)
        
        # Spaltenüberschriften
        dataFrame.columns = ["cursor","service","ags","commune","rating","text","createdAt","date","ratingcalc"]
        
        # Ausgabe in CSV
        print("\nFinal Result to csv:\n\n")
        dataFrame.info()
        dataFrame.to_csv("outputFeedbacksComplete.csv", index=False) 
        
        return None
    
    def getFeedbackPage(self,query,variables,numberPerPage):
        json_data = util.graphql_post(akdb.urlV2,query,variables,akdb.headers)
        if json_data is None: 
            print("json_data is None - keine Daten aus GraphQL-Request...")
            return pd.DataFrame()
        
        df = pd.json_normalize(json_data['data']['feedback']['cursor']['edges'])
        page_df = pd.json_normalize(json_data['data']['feedback']['cursor']['pageInfo'])
        
        hasNextPage = page_df["hasNextPage"].values[0]
        lastCursorPostion = page_df["endCursor"].values[0]
        print(f'next-page exists= {hasNextPage}, after= {lastCursorPostion}')    


        next_df = pd.DataFrame()
        if hasNextPage:
            variables = {
                "filter": {
                    # "approved" : False,
                    "asc" : False
                },
                "first": numberPerPage,
                "after": lastCursorPostion
            }
            try:
                next_df, next_page_df = self.getFeedbackPage(query,variables,numberPerPage)
            except TypeError as e:
                print(f"TypeError aufgetreten: {e}")
                print(f"Fehlertyp: {type(e).__name__}")
                print(f"Fehler TypeError: {variables} ")
            print("____")
            
            df = pd.concat([df,next_df])
            df.info()
                    
        return df, page_df


    
    def exportStatistic(self):
        print(f"Moin Statistic: {akdb.urlV1}")
        
        query = '''
            query SystemServices {
                systemServices {
                    id
                    name
                    avgFeedback
                    countFeedback
                }
            }
        '''
    
        variables = {}
        
        # HTTP POST-Anfrage an die GraphQL-Schnittstelle
        json_data = util.graphql_post(akdb.urlV1,query,variables,akdb.headers)

        if json_data is not None:
            
            # Beispiel-Datensatz schreiben:
            print('innen:\n', json_data['data']['systemServices'][0])
            
            
            df = pd.json_normalize(json_data['data']['systemServices'])
            df["avgFeedback"] = round((df["avgFeedback"] / 50) + 3 ,2)
            
            #df.to_excel('output.xlsx')
            print(df.head())
            # print(df["avgFeedback"].mean())
            # print(df["countFeedback"].sum())
            
            # at_df = df
            at_df = df[
                (df["id"] == "at-erwerbstaetigkeit") |
                (df["id"] == "at-ausbildung") |
                (df["id"] == "at-familiennachzug") |
                (df["id"] == "at-nebenbestimmungen") |
                (df["id"] == "at-niederlassungserlaubnis") |
                (df["id"] == "at-beschaeftigungserlaubnis") |
                (df["id"] == "at-germany-for-ukraine") |
                (df["id"] == "at-fachkraefteverfahren") |
                (df["id"] == "aw-aufenthaltskarte") |
                (df["id"] == "aw-beschaeftigungserlaubnis") |
                (df["id"] == "aw-rueckkanal-antwort") 
            ]
            print(at_df)
            
            durchschnitt = round(at_df["avgFeedback"].mean(), 2)
            summe = at_df["countFeedback"].sum()
            
            result_row = pd.DataFrame([['Durchschnitt', '', durchschnitt,summe]], columns=df.columns)
            at_df = pd.concat([at_df, result_row], ignore_index=True)
            
            output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'feedbackStatistics.xlsx')
            at_df.to_excel(output_file, index=False)
            
        else:
            print(f'Query failed')        
            
        return None
