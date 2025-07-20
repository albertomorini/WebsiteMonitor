

CASO 1 (percentuale >= 0.5):
    contatore salita +1
    contatore uguale = 0
    prezzo massimo = prezzo attuale

CASO 2 (percentuale>0 e percentaule<0.5):
    contatore salita = 0
    contatore uguale = 0
    prezzo massimo = prezzo attuale


CASO 3 (percentale = 0 ):
    contatore salita = 0
    contatore uguale +1

CASO 4 (percentuale > percentuale PERDITA):
    // SEGNALO DA VENDERE
    reset di tutti i campi

CASO 5 (percentuale<0 e percentuale < percentuale PERDITA):
    contatore salita = 0
    contatore uguale +1


-----

Se contatoreSalita=Contatore: compro 
Se contatoreUguale=ContatoreUguale: vendo
Se CASO4: vendo
