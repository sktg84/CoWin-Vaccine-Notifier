import requests
from datetime import datetime, timedelta
import time

# EDIT THIS SECTION
age = 36
pincodeMode = False
pincodes = ["600001"]

states = ["Tamil Nadu"]
districts = ["Chennai", "Chengalpet"]
num_days = 2
retry = 1
infiniteLoop = True
#filter_type = ["COVAXIN","COVISHIELD"]
#filter_dose = ["available_capacity_dose1","available_capacity_dose2"]
filter_type = ["COVAXIN"]
filter_dose = ["available_capacity_dose2"]

# DONOT EDIT BEYOND THIS
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
print_flag = 'Y'
districtMap = {}
if (pincodeMode == False):  
    # get district code from the input
    stateList = []
    districtList = []
    URL = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    result = requests.get(URL, headers=header)
    if result.ok:
        response_json = result.json()
        # print (response_json)
        if response_json["states"]:
            for state in response_json["states"]:
                for ipState in states:
                    if (state["state_name"].lower() == ipState.lower()):
                        stateList.append(state["state_id"])
    
    # parse states and district codes
    URL_BASE = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/"
    for stateId in stateList:
        URL = URL_BASE + str(stateId)
        result = requests.get(URL, headers=header)
        if result.ok:
            response_json = result.json()
            if response_json["districts"]:
                for district in response_json["districts"]:
                    for ipDistrict in districts:
                        #print(district["district_name"].lower()+" --> "+ipDistrict.lower())
                        if(district["district_name"].lower() == ipDistrict.lower()):
                            #print("--------Matched------")
                            districtList.append(str(district["district_id"]))
                            districtMap.update({str(district["district_id"]):district["district_name"]})
    
    # overwrite pincodes list with districtList
    pincodes = districtList  
    print("Codes:",pincodes)           

# print (districtList)        
actual = datetime.today()
list_format = [actual + timedelta(days=i) for i in range(num_days)]
actual_dates = [i.strftime("%d-%m-%Y") for i in list_format]

while (retry > 0) or (infiniteLoop == True):
    if (infiniteLoop == False):
        retry = retry - 1
    counter = 0 
    today = datetime.now()
    date_time = today.strftime("%m/%d/%Y, %H:%M:%S")  
    
    print ("INFO: Querying  for Covid vaccine slots as on: " + date_time +" for age <= ",age)
    print (f"INFO: Active filters are -> Vaccine: {filter_type} , Dose: {filter_dose} , Days to check: {num_days} , Loop: {infiniteLoop} ")
    
    
    for pincode in pincodes:   
        for given_date in actual_dates:

            if (pincodeMode == True):
                URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}".format(pincode, given_date)
            else:
                URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(pincode, given_date)
             
            #print (URL)

            print (f'----------- For {districtMap[pincode]} on {given_date}-----------')
            
            result = requests.get(URL, headers=header)
            
            if result.ok:
                response_json = result.json()
                #print (response_json)
                if response_json["centers"]:
                    if(print_flag.lower() == 'y'):
                        for center in response_json["centers"]:
                            for session in center["sessions"]:
                                if (session["min_age_limit"] <= age and session["available_capacity"] > 0 and filter_type.count(session["vaccine"]) > 0 ) :
                                # if (session["min_age_limit"] <= age ) :
                                    dose1mode=False
                                    dose2mode=False
                                    if(filter_dose.count("available_capacity_dose1") > 0):
                                        if(session["available_capacity_dose1"] > 0):
                                            dose1mode = True

                                    if(filter_dose.count("available_capacity_dose2")):
                                        if(session["available_capacity_dose2"] > 0):
                                            dose2mode = True
                                    
                                    if ( dose1mode or dose2mode ):
                                       if (pincodeMode == False):
                                            print ('District:' + districtMap[pincode]) 
                                       else:
                                            print('Pincode: ' + pincode)
                                            print("Available on: {}".format(given_date))
                                    else:
                                        continue
                                    print("\t", center["name"])
                                    print("\t", center["block_name"])
                                    print("\t Fee Type: ", center["fee_type"])
                                    print("\t Availablity : ", session["available_capacity"])
                                    print("\t --- Dose 1  : ",session["available_capacity_dose1"])
                                    print("\t --- Dose 2  : ",session["available_capacity_dose2"])
                                    if(session["vaccine"] != ''):
                                        print("\t Vaccine type: ", session["vaccine"])
                                        if "vaccine_fees" in center:
                                            for fee in center["vaccine_fees"]:
                                                if (fee["vaccine"] == session["vaccine"]):
                                                    print("\t Vaccine Fees: Rs. ", fee["fee"])
                                        
                                                                
                                            # [session["vaccine"]])
                                    print("\n")
                                    counter = counter + 1
            else:
                print("No Response!")
                
    if counter == 0:
        print("No other Vaccination slot(s) available!")
    else:
        for itr in range (1,5):
                print ("\a") #alert bell
                time.sleep(0.5)
        print(f"INFO: Search Completed and found  {counter} vaccine slot(s)!!")
    if (retry > 0) or (infiniteLoop == True):
        print ("INFO: Sleeping.... Auto Wake-up in 3 mins.")
        if (infiniteLoop == False):
            print("INFO: Retries pending : ", retry)
        time.sleep(180)
