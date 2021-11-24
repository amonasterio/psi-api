import time, urllib.request, json, pandas as pd, sys
from urllib.error import HTTPError

'''
Script que devuelve un csv con los datos más importantes tras hacer una llamada a la API de PSI
Pasamos 3 parámetros:
    API_KEY de PSI para evitar que nos baneen
    Fichero csv de entrada con todas las URL que queremos analizar. La primera línea debe contener el texto 'url'
    Fichero csv de salida con todos los datos
'''


# Validamos que se han pasado todos los parámetros necesarios
if len(sys.argv) == 4:
    api_key=sys.argv[1]
    fichero_entrada=sys.argv[2]
    fichero_salida=sys.argv[3]
   
    try:
        crawldf = pd.read_csv(fichero_entrada) 
        addresses = crawldf['url'].tolist()

        dispositivos=['mobile','desktop']
        dct_arr=[]
        try:
            for row in addresses:
                analiza=row
                for dispo in dispositivos:
                    url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url="+analiza+"&key="+api_key+"&strategy="+dispo+"&locale=es"
                    
                    response = urllib.request.urlopen(url)

                    data = json.loads(response.read())  
                    print(url)
                    print(data["loadingExperience"]["metrics"].values())
                    psi_dict={}
                    psi_dict['url']=data["lighthouseResult"]["finalUrl"]
                    psi_dict['dispositivo']=dispo
                    psi_dict['score'] = data["lighthouseResult"]["categories"]["performance"]["score"]
                    psi_dict['fcp_chrux (ms)'] =data["loadingExperience"]["metrics"]["FIRST_CONTENTFUL_PAINT_MS"]["percentile"] #into seconds (/1000)
                    psi_dict['fcp_chrux_score'] = data["loadingExperience"]["metrics"]["FIRST_CONTENTFUL_PAINT_MS"]["category"]
                    if  data["loadingExperience"]["metrics"].get("FIRST_INPUT_DELAY_MS") != None:
                        psi_dict['fid_chrux (ms)'] = data["loadingExperience"]["metrics"]["FIRST_INPUT_DELAY_MS"]["percentile"] #into seconds (/1000)
                        psi_dict['fid_chrux_score'] = data["loadingExperience"]["metrics"]["FIRST_INPUT_DELAY_MS"]["category"]
                    else:
                         psi_dict['fid_chrux (ms)'] ="-"
                         psi_dict['fid_chrux_score'] = "-"
                    psi_dict['lcp_chrux (ms)'] = data["loadingExperience"]["metrics"]["LARGEST_CONTENTFUL_PAINT_MS"]["percentile"]
                    psi_dict['lcp_chrux_score'] = data["loadingExperience"]["metrics"]["LARGEST_CONTENTFUL_PAINT_MS"]["category"]
                    psi_dict['cls_chrux'] = data["loadingExperience"]["metrics"]["CUMULATIVE_LAYOUT_SHIFT_SCORE"]["percentile"]/100
                    psi_dict['cls_chrux_score'] = data["loadingExperience"]["metrics"]["CUMULATIVE_LAYOUT_SHIFT_SCORE"]["category"]
                    
                    
                    psi_dict['fcp_lighthouse (ms)'] =data["lighthouseResult"]["audits"]["first-contentful-paint"]["numericValue"] #into seconds (/1000)
                    psi_dict['fcp_lighthouse_score'] =data["lighthouseResult"]["audits"]["first-contentful-paint"]["score"] 
                    psi_dict['lcp_lighthouse (ms)'] =data["lighthouseResult"]["audits"]["largest-contentful-paint"]["numericValue"] 
                    psi_dict['lcp_lighthouse_score'] =data["lighthouseResult"]["audits"]["largest-contentful-paint"]["score"] 
                    psi_dict['cls_lighthouse'] =round(data["lighthouseResult"]["audits"]["cumulative-layout-shift"]["numericValue"],3)
                    psi_dict['cls_lighthouse_score'] =data["lighthouseResult"]["audits"]["cumulative-layout-shift"]["score"] 
                    psi_dict['max_potential_fid (ms)'] =data["lighthouseResult"]["audits"]["max-potential-fid"]["numericValue"] 
                    psi_dict['max_potential_fid_score'] =data["lighthouseResult"]["audits"]["max-potential-fid"]["score"] 
                    
                    psi_dict['tbt (ms)']  = data["lighthouseResult"]["audits"]["total-blocking-time"]["numericValue"]
                    psi_dict['tbt_score'] = data["lighthouseResult"]["audits"]["total-blocking-time"]["score"]
                    

                    psi_dict['speed_index (ms)'] = round(data["lighthouseResult"]["audits"]["speed-index"]["numericValue"],1)
                    psi_dict['speed_index_score'] = data["lighthouseResult"]["audits"]["speed-index"]["score"]
                
                    psi_dict['tti (ms)'] = round(data["lighthouseResult"]["audits"]["interactive"]["numericValue"],1)
                    psi_dict['tti_score']= data["lighthouseResult"]["audits"]["interactive"]["score"]

                    items=data["lighthouseResult"]["audits"]["resource-summary"]['details']["items"]

                    for elem in items:
                        if elem.get('resourceType')=='total':
                            psi_dict['total_size (KB)']=round(elem.get('transferSize')/1024,2)
                            psi_dict['total']=elem.get('requestCount')
                        elif elem.get('resourceType')=='stylesheet':
                            psi_dict['css_size (KB)']=round(elem.get('transferSize')/1024,2)
                            psi_dict['css']=elem.get('requestCount')
                        elif elem.get('resourceType')=='font':
                            psi_dict['fonts_size (KB)']=round(elem.get('transferSize')/1024,2)
                            psi_dict['fonts']=elem.get('requestCount')
                        elif elem.get('resourceType')=='image':
                            psi_dict['img_size (KB)']=round(elem.get('transferSize')/1024,2)
                            psi_dict['img']=elem.get('requestCount')
                        elif elem.get('resourceType')=='script':
                            psi_dict['js_size (KB)']=round(elem.get('transferSize')/1024,2)
                            psi_dict['js']=elem.get('requestCount')
                        elif elem.get('resourceType')=='document':
                            psi_dict['html_size (KB)']=round(elem.get('transferSize')/1024,2)
                            psi_dict['html']=elem.get('requestCount')
                        elif elem.get('resourceType')=='media':
                            psi_dict['media_size (KB)']=round(elem.get('transferSize')/1024,2)
                            psi_dict['media']=elem.get('requestCount')
                        elif elem.get('resourceType')=='other':
                            psi_dict['others_size (KB)']=round(elem.get('transferSize')/1024,2)
                            psi_dict['others']=elem.get('requestCount')
                        elif elem.get('resourceType')=='third-party':
                            psi_dict['third_party_size (KB)']=round(elem.get('transferSize')/1024,2)
                            psi_dict['third_party']=elem.get('requestCount')
                    dct_arr.append(psi_dict)
                    print(psi_dict)
                    time.sleep(3)
            df = pd.DataFrame(dct_arr)
            df.to_csv(fichero_salida, index=False)
        except HTTPError as e:
            print('Error al procesar la petición')
    except FileNotFoundError as e:
        print("File not found: "+e.strerror)
    except pd.errors.EmptyDataError:
        print("No data")
    except pd.errors.ParserError:
        print("Parse error")
    except Exception as e:
        print("Some other exception")
else:
    print('Número de parámetros incorrecto')
print('fin')