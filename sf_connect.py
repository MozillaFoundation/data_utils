import pandas as pd
import os
from simple_salesforce import Salesforce
from simple_salesforce import bulk2
from simple_salesforce.format import format_soql
import requests
import re
import csv
from datetime import date, datetime
from numpy import float64, int64

#Salesforce reference of data types 
#https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/field_types.htm
DTYPE_MAPPER = {'string': str
                ,'double': float64
                ,'boolean': bool
                ,'textarea': str
                ,'date': date
                ,'datetime': datetime
                ,'id': str
                ,'masterrecord': str
                ,'reference': str
                ,'email': str
                ,'picklist': str
                ,'phone': str
                ,'percent': float64
                ,'location': str
                ,'currency': str
                ,'address': str}

class sf_connect:
    def __init__(self):
        
        #Create the tuple of environment variables to search for
        env_vars = ('SALESFORCE_INSTANCE_URL'
                    ,'SALESFORCE_API_USER'
                    ,'SALESFORCE_API_PASS'
                    ,'SALESFORCE_API_TOKEN')
        
        #Create an empty dict for the credentials
        credentials = {}
        
        #Loop through the evironment variables and add them to the credential dict if they exist
        #otherwise raise an exception.
        for e in env_vars:
            try:
                credentials.update({e: os.environ[e]})
            except:
                raise Exception('Environment Variable {} does not exist, please set this value.'.format(e))
        
        #Set the credentials of the class
        self.__credentials = credentials
        
        #Connect to Salesforce using the credentials from above
        self.salesforce = Salesforce(instance = self.__credentials.get('SALESFORCE_INSTANCE_URL')
                                    ,username = self.__credentials.get('SALESFORCE_API_USER')
                                    ,password = self.__credentials.get('SALESFORCE_API_PASS')
                                    ,security_token = self.__credentials.get('SALESFORCE_API_TOKEN')
                                    ,session_id = requests.Session())
    
    #Create the method to run a SOQL query against the Salesforce connection
    def sf_query_to_df(self, query):
        try:
            #If the query string was provided then execute the query
            if query:
                query = format_soql(query)
                query_results = self.salesforce.query_all(query)
            
            #Otherwise raise an exception
            else:
                raise Exception('The value of query cannot be null')
            
            #If query results were retrieved transform the dictionary into a dataframe
            if query_results:
                results_df = (pd.DataFrame([r for r in query_results.get('records')])
                                          .drop(columns = 'attributes'))
            #Return the dataframe
            return results_df
        
        #Otherwise raise any exceptions from the Salesforce class or otherwise
        except Exception as e:
            raise(e)
        
    def get_sf_object(self, query):
        if query:
            query = format_soql(query)

            #Create the search expression: the "from" statement, with spaces and at least one of any letter or digit.
            #The purpose is to extract the Salesforce Object
            search_object = re.compile('from\s{1,}\w{1,}(\s{0,}|$)', re.IGNORECASE)
            
            #Create the replacement expression, we want to replace the from and any space characters
            replace = re.compile('(from|\s)', re.IGNORECASE)

            #Search the input query
            result = re.search(search_object, query)

            try:
                #Replace the strings to only get the object.
                self.sf_object = re.sub(replace, '', result[0])
                #Return the salesforce object.
                #return sf_object
            except:
                raise Exception('No salesforce object found in query. The result is empty, please check your query')
            
    def sf_object_dtypes(self, query):
        self.get_sf_object(query)

        #Create a dict of column names and the salesforce data types
        from_dtypes = {c.get('name'): c.get('type') for c in self.salesforce.__getattr__(self.sf_object).describe().get('fields')}

        #Map these data types to the appropriate pandas data types
        self.to_dtypes = {k: DTYPE_MAPPER.get(v) for k,v in from_dtypes.items()}
        #return to_dtypes
    
    def sf_query_object(self, query):
        
        self.get_sf_object(query)

        self.api_object = self.salesforce.__getattr__(self.sf_object)
        self.bulk2_object = self.salesforce.bulk2.__getattr__(self.sf_object)

        #Create a dict of column names and the salesforce data types
        from_dtypes = {c.get('name'): c.get('type') for c in self.api_object.describe().get('fields')}

        #Connect to the object via bulk2
        results = self.bulk2_object.query(query)


        csv_data = [r for r in results]

        df_list = []

        #Iterate through the list of lists
        for c in csv_data:
            #Split each list by the newline characters
            newline_split = c.split('\n')
            #Create a csv reader for all rows except the header, explicitly delimit by a comma
            reader = csv.reader(newline_split[1:], delimiter = ',')
            #Create a csv reader for only the header, explicitly delimit by a comma
            col_reader = csv.reader([newline_split[0]], delimiter = ',')
            #Append a dataframe with the values and columns to the df_list
            df_list.append(pd.DataFrame([row for row in reader if row], columns = [c for c in col_reader]))
        
        #Concatenate the df_list
        self.data = pd.concat(df_list)

        #Map these data types to the appropriate pandas data types
        self.to_dtypes = {k: DTYPE_MAPPER.get(v) for k,v in from_dtypes.items() if k in self.data.columns}

        #return data