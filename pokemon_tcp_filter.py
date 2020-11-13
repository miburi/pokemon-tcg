#!/usr/bin/python
#pokemon_tcg_filter.py
#Miburi https://github.com/miburi/pokemon-tcg
#Last Updated: 11/13/2020

from pokemontcgsdk import Card
from pokemontcgsdk import Set 
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
from datetime import * 
import re
import mysql.connector



def help_menu():
    helpStr="""Supported Pokemon TCG Series 
----------------------------
1) Sword & Shield 
2) Sun & Moon
3) XY
"""
    def printPokemonHelpMenu(argument): 
        switcher = { 
            "1": "Sword & Shield", 
            "2": "Sun & Moon", 
            "3": "XY", 
        } 
        result=switcher.get(argument, "") 
        sets=Set.where(series=result)
        for pokemonSet in sets:
            print(pokemonSet.release_date, pokemonSet.name, "[", pokemonSet.code, "]" )
    print(helpStr)
    
    sets=Set.all()    
    try:  
        seriesInput=input("Select your series:")             
        printPokemonHelpMenu(seriesInput)
    except ValueError as e:
        print("Input Value error",e)

def pokemon_cards_list(s):
    
    cards=Card.where(setCode=user_input)
    cardCount,normalCardCount,trainerCardCount,rarePokemonCount=0,0,0,0
    pokemonCards,rarePokemonCards,trainerCards=[],[],[]

    for card in cards:
        if card.number.isnumeric(): #Only for cases where card is a number not for cases like 101a
            pokemonCards.append({"types":card.types,"id":card.id, "name":card.name, "number":int(card.number), "pokedex_number":card.national_pokedex_number, "rarity":card.rarity})
        else:
            temp = re.compile("([0-9]+)([a-zA-Z]+)") 
            res=temp.match(card.number).groups()
            card.number=res[0]
            pokemonCards.append({"types":card.types, "id":card.id, "name":card.name, "number":int(card.number), "pokedex_number":card.national_pokedex_number, "rarity":card.rarity})

        if card.supertype=="Pokémon":
            if not (card.rarity in "Common Uncommon"):
                rarePokemonCards.append({"types":card.types, "id":card.id, "name":card.name, "number":int(card.number), "pokedex_number":card.national_pokedex_number, "rarity":card.rarity})
                rarePokemonCount+=1
            else:
                normalCardCount+=1
        else:
            trainerCards.append({"types":card.types, "id":card.id, "name":card.name, "number":int(card.number), "pokedex_number":card.national_pokedex_number, "rarity":card.rarity})
            trainerCardCount+=1
    cardCount+=1
    pokemonSet=Set.find(s)
    print(pokemonSet.series ,"-", pokemonSet.name, ", Total Cards:", pokemonSet.total_cards, "Release Date:",pokemonSet.release_date)
    searchCards=[]
    while True:
        cardSetVal=input("Select Output 1) All Cards, 2) Rare Cards, 3) Trainer Cards, 4) Search for Cards:")    
        switcher = { 
               "1": pokemonCards, 
               "2": rarePokemonCards, 
               "3": trainerCards, 
               "4": searchCards, 
         }           
        if cardSetVal =="4":
            cardSearchName=input("Enter card name(i.e. Charizard):")
            print(cardSearchName)
            for card in pokemonCards:
                x=re.search(cardSearchName, card['name'],re.IGNORECASE)
                if x:
                    print(card) 
            break 
   
        else:
            pokemonCardSet=switcher.get(cardSetVal, "") 
            print("pokemonCardSet=",pokemonCardSet)
            
            sortVal=input("Select sort type[1:type, 2:name, 3:number, 4:rarity]:")
            if sortVal in ("1","2","3","4"):
                switcher = { 
                    "1": "types", 
                    "2": "name", 
                    "3": "number", 
                    "4": "rarity",
                }           
                sortValStr=switcher.get(sortVal, "") 
                sortedPokemonCards=sorted(pokemonCardSet, key=lambda e: e[sortValStr])
                print("\n")
                print("--------------------------------------------------")
                f = open(user_input+".csv", "w")
                for card in sortedPokemonCards:
                    print(card['number'], card['name'], card['types'], card['rarity'])
                    f.write(str(card['number'])+","+card['name']+","+str(card['types'])+","+str(card['rarity']))
                    f.write("\n")
                f.close()

            #sortedPokemonCards=sorted(rarePokemonCards, key=lambda e: e["number"])



            elif sortVal=='q':
                break
            else:
                print("Invalid input..")

     
    #for card in rarePokemonCards:
    #    print(card['name'], card['id'], card['rarity'])
    #sortedPokemonCards=sorted(rarePokemonCards, key=lambda e: e["number"])

    #for card in sortedPokemonCards:
    #    print(card['name'], card['id'], card['number'],card['rarity'])

    #print(rarePokemonCards['id']) 
    #print("Rare pokemon cards", rarePokemonCards, rarePokemonCount)
    
    #print("Trainer cards", trainerCards, trainerCardCount)
    #print("Normal card count", normalCardCount)
    #print("All Pokemons",pokemonCards) 

f=open("/home/ec2-user/.my.cnf","r")

lines=f.readlines()
username, password="",""
for line in lines:
    line=line.split()
    if line[0]=="user":
        username=line[2]
    elif line[0]=="password":
        password=line[2]
f.close()

