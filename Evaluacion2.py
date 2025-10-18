#pip install requests

import requests
import urllib.parse

geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"
key = "32cb82ff-4ced-4448-a38c-7bd840ccd2b0"


def geocoding (location, key):

    while location == "":
        location = input("Ingrese nuevamente la localización: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q":location, "limit": "1", "key":key})

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200:
        lat=round(json_data["hits"][0]["point"]["lat"],2) #Agregado el round(x,2) para 2 decimales
        lng=round(json_data["hits"][0]["point"]["lng"],2) #Agregado el round(x,2) para 2 decimales
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        if value == "city":     #Para cambiar el idioma del tipo de localización despues de sacar la variable de la API
            value = "Ciudad"
        if value == "country":
            value = "País"
        if value == "state":
            value = "Estado"
        if value == "administrative":
            value = "Administrativo"
        if value == "suburb":
            value = "suburbio"

        if "country" in json_data["hits"][0]:
            country = json_data["hits"][0]["country"]
        else:
            country=""
        if "state" in json_data["hits"][0]:
            state = json_data["hits"][0]["state"]
        else:
            state=""

        if len(state) !=0 and len(country) !=0:
            new_loc = name + ", " + state + ", " + country
        elif len(state) !=0:
            new_loc = name + ", " + country
        else:
            new_loc = name
        
        
    
        print("\nGeocodificación API URL para " + new_loc + " (Tipo de ubicación: " + value + ")\n" + url)
    else:
        lat="null"
        lng="null"
        new_loc=location
    return json_status,lat,lng,new_loc

while True:

    print("\nEscriba 's' o 'salir' para terminar programa \n")

    print("\n=================================================")
    print("Perfiles de vehículos disponibles en Graphhopper:")
    print("=================================================")
    print("auto, bicicleta, caminando")
    print("=================================================")

    #Mapeo nombres en español a nombres que usa la API
    mapa_vehiculos = {
        "auto": "car",
        "bicicleta": "bike",
        "caminando": "foot"
    }

    vehiculo_input = input("Introduzca un perfil de vehículo de la lista anterior: ").strip().lower()
    if vehiculo_input == "s" or vehiculo_input == "salir":
        break
    elif vehiculo_input in mapa_vehiculos:
        vehicle = mapa_vehiculos[vehiculo_input] # Para buscar en el diccionario mapa_vehiculos la clave que es el string vehiculo_input
    else:
        vehicle = "car"
        print("Perfil de vehículo no válido. Se usará 'auto' por defecto.")


    loc1 = input("Ingrese Localización de inicio: ")
    if loc1 == "s" or loc1 == "salir":
        break
    orig = geocoding(loc1, key)
    print(str(orig) + "\n")

    loc2 = input("Ingrese su destino: ")
    if loc2 == "s" or loc2 == "salir":
        break
    dest = geocoding(loc2, key)
    print(str(dest) + "\n")
    print("================================================= \n")
    if orig[0] == 200 and dest[0] == 200:
        op="&point="+str(orig[1])+"%2C"+str(orig[2])
        dp="&point="+str(dest[1])+"%2C"+str(dest[2])

        params = {      # Cambio de construccion de URL
        "key": key,
        "locale": "es",  # Aqui se cambia el idioma de las intrucciones del viaje a español
        "vehicle": vehicle # Se agrega el parametro vehiculo para construit la URL
        }

        paths_url = route_url + urllib.parse.urlencode(params) + op + dp #Se agregan los params de arriba a la URL
        paths_status = requests.get(paths_url).status_code
        paths_data = requests.get(paths_url).json()

        mapa_vehiculos_print = {
            "car": "auto",
            "bike": "bicicleta",
            "foot": "caminando"
        }


        print("Routing API Status: " + str(paths_status) + "\nRouting API URL:\n" + paths_url)
        print("=================================================")
        print("Direcciones desde " + orig[3] + " hacia " + dest[3] + " por " + mapa_vehiculos_print.get(vehicle, vehicle))
        print("=================================================")


        if paths_status == 200:
            distancia_km = paths_data["paths"][0]["distance"] / 1000
            distancia_millas =  distancia_km * 0.621371
            total_segundos = paths_data["paths"][0]["time"] / 1000

            horas = int(total_segundos // 3600)
            minutos = int((total_segundos % 3600) // 60)
            segundos = int(total_segundos % 60)

            print(f"Distancia recorrida: {distancia_km:.2f} km // {distancia_millas:.2f} mi") #Cambio de metros a km y que se muestren 2 decimales.
            print(f"Duración del viaje: {horas}h {minutos}m {segundos}s") #Cambio de milisegundos a horas, minutos, segundos para mejor legibilidad
            print("=================================================\n")

            for each in range(len(paths_data["paths"][0]["instructions"])):
                path = paths_data["paths"][0]["instructions"][each]["text"]
                distance = paths_data["paths"][0]["instructions"][each]["distance"]
                print("{0}. {1} ( {2:.1f} km / {3:.1f} miles )".format(
                    each + 1, path, distance / 1000, distance / 1000 / 1.61))
            print("=============================================\n")
        else:
            error_message_en = paths_data.get("message", "No se recibió un mensaje de error.")
            # Diccionario de traducciones de errores
            translation_dict = { 
                "Connection between locations not found": "No se encontró conexión entre las ubicaciones",
                # Se pueden agregar mas errores
            }
            error_message_es = translation_dict.get(error_message_en, error_message_en)
            print("Mensaje de error: " + error_message_es)
            print("*************************************************\n")