import requests
import json
from datetime import datetime
import sys

def calculate_time_difference(horaire_prevu, horaire_corrigee):
    try:
        heures_prevues, minutes_prevues, _ = map(int, [horaire_prevu[:2], horaire_prevu[2:4], horaire_prevu[4:]])
        heures_corrigees, minutes_corrigees, _ = map(int, [horaire_corrigee[:2], horaire_corrigee[2:4], horaire_corrigee[4:]])
        difference_minutes = max(0, (heures_corrigees - heures_prevues) * 60 + (minutes_corrigees - minutes_prevues))
        return difference_minutes
    except ValueError:
        #print("Erreur de format. Assurez-vous que les horaires sont au format 'HHMMSS'.")
        return None

def complete_amended_arrival_time(amended_time, full_date):
    try:
        # Convertir amended_time en format HHMMSS en heures, minutes et secondes
        heures_amended = int(amended_time[:2])
        minutes_amended = int(amended_time[2:4])
        secondes_amended = int(amended_time[4:])
        
        # Analyser la date complète en format YYYYMMDDTHHMMSS
        full_date = datetime.strptime(full_date, '%Y%m%dT%H%M%S')
        
        # Créer une nouvelle date en ajoutant les heures, minutes et secondes de amended_time
        amended_arrival_time = full_date.replace(hour=heures_amended, minute=minutes_amended, second=secondes_amended)
        
        # Formater la nouvelle date en chaîne au format YYYYMMDDTHHMMSS
        amended_arrival_time_str = amended_arrival_time.strftime('%Y%m%dT%H%M%S')
        
        return amended_arrival_time_str
    except ValueError:
        #print("Erreur de format. Assurez-vous que les horaires sont au format 'HHMMSS' et la date au format 'YYYYMMDDTHHMMSS'.")
        return None


def get_next_ter_info(api_key, from_stop, to_stop, n_max_train):
    url = 'https://api.sncf.com/v1/coverage/sncf/journeys'
    
    params = {
        'from': f'stop_area:SNCF:{from_stop}',
        'to': f'stop_area:SNCF:{to_stop}',
        'count': 5*n_max_train,
        'data_freshness': 'realtime'
    }

    response = requests.get(url, auth=(api_key, ''), params=params)

    if response.status_code == 200:
        data = response.json()
        nTER = 1
        trajets = []
        for journey in data['journeys']:
            num_train = 'N/A'
            retard = False

            for section in journey['sections']:
                if 'display_informations' in section:
                    display_info = section['display_informations']
                    num_train = display_info.get('headsign', 'N/A')
                    type_train = display_info.get('commercial_mode', 'N/A')
                    if 'DELAYS' in journey['status']:
                        retard = True
                    break
            
            if type_train != 'TER':
                continue
            
            amended_arrival_time = journey['sections'][-1]['arrival_date_time']
            difference_minutes = 0
            motif_retard = None
            if retard:
                links = journey['sections'][1]['display_informations']['links']
                for link in links:
                    if 'disruptions' in link['rel']:
                        id_disruption = link['id']
                        disruptions = data['disruptions']
                        for disruption in disruptions:
                            if disruption['id'] == id_disruption:
                                motif_retard_unicode = disruption['messages'][0]['text']
                                motif_retard = motif_retard_unicode.encode('utf-8').decode('unicode-escape')
                                impacted_stops = disruption['impacted_objects'][0]['impacted_stops']
                                for impacted_stop in impacted_stops:
                                    if to_stop in impacted_stop['stop_point']['id']:
                                        base_arrival_time = impacted_stop['base_arrival_time']
                                        if 'amended_arrival_time' in impacted_stop:
                                            amended_arrival_time = impacted_stop['amended_arrival_time']
                                        else:
                                            amended_arrival_time = journey['sections'][-1]['arrival_date_time']
                                        difference_minutes = calculate_time_difference(base_arrival_time, amended_arrival_time)
                                break

            trajet_info = {
                'Depart': journey['sections'][0]['from']['name'],
                'Arrivee': journey['sections'][-1]['to']['name'],
                'Numero du Train': num_train,
                'Heure de Depart': journey['sections'][0]['departure_date_time'],
                'Heure d\'Arrivee': complete_amended_arrival_time(amended_arrival_time, journey['sections'][-1]['arrival_date_time']) if retard else journey['sections'][-1]['arrival_date_time'],
                'Type de Train': type_train,
                'Status': 'RETARD' if retard else 'A l\'heure',
                'Motif du retard': motif_retard if retard else None,
                'Retard (minutes)': difference_minutes
            }
            trajets.append(trajet_info)
            if nTER == n_max_train:
                return trajets, response.status_code
            else:
                nTER += 1

        return trajets, response.status_code
    else:
        print('La requête a échoué avec le code de statut:', response.status_code)
        return None

#####################
#####################
#####################
#####################

#####################
# Remplacez ces valeurs par votre clé d'identification et les codes des gares
ville1 = '...' # par exemple 87391003 pour Paris - Montparnasse - Hall 1 & 2
ville2 = '...' # par exemple 87571000 pour Tours
api_key = "..." # clé à obtenir sur https://numerique.sncf.com/startup/api/token-developpeur/
#####################

# Vérifiez si des arguments de ligne de commande sont fournis
if len(sys.argv) != 3:
    #print("Utilisation: python3 script.py <from_depature> <to_arrival>")
    sys.exit(1)

#####################
# Remplacez les chaines pour les noms des villes que vous utiliserez 
# par exemple sur l'exemple Paris - Tours, 'ville1' peut être remplacé par 'Paris' et 'ville2' par 'Tours'
#####################
from_depature = sys.argv[1]
if from_depature == 'ville1':
    from_depature = ville1
elif from_depature == 'ville2':
    from_depature = ville2
to_arrival = sys.argv[2]
if to_arrival == 'ville1':
    to_arrival = ville1
elif to_arrival == 'ville2':
    to_arrival = ville2

n_max_train = 5

# Obtenez les informations TER en utilisant les arguments de la ligne de commande
result, status = get_next_ter_info(api_key, from_depature, to_arrival, n_max_train)

if result is not None:
    result = {"trains": result,
              "status": status}
    print(json.dumps(result, indent=2))
else:
    trajet_info = {
        'Depart': None,
        'Arrivee': None,
        'Numero du Train': None,
        'Heure de Depart': None,
        'Heure d\'Arrivee': None,
        'Type de Train': None,
        'Status': 'unknown',
        'Motif du retard': None,
        'Retard (minutes)': 0
    }
    result = {"trains": trajet_info,
              "status": "error"}
    