############# SECTION FOR UPDATING SETS ##############################
mydb=mysql.connector.connect( host="localhost", user=username, password=password, database="pokemontcg")
mycursor=mydb.cursor()
sets=Set.all()    
for i in sets:
    #Checks if set exists, if so it tries to update or else inserts new statement 
    sql="select * from sets where code='"+i.code+"'"
    mycursor.execute(sql)
    rows = mycursor.fetchall()
    if len(rows)!= 1:
        print("Inserting set ", i.code, i.release_date, i.name, i.series, i.total_cards)
        #Insert statement for new sets 
        sql="INSERT INTO sets (code, ptcgo_code, release_date, name, series, total_cards, standard_legal, updated_at, symbol_url, logo_url) values(%s, %s, STR_TO_DATE(%s, '%m/%d/%Y'), %s, %s, %s, %s, STR_TO_DATE(%s,'%m/%d/%Y %H:%i:%S'), %s, %s)"
        val=(i.code, i.ptcgo_code, i.release_date, i.name, i.series, i.total_cards, i.standard_legal, i.updated_at, i.symbol_url, i.logo_url)
        mycursor.execute(sql, val)
        mydb.commit()
    else:
        #print("Found set, attempt to update values..")
        sql="UPDATE sets SET code=%s, ptcgo_code=%s, release_date=STR_TO_DATE(%s, '%m/%d/%Y'), name=%s, series=%s, total_cards=%s, standard_legal=%s, updated_at=STR_TO_DATE(%s, '%m/%d/%Y %H:%i:%S'), symbol_url=%s, logo_url=%s where code="+"'"+i.code+"'"
        val=(i.code, i.ptcgo_code, i.release_date, i.name, i.series, i.total_cards, i.standard_legal, i.updated_at, i.symbol_url, i.logo_url)
        mycursor.execute(sql, val)
        mydb.commit()
######################################################################################################

print("###########################################################")
print("Miburi Pokemon Trading Card Game Collections App..")
print("Alpha Version 1.1")
print("Youtube/Instagram Channel: Miburi Official")
print("https://github.com/miburi/pokemon-tcg")
print("###########################################################")
while True:
    try:
        user_input=input("Enter your deck #(h for help list):")
        if user_input in ('h', 'H','?'):
            help_menu()
        elif user_input in ('q', 'Q'):
            sys.exit(1)
        elif isinstance(user_input,str):
            pokemon_cards_list(user_input) 
        elif not user_input:
            raise ValueError('No input, try again..') 
    except ValueError as e:
        print("Invalid input, try again..",e)
    
sys.exit(1)
















#setDeck=Set.find('base1')
#print(setDeck.code, setDeck.name, setDeck.series, setDeck.total_cards, setDeck.release_date, setDeck.updated_at,setDeck.symbol_url)
rarePokemonCount=0
for card in cards:
    print(card.id, card.name, card.rarity)
    if card.number.isnumeric():
        pokemonCards.append({"number":int(card.number),"id":card.id, "name":card.name, "types":card.types, "rarity":str(card.rarity)})
    else:
        temp = re.compile("([0-9]+)([a-zA-Z]+)") 
        res=temp.match(card.number).groups()
        print("SKIP POKEMON", res) 
        pokemonCards.append({"number":int(res[0]),"id":card.id, "name":card.name, "types":card.types, "rarity":str(card.rarity)})

        #pokemonCards.append({"number":int(card.number),"id":card.id, "name":card.name, "types":card.types, "rarity":str(card.rarity)})

    #if card.supertype=="Pokémon":
    #    pokemonCards.append([card.name, card.national_pokedex_number])
    #    if not (card.rarity in "Common Uncommon"):
    #        rarePokemonCards.append([card.id, card.name, card.national_pokedex_number, card.rarity])
    #        rarePokemonCount+=1
    #    else:
    #        normalCardCount+=1
    #else:
    #    #print("Not pokemon, this is a ", card.id, card.name, card.supertype ,card.rarity)
    #    trainerCards.append([card.id, card.name, card.national_pokedex_number, card.rarity])
    #    trainerCardCount+=1
    #    
    cardCount+=1
#print(pokemonCards)
#print(trainerCards)

#print("Rare pokemon cards", rarePokemonCards, rarePokemonCount)
#print("Trainer cards", trainerCards, trainerCardCount)
#print("Normal card count", normalCardCount)
#print("All Pokemons",pokemonCards) 
sortedPokemonCards=sorted(pokemonCards, key=lambda e: e["number"])
print(sortedPokemonCards)

f = open("xy10.csv", "w")
for card in sortedPokemonCards:
    print(str(card['number']),",",card['name'],",", card['types'],",",str(card['rarity']))
    f.write(str(card['number'])+","+card['name']+","+str(card['types'])+","+str(card['rarity']))
    f.write("\n")
f.close()






############################################################
###### Finding set information ###### 
#compareCPDate=datetime(2017,1,1)
#setCP=Set.find('swsh35') #champion's path
#setCPDate=setCP.release_date #08/23/2019
#setCPDate=datetime.strptime(setCPDate, "%m/%d/%Y")
#setAll=Set.all()
#print(setCP.total_cards)
#print(setAll)
#for s in setAll:
#    #print("%s %s %s" %(s.name, s.series, s.total_cards))
#    setReleaseDate=datetime.strptime(s.release_date, "%m/%d/%Y")
#    if s.total_cards <= 100 and setReleaseDate > compareCPDate:
#     print("%s %s %s %s" %(s.name, s.series, s.total_cards, s.release_date))
#############################################################


