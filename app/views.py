from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import time
import random
import requests
from concurrent import futures

CALLBACK_URL = "http://localhost:8000/async"
AUTH_KEY = "secret-async-resources"

executor = futures.ThreadPoolExecutor(max_workers=1)

def get_random_fact(report_ref, resource_ref):
    time.sleep(5)
    return {
        "report_ref": report_ref,
        "resource_ref": resource_ref,
        "fact": random.randint(1, 100),
    }

def status_callback(task):
    try:
        result = task.result()
        print(result)
    except futures._base.CancelledError:
        return
    
    nurl = str(CALLBACK_URL + "/" + str(result["report_ref"]) + "/" + str(result["resource_ref"]))
    print(nurl)
    answer = {"report_ref": result["report_ref"], 
              "resource_ref": result["resource_ref"], 
              "fact": result["fact"]}
    
    requests.post(nurl, json=answer, timeout=3)

@api_view(['POST'])
def set_plan(request):
    if "Authorization" not in request.headers or request.headers["Authorization"] != AUTH_KEY:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if ("report_ref" and "resource_ref") in request.data.keys():   
        report_ref = request.data["report_ref"]    
        resource_ref = request.data["resource_ref"]    

        print(report_ref, resource_ref)

        task = executor.submit(get_random_fact, report_ref, resource_ref)
        task.add_done_callback(status_callback)        
        return Response(status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)