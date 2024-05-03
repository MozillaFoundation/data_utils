import pandas as pd
import os
from simple_salesforce import Salesforce
from simple_salesforce.format import format_soql
import requests

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