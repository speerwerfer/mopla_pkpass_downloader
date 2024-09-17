import requests
import json
import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta
import calendar

parser = ArgumentParser(description="mo.pla pkpass downloader")
parser.add_argument("-u", "--username", dest="username", help="mo.pla username")
parser.add_argument("-p", "--password", dest="password", help="mo.pla password")
parser.add_argument("-o", "-output", dest="outputfile", default="deutschlandticket", help="name of the outputfile (default=deutschlandticket.pkpass)")
args = parser.parse_args()

if not args.username:
    print("no username set")
    sys.exit()

if not args.password:
    print("no password set")
    sys.exit()    

googleUrl = 'https://identitytoolkit.googleapis.com/v1/accounts:createAuthUri?key=AIzaSyDs7EoghaZrC-39RFyeRS_DdacygMvinzQ'
#header = {'Content-Type': 'application/json'}
payload = {'identifier': args.username,'continueUri': 'https://app.mopla.solutions/welcome?login'}
r = requests.post(googleUrl, data=payload)

googleUrl = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDs7EoghaZrC-39RFyeRS_DdacygMvinzQ'
payload = {'email': args.username,'password': args.password,'returnSecureToken': 'true'}
r = requests.post(googleUrl, data=payload)
idToken = r.json().get('idToken')

googleUrl = 'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=AIzaSyDs7EoghaZrC-39RFyeRS_DdacygMvinzQ'
payload = {'idToken': idToken }
r = requests.post(googleUrl, data=payload)
response = r.json().get('idToken')

url = 'https://backend.mopla.solutions/api/whoami'
header = {
    'Content-Type': 'application/json', 
    'Authorization': 'Bearer ' + idToken
    }
r = requests.get(url, headers=header)

url = 'https://backend.mopla.solutions/api/passengers/tickets'
r = requests.get(url, headers=header)
tickets = []
for item in r.json():
    gueltig_ab = datetime.strptime(item['validFrom'], "%Y-%m-%dT%H:%M:%S%z").date() + timedelta(days=1)
    tickets.append((item['id'], calendar.month_name[gueltig_ab.month]))

if not tickets:
    print("Keine Tickets gefunden. Programm wird abgebrochen.")
    sys.exit()

url = 'https://backend.mopla.solutions/api/passengers/appleWalletPass'
header = {
    'Content-Type': 'application/json', 
    'Authorization': 'Bearer ' + idToken
    }

for id, monat in tickets:
    payload = {'ticketId': id}
    r = requests.get(url, headers=header, params=payload)
    output_file = args.outputfile + '_' + monat + '.pkpass'
    with open(output_file, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    print('Datei ' + output_file + ' erzeugt!')

