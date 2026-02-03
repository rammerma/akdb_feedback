import requests # type: ignore
import json
import pandas as pd # type: ignore
import src.util.util as util
import datetime 

headers = {
  "Authorization" : "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IklPRFJPMmZUOXh2c2ZQblJIdHhJeWZIM1N4OTJJN1RFcnNpM0dxOEd4In0.eyJ1c2VybmFtZSI6InJvbGYuYW1tZXJtYW5uIiwidXVpZCI6IjViNGM1NTBlLWRkODgtNGMwZi05Y2QyLWU1ZGY0MDIxNzI1YiJ9.LgBcyJXxp2IoRafK9aGgmwrF7r76i8JlmGEBZoWhaa6ad_9MxrYf6Sl4Usxb4Rvr_XS2wDJUQwfj5L4__rE56g"
}

# Search Commune    
def searchCommune(url, searchString):
 
    searchCommuneQuery = """
    query SearchCommune($searchString: String!) {
        searchCommune(searchText: $searchString) {
            ags
            name
            domains
            services
        }
    }
    """
    searchCommuneVariables = {"searchString": searchString}

    # HTTP POST-Anfrage an die GraphQL-Schnittstelle
    response = requests.post(
        url,
        json={"query": searchCommuneQuery, "variables": searchCommuneVariables}, headers=headers
    )

    if response.status_code == 200:
        pretty_json = json.dumps(response.json(), indent=4 )
        print('Response JSON:\n', pretty_json)
    
        data = json.loads(pretty_json)
        df = pd.json_normalize(data['data']['searchCommune'])
        df.to_excel('output.xlsx')
    else:
        print(f'Query failed with status code {response.status_code}')
        
# Export complete Feedback
def exportFeedback(url):
    
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

    numberPerPage = 100000
    # Zusätzliche Variablen (wenn notwendig)
    variables = {
        "filter": {
            # "approved" : False,
            # "asc" : True
        },
        "first": numberPerPage
    }
    
    
    dataFrame, pageDataFrame = getFeedbackPage(url,query,variables,headers,numberPerPage)
    print("\nFinal Result to csv:\n\n")
    dataFrame.to_csv("outputFeedbacksComplete.csv", index=False) 
    
    
def getFeedbackPage(url,query,variables,headers,numberPerPage):
    data = util.graphql_post(url,query,variables,headers)
    df = pd.json_normalize(data['data']['feedback']['cursor']['edges'])
    page_df = pd.json_normalize(data['data']['feedback']['cursor']['pageInfo'])
    
    hasNextPage = page_df["hasNextPage"].values[0]
    lastCursorPostion = page_df["endCursor"].values[0]
    print(f'next-page exists= {hasNextPage}, after= {lastCursorPostion}')
        
    #for i in range(numberPerPage):
    df["node.date"] = pd.to_datetime(df["node.createdAt"].astype("float") / 1000, unit='s')
    #print(f'Zeit= {df["node.date"][i]}, AGS={df["node.ags"][i]}, Service={df["node.service"][i]}, Rating={df["node.rating"][i]}')    
    #print(df.head())
    #df.info()
    
    # at_df = df[
    #     (df["node.service"] == "at-erwerbstaetigkeit") |
    #     (df["node.service"] == "at-ausbildung") |
    #     (df["node.service"] == "at-familiennachzug") |
    #     (df["node.service"] == "at-nebenbestimmungen") |
    #     (df["node.service"] == "at-niederlassungserlaubnis") |
    #     (df["node.service"] == "at-beschaeftigungserlaubnis") |
    #     (df["node.service"] == "at-germany-for-ukraine") |
    #     (df["node.service"] == "at-fachkraefteverfahren") |
    #     (df["node.service"] == "aw-aufenthaltskarte") 
    # ]

    
    if hasNextPage:
        variables = {
            "filter": {
                # "approved" : False,
                # "asc" : False
            },
            "first": numberPerPage,
            "after": lastCursorPostion
        }
        next_df, next_page_df = getFeedbackPage(url,query,variables,headers,numberPerPage)
        print("____")
        
        df = pd.concat([df,next_df])
        df.info()

    
                
    return df, page_df
    
    
def exportFeedbackStatistics(url):
    
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
    response = requests.post(
        url,
        json={"query": query, "variables": variables}, headers=headers
    )

    if response.status_code == 200:
        pretty_json = json.dumps(response.json(), indent=4 )
        print('Response JSON:\n', pretty_json)
    
        data = json.loads(pretty_json)
        
        # Beispiel-Datensatz schreiben:
        print('innen:\n', data['data']['systemServices'][0])
        
        
        df = pd.json_normalize(data['data']['systemServices'])
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
        
        at_df.to_excel('feedbackStatistics.xlsx', index=False)
        
    else:
        print(f'Query failed with status code {response.status_code}')
        
def exportActivities(url):
    query = '''
        query Overview {
            activities {
                timestamp
                name
                payload {
                    key
                    value
                }
            }
        }
    '''
    
    variables = {}
    
    response = requests.post(
        url,
        json={"query": query, "variables": variables}, headers=headers
    )

    if response.status_code == 200:
        pretty_json = json.dumps(response.json(), indent=4 )
        print('Response JSON:\n', pretty_json)
    
        data = json.loads(pretty_json)
        df = pd.json_normalize(data['data']['activities'])
        #df["timestamp"] = datetime.datetime.fromtimestamp(df["timestamp"].astype("float")).strftime('%Y-%m-%d %H:%M:%S')
        df["date"] = pd.to_datetime(df["timestamp"].astype("float") / 1000, unit='s')
        print(df.head())
        df.to_excel('activities.xlsx', index=False)
        
    else:
        print(f'Query failed with status code {response.status_code}')