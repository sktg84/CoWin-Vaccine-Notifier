'''
Script: Covid Vaccine Slot Availability Notifier
By Ayushi Rawat, Extended by: Karthik Subramanian
'''
import requests
from datetime import datetime, timedelta
import time

#EDIT THIS SECTION
age = 50
pincodeMode=False
#{"districts":[{"district_id":779,"district_name":"Aranthangi"},{"district_id":555,"district_name":"Ariyalur"},{"district_id":578,"district_name":"Attur"},{"district_id":565,"district_name":"Chengalpet"},{"district_id":571,"district_name":"Chennai"},{"district_id":778,"district_name":"Cheyyar"},{"district_id":539,"district_name":"Coimbatore"},{"district_id":547,"district_name":"Cuddalore"},{"district_id":566,"district_name":"Dharmapuri"},{"district_id":556,"district_name":"Dindigul"},{"district_id":563,"district_name":"Erode"},{"district_id":552,"district_name":"Kallakurichi"},{"district_id":557,"district_name":"Kanchipuram"},{"district_id":544,"district_name":"Kanyakumari"},{"district_id":559,"district_name":"Karur"},{"district_id":780,"district_name":"Kovilpatti"},{"district_id":562,"district_name":"Krishnagiri"},{"district_id":540,"district_name":"Madurai"},{"district_id":576,"district_name":"Nagapattinam"},{"district_id":558,"district_name":"Namakkal"},{"district_id":577,"district_name":"Nilgiris"},{"district_id":564,"district_name":"Palani"},{"district_id":573,"district_name":"Paramakudi"},{"district_id":570,"district_name":"Perambalur"},{"district_id":575,"district_name":"Poonamallee"},{"district_id":546,"district_name":"Pudukkottai"},{"district_id":567,"district_name":"Ramanathapuram"},{"district_id":781,"district_name":"Ranipet"},{"district_id":545,"district_name":"Salem"},{"district_id":561,"district_name":"Sivaganga"},{"district_id":580,"district_name":"Sivakasi"},{"district_id":551,"district_name":"Tenkasi"},{"district_id":541,"district_name":"Thanjavur"},{"district_id":569,"district_name":"Theni"},{"district_id":554,"district_name":"Thoothukudi (Tuticorin)"},{"district_id":560,"district_name":"Tiruchirappalli"},{"district_id":548,"district_name":"Tirunelveli"},{"district_id":550,"district_name":"Tirupattur"},{"district_id":568,"district_name":"Tiruppur"},{"district_id":572,"district_name":"Tiruvallur"},{"district_id":553,"district_name":"Tiruvannamalai"},{"district_id":574,"district_name":"Tiruvarur"},{"district_id":543,"district_name":"Vellore"},{"district_id":542,"district_name":"Viluppuram"},{"district_id":549,"district_name":"Virudhunagar"}],"ttl":24}
pincodes = ["600064"]
#pincodes = ["571"]
states=["Tamil Nadu"]
districts=["Chennai","Chengalpet"]
num_days = 2
retry = 1
infiniteLoop= False

#DONOT EDIT BEYOND THIS
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
print_flag = 'Y'
districtMap={}
if (pincodeMode == False):  
    #get district code from the input
    stateList=[]
    districtList=[]
    URL = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    result = requests.get(URL, headers=header)
    if result.ok:
        response_json = result.json()
        #print (response_json)
        if response_json["states"]:
            for state in response_json["states"]:
                for ipState in states:
                    if (state["state_name"].lower() == ipState.lower()):
                        stateList.append(state["state_id"])
    
    #parse states and district codes
    URL_BASE = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/"
    for stateId in stateList:
        URL = URL_BASE+str(stateId)
        result = requests.get(URL, headers=header)
        if result.ok:
            response_json = result.json()
            if response_json["districts"]:
                for district in response_json["districts"]:
                    for ipDistrict in districts:
                        if(district["district_name"].lower() == ipDistrict.lower()):
                            districtList.append(str(district["district_id"]))
                            districtMap.update({str(district["district_id"]):district["district_name"]})
    
    #overwrite pincodes list with districtList
    pincodes = districtList             

#print (districtList)        
actual = datetime.today()
list_format = [actual + timedelta(days=i) for i in range(num_days)]
actual_dates = [i.strftime("%d-%m-%Y") for i in list_format]

while (retry > 0) or (infiniteLoop == True ):
    if (infiniteLoop == False ):
        retry = retry - 1 ;
    counter = 0 
    today = datetime.now()
    date_time = today.strftime("%m/%d/%Y, %H:%M:%S")  
    
    print ("INFO: Querying  for Covid vaccine slots >>> "+date_time)
    
    for pincode in pincodes:   
        for given_date in actual_dates:

            if (pincodeMode == True):
                URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}".format(pincode, given_date)
            else:
                URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(pincode, given_date)
             
            
            result = requests.get(URL, headers=header)
            
            if result.ok:
                response_json = result.json()
                #print (response_json)
                if response_json["centers"]:
                    if(print_flag.lower() =='y'):
                        for center in response_json["centers"]:
                            for session in center["sessions"]:
                                if (session["min_age_limit"] <= age and session["available_capacity"] > 0 ) :
                                #if (session["min_age_limit"] <= age ) :
                                    if (pincodeMode == False):
                                        print ('District:' + districtMap[pincode]) 
                                    else:
                                        print('Pincode: ' + pincode)
                                    print("Available on: {}".format(given_date))
                                    print("\t", center["name"])
                                    print("\t", center["block_name"])
                                    print("\t Fee Type: ", center["fee_type"])
                                    print("\t Availablity : ", session["available_capacity"])

                                    if(session["vaccine"] != ''):
                                        print("\t Vaccine type: ", session["vaccine"])
                                        if "vaccine_fees" in center:
                                            for fee in center["vaccine_fees"]:
                                                if (fee["vaccine"] == session["vaccine"]):
                                                    print("\t Vaccine Fees: Rs. ",fee["fee"])
                                        
                                                                
                                            #[session["vaccine"]])
                                    print("\n")
                                    counter = counter + 1
            else:
                print("No Response!")
                
    if counter == 0:
        print("No other Vaccination slot(s) available!")
    else:
        print('\a')
        print("INFO: Search Completed and found vaccine slots!!")
    if (retry > 0) or (infiniteLoop == True ):
        print ("INFO: Sleeping.... Auto Wake-up in 3 mins.")
        if (infiniteLoop == False ):
            print("INFO: Retries pending : ",retry)
        time.sleep(180)
