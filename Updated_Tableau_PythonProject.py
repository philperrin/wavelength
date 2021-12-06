# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 16:07:01 2021

@author: Jealyn
"""
import tableauserverclient as TSC
import pandas as pd
from datetime import date
slack_users = pd.read_excel(r'slack user ids.xlsx', sheet_name='Assignments')

# Signing into the corresponding Tableau Server
tableau_token = TSC.PersonalAccessTokenAuth('Python Project',
                'Y5Erq6dORA65IO4hSUdt6A==:6fuJtMdRGUMti8kJzjHTvHik2klzxHq6',
                site_id = 'tessellationhq')
tess_server = TSC.Server('https://prod-useast-b.online.tableau.com/',
                         use_server_version= True)
tess_server.auth.sign_in(tableau_token)

# Looking at all the views in Tableau along with their IDs
with tess_server.auth.sign_in(tableau_token):
    for view in TSC.Pager(tess_server.views):
        print(view.name)
        print(view.id)
        
# Getting the correct view image from tableau that is needed from this project
with tess_server.auth.sign_in(tableau_token):
    utilization = tess_server.views\
    .get_by_id('5c41cd96-6263-447f-93c9-1cba0cb56348')
    print(utilization.name)
    tess_server.views.populate_image(utilization)
    with open('./utilization_image.png','wb') as v:
        v.write(utilization.image)
    
#%% Changing script to have for loop 
employees = slack_users.loc[slack_users['Include'] == True, 'UserID']
view_id = '5c41cd96-6263-447f-93c9-1cba0cb56348'

def utilization():
    utilization_image_options = TSC.ImageRequestOptions(imageresolution = 
                            TSC.ImageRequestOptions.Resolution.High, maxage=1) 
    for i in employees:
        utilization_image_options.vf('SlackID', (i))
        with tess_server.auth.sign_in(tableau_token):
            utilization = tess_server.views\
                    .get_by_id(view_id)
        tess_server.views.populate_image(utilization, utilization_image_options)
        with open ('{}.png'.format(i), 'wb') as m:
            m.write(utilization.image)

def employee():
    individual_image_options = TSC.ImageRequestOptions(imageresolution = 
                        TSC.ImageRequestOptions.Resolution.High, maxage=1)
    individual_image_options.vf('SlackID', employees[18])
    with tess_server.auth.sign_in(tableau_token):
        utilization = tess_server.views\
                    .get_by_id(view_id)
        tess_server.views.populate_image(utilization, individual_image_options)
        with open('{}.png'.format(employees[18]), 'wb') as n:
            n.write(utilization.image)

# Creating a condition to show that if it's Monday, then it will run the for
# loop, but if not, then it will run the other portion of the script.
if date.today().weekday() == 0:
    utilization()
if date.today().weekday() != 0:
    employee()