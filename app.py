from flask import Flask,request,make_response
import json
import os
import pandas as pd



app = Flask(__name__)

df_dist=pd.read_csv("covid_india_district.csv")
df_state=pd.read_csv("covid_state.csv")
df_world=pd.read_csv("covid_world.csv")
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
    mail=parameters.get('mail',None)
    code=parameters.get('pincode',None)
    code=parameters.get('pincode',None)


    intent = query_response.get("intent").get('displayName')
    if(intent == 'Covid_World_Stats'):
        cntry_param=query_response.get("queryText")
        cntry_param=query_response.get('parameters',None)
        cntry=parameters.get('country',None)
        state=parameters.get('state',None)
        state=state.replace(" ","")
        wrld_cases = df_world['Total_Cases'].sum(axis=0)
        if(cntry!=''):
            cntry_cases = df_world[df_world['Country'] == cntry].Total_Cases
            cntry_cases = cntry_cases.to_string().split(" ")[4]
            speech="The number of cases in " + cntry + " is " + cntry_cases
        elif(state!=''):
            state_cases = df_state[df_state['State'] == state].Cases
            state_cases = state_cases.to_string().split(" ")[4]
            speech="The number of cases in " + state + " is " + state_cases
        else:
            speech = "Total number of cases all over world " + " is " + str(wrld_cases)

    elif(intent == 'Name'):
        pincode_search = df_pincodes[df_pincodes['pincode'].str.contains(str(code))]
        if(len(pincode_search) != 0):
            dist = df_pincodes[df_pincodes['pincode'] == str(code)].District
            dist= dist.to_string().split(" ")[4]
            dist_cases = df_dist[df_dist['District'] == dist].Cases
            dist_cases = dist_cases.to_string().split(" ")[4]
            speech = "The number of cases in your" + " " + dist+ " district " + "is " + dist_cases + "." + "Would you like to know more about this virus?"

        else:
            speech="Please enter valid pin code"
    elif(intent=='Covid_Stats_Recovered'):
        cntry_param = query_response.get("queryText")
        cntry_param = query_response.get('parameters', None)
        cntry = parameters.get('country', None)
        state = parameters.get('state', None)
        state = state.replace(" ", "")


        wrld_cases = df_world['Recovered'].sum(axis=0)
        if (cntry != ''):
            cntry_cases = df_world[df_world['Country'] == cntry].Recovered
            cntry_cases = cntry_cases.to_string().split(" ")[4]
            speech = "The number of recovery cases in " + cntry + " is " + cntry_cases
        elif (state != ''):
            state_cases = df_state[df_state['State'] == state].Recovered
            state_cases = state_cases.to_string().split(" ")[4]
            speech = "The number of recovery cases in " + state + " is " + state_cases
        else:
            speech = "Total number of recovery cases all over world " + " is " + str(wrld_cases)
    elif (intent == 'Covid_Stats_Death'):
        cntry_param = query_response.get("queryText")
        cntry_param = query_response.get('parameters', None)
        cntry = parameters.get('country', None)
        state = parameters.get('state', None)
        state = state.replace(" ", "")
        wrld_cases = df_world['Deaths'].sum(axis=0)
        if (cntry != ''):
            cntry_cases = df_world[df_world['Country'] == cntry].Deaths
            cntry_cases = cntry_cases.to_string().split(" ")[4]
            speech = "The number of death cases in " + cntry + " is " + cntry_cases
        elif (state != ''):
            state_cases = df_state[df_state['State'] == state].Deaths
            state_cases = state_cases.to_string().split(" ")[4]
            speech = "The number of death cases in " + state + " is " + state_cases
        else:
            speech = "Total number of death cases all over world " + " is " + str(wrld_cases)
    print(speech)
    return {
        "speech": speech,
        "fulfillmentText": speech
    }
if __name__ == "__main__":
    port = int(os.getenv('PORT'))
    print("Starting app on port %d" %(port))
    app.run(debug=False)
