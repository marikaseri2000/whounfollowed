"""
Voglio creare un programma che sia in grado di accedere alla mia lista 
di follower su Github e che riesca a tracciarli giorno per giorno, 
in questo modo posso capire chi ha smesso di seguirmi e chi mi segue.

https://github.com/emanuelegurini?tab=followers
https://github.com/emanuelegurini?page=2&tab=followers
<a rel="nofollow" href="https://github.com/emanuelegurini?page=2&amp;tab=followers">Next</a>


OPERAZIONI DA COMPIERE:
1. strat
2. scarichiamo il contenuto di una pagina
3. verifichiamo se è presente il bottone NEXT
        - se si:
            - prendiamo l'URL e scarichiamo anche quella pagina fino all'ultima
        - se no:
            - verifichiamo se ci sono i follower attraverso lo specifico elemento httml

        -dobbiamo salvare i follower e il numero
            -dove?
                -in un file
       
"""
from requests import get
import re
import uuid
import datetime
import json

#emanuelegurini
#r'<span class="Link--secondary(?: pl-1)?">([^<]+)</span>'

BASE_URL: int = "https://github.com/"
END_URL: str="tab=followers"

PATTERN: str= r'<a\s+[^>]*href="https://github\.com/([^/]+)\?page=(\d+)&amp;tab=followers"[^>]*>Next</a>'
PATTERN_USER= r'<span class="Link--secondary(?: pl-1)?">([^<]+)</span>'

def create_record_object(user_list: list[str]) -> dict[str, str]:
    if not user_list:
        return None
    
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    clean_date = now_utc.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

    return {
        'id': str(uuid.uuid4()),  
        'createdAt': clean_date,  
        'users': user_list,
        'numberOfUsers': len(user_list)
    }

def save(db_name: str, new_value: dict [str, str]) -> bool:
    db: list[str]=[]
    
    with open(f"db/name{db_name}", "r") as f:
        value=json.load(f)
        db.extend(value)
    db.append(new_value)
    
    with open(f"db/name{db_name}", "w", encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    return bool

"""
1. leggere file
2. verificare che sia presente il bottone next
3. se è presente prendere l'url
4. lanciare una nuova get e salvare il contenuto
"""

def is_next_button_present(text: str)->bool:
    if not text:
        raise ValueError("La stringa non può essere vuota.")
    #REGEX
    return bool(re.search(PATTERN, text))

def main()-> None:
    
    controller: bool= False
    counter: int = 0
    
    print("Start del programma")
    
    while True:
        try:
            nome_utente: str= input("Inserisci il nome utente che vuoi analizzare del profilo Github:")
            if not nome_utente:
                raise ValueError("Il nome utente non può essere vuoto.")
            
            # TODO :Il nome exit esiste già
            if nome_utente.strip().lower() == "opsexit":
                break
            print(f"Stai cercando: {nome_utente}")       
            #verifico che l'utente esiste 
            response=get(f"{BASE_URL}{nome_utente}")
            if response.status_code == 404:
                print("Il profilo non esiste")
            else:
                print(f"Profilo {nome_utente} trovato correttamente.")
                controller = True
                break

        except Exception as e:
            print("OPS! Qualcosa è andato storto: {e}") 
        
    while controller:
        counter: int = counter + 1
        url = f"{BASE_URL}{nome_utente}?page={counter}&{END_URL}"
        
        try:
            response = get(url)
            print(response.status_code)
            
            with open(f"tmp/pagina-{counter}.txt", "w") as f:
                #is_next_button_present(response.text)
                f.write(response.text)
                controller = is_next_button_present(response.text)
                print("File salvato.")
        except Exception as e:
            print(f"Errore: {e}")

    lista_utenti: list[str]=[]
    for i in range(counter):
        print(f"Counter: {i+1}")
        with open(f"tmp/pagina-{i+1}.txt", "r") as f:
            text=f.read()
            lista_utenti.extend(re.findall(PATTERN_USER, text))
    #abbiamo creato il nostro record
    save("db.json", create_record_object(lista_utenti))
    print("Fine programma, arrivederci.")

if __name__=="__main__":
    main()

