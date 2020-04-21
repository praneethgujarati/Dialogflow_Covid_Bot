from flask import Flask,request,make_response
import json
import os
from Send_Email import EmailSender
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


app = Flask(__name__)

df_dist=pd.read_csv("covid_india_district.csv")
df_state=pd.read_csv("covid_state_new.csv")
df_world=pd.read_csv("Covid_World_2104.csv")
df_pincodes=pd.read_excel("pincodes_data.xlsx")
df_pincodes['pincode'] = df_pincodes['pincode'].astype(str)



@app.route('/webhook',methods=['POST'])

def webhook():
    if request.method == 'POST':
        req = request.get_json(silent=True, force=True)
        res = makeWebhookResult(req)
        res = json.dumps(res,indent=True)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        return r

def makeWebhookResult(req):
    query_response=req['queryResult']
    user_says_name = query_response.get("queryText")
    parameters=query_response.get('parameters',None)
    name=parameters.get('name',None)
    code=parameters.get('pincode',None)


    intent = query_response.get("intent").get('displayName')
    if(intent == 'Covid_World_Stats'or intent=='Covid_World_Stats - custom'):
        cntry_param=query_response.get("queryText")
        cntry_param=query_response.get('parameters',None)
        cntry=parameters.get('country',None)
        state=parameters.get('state',None)
        state=state.replace(" ","")
        city=parameters.get('city',None)
        wrld_cases_total = str(df_world['Total_Cases'].astype(int).sum(axis=0))
        wrld_cases_deaths = str(df_world['Deaths'].astype(int).sum(axis=0))
        wrld_cases_rec = str(df_world['Recovered'].astype(int).sum(axis=0))
        wrld_cases_act = str(df_world['Active_Cases'].astype(int).sum(axis=0))
        wrld_cases_new = str(df_world['New_Cases'].astype(int).sum(axis=0))
        wrld_cases_new_deaths = str(df_world['New_Deaths'].astype(int).sum(axis=0))
        if (cntry != ''):
            cntry_cases = df_world[df_world['Country'] == cntry]
            cntry_cases = cntry_cases.to_dict('index')
            cntry_cases = [str(j) + ":" + str(k) for i in cntry_cases for j, k in cntry_cases[i].items()]
            cntry_cases = str(cntry_cases).replace("[", "").replace("]", "").replace("'", "")
            speech = cntry_cases
        elif (state != ''):
            state_search = df_state[df_state['State'].str.contains(state)]
            if (len(state_search) != 0):
                state_cases = df_state[df_state['State'] == state]
                state_cases = state_cases.to_dict('index')
                state_cases = [str(j) + ":" + str(k) for i in state_cases for j, k in state_cases[i].items()]
                state_cases = str(state_cases).replace("[", "").replace("]", "").replace("'", "")
                speech = state_cases
            else:
                speech = "Please enter any of India's States!"
        elif(city == ''):
            speech = "World-Wide Statistics, " + "Total_Cases:" + wrld_cases_total + " ," + "Total_Deaths:" + wrld_cases_deaths + " ," + "Total_Recovered:" + wrld_cases_rec + " ," + "Total_Active_Cases:" + wrld_cases_act + " ," + "New_Cases:" + wrld_cases_new + " ," + "New_Deaths:" + wrld_cases_new_deaths
        else:
            speech = "I'm here to provide covid-19 statistics country-wise and state-wise!Please ask related to it"


    elif(intent == 'Name' or intent == 'Name - custom'):
        pincode_search = df_pincodes[df_pincodes['pincode'].str.contains(str(code))]
        if(len(pincode_search) != 0):
            dist = df_pincodes[df_pincodes['pincode'] == str(code)].District
            dist= dist.to_string().split(" ")[4]
            dist_cases = df_dist[df_dist['District'] == dist].Cases
            dist_cases = dist_cases.to_string().split(" ")[4]
            speech = "The number of cases in your" + " " + dist+ " district " + "is " + dist_cases + "." + "Would you like to know more about the covid-19 cases?"

        else:
            speech="Please enter valid any of India's pin code"
    elif(intent == 'Summary'):
        smry_param = query_response.get("queryText")
        smry_param = query_response.get('parameters', None)
        smry = parameters.get('summary', None)
        if(smry == 'states'):
            cnt_states = df_state.shape[0]
            state_aff_most = df_state.iloc[df_state['Confirmed'].argmax()]
            state_aff_most = state_aff_most['State']
            speech = "The number of states affected with corona virus in India is " + str(cnt_states) + "." + "The state with most cases is " + state_aff_most
        else:
            cnt_cntries = df_world.shape[0]
            cntry_aff_most = df_world.iloc[df_world['Total_Cases'].argmax()]
            cntry_aff_most = cntry_aff_most['Country']
            speech = "The number of countries impacted all over the world is " + str(cnt_cntries)+ "." + "The country with most cases is " + cntry_aff_most
    print(speech)
    return {
        "speech": speech,
        "fulfillmentText": speech
    }
if __name__ == "__main__":
    port = int(os.getenv('PORT'))
    print("Starting app on port %d" %(port))
    app.run(debug=False)
