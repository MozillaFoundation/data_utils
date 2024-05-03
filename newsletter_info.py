import requests
import json
import pandas as pd
import os

class newsletters:

    def __init__(self
                 ,mofo_only = True
                 ,active = True):
        self.mofo_only = mofo_only
        self.active = active
        
        try:
            self.BASKET_URL = os.environ['BASKET_URL']
        except:
            raise Exception('No enviornment variable set for the BASKET_URL, please set this variable.')
    
    def get_newsletters(self, by_lang = False):

        try:
            response = requests.get(self.BASKET_URL + '/news/newsletters/')
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise SystemExit(e)

        if response:
            newsletter = response.json()

        newsletter_slugs = list(newsletter['newsletters'].keys())

        newsletter_list = []
    
        update_slug = [newsletter['newsletters'].get(s).update({'newsletter_slug': s}) for s in newsletter_slugs]

        newsletter_list = list(newsletter.get('newsletters').values())

        newsletters_df = pd.DataFrame(newsletter_list)
        
        if newsletters_df is not None:
            
            final_newsletters = (newsletters_df[((newsletters_df['is_mofo'] == self.mofo_only) 
                                                | (newsletters_df['newsletter_slug'] == 'take-action-for-the-internet')) 
                                                & (newsletters_df['active'] == self.active)]
                                                [['newsletter_slug'
                                                  ,'title'
                                                  ,'description'
                                                  ,'show'
                                                  ,'private'
                                                  ,'indent'
                                                  ,'languages'
                                                  ,'requires_double_optin'
                                                  ,'is_mofo']]
                                                 .copy())
            if by_lang == True:
                langs = [{'newsletter_slug': r['newsletter_slug']
                          ,'language': l} for i, r in final_newsletters.iterrows() for l in r['languages']]

                langs_df = pd.DataFrame(langs)
                return final_newsletters.merge(langs_df, how = 'left', on = 'newsletter_slug').drop(columns = 'languages')
            else:
                return final_newsletters