#!/usr/bin/python
#pokemon_tcg_filter.py
#Miburi https://github.com/miburi/pokemon-tcg
#Last Updated: 12/14/2020

from pokemontcgsdk import Card
from pokemontcgsdk import Set 
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
from datetime import * 
from datetime import datetime
import re
import mysql.connector
import json 

def help_add_menu():
    helpStr="""
    Type the command below to run the following actions.. 
    ---------------------------------------
    a|add) Add cards to inventory..
    r|remove) Remove cards in inventory...  
    c|change) Change card input set name...
    h|help) Display the help menu.. 
    v|view) For displaying current inventory.. 
    q|quit) Goes back to top menu...
    """
    print(helpStr)

def help_menu():
    helpStr="""
    Type the command below to run the following actions.. 
    ---------------------------------------
    h|help) Display the help menu 
    i|inventory) Go into the inventory to add/remove cards..
    p|pokemon) Go into the Pokemon card section...
    q|quit) Quits application
    s|set) Updates the Pokemon tcg database set...  
    """
    print(helpStr)


def help_pokemon_menu():
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

############# SECTION THAT CHECKS IF CARD STRING SET IS VALID #############################
def setChecker(cardSet):
    cards=Card.where(setCode=cardSet)
    if len(cards)>0:
        return cards 
    return [] 

############# SECTION FOR UPDATING CARDS IN INVENTORY ##############################
def add_card():
    print("###################################################################") 
    print("Welcome! This section is for adding your cards into the inventory..") 
    
    
    while True:
        try:
            user_input=input("What would you like to do(h for menu)?")
            #Add card to inventory function 
            class Found(Exception):pass
            try:
                if user_input in ('a', 'A','add', 'Add'):
                    insertSet=input("Please enter a tracking code(for set track/retrieval purposes):")
                    print("Your setcode is:", insertSet) 
                    while True: 
                        cardSet=input("Type the set code(i.e. Evolutions xy12) you would like to use#(h for set list):")
                        if cardSet in ('h', 'H','?', 'help'):
                            help_pokemon_menu()
                        elif cardSet in ('q', 'Q','quit', 'Quit'):
                            raise Found 
                        cards=setChecker(cardSet)
                        if len(cards) <=0:
                            print("Invalid card set, returning..")
                            return 1
                        else: 
                            print("Set confirmed:", Set.find(cardSet).name)
                            #pokemon_cards_list(user_input) 
                            print("Find the card number on bottom left corner and enter in the following format: NUMBER + (optional) any special rarity types(r-reverse holo, f-full art, p-promo) + (optional) quantity via '+' (if greater than 1 is needed), and comma for multiple cards.")
                            print("Example: 1 Regular Caterpie(3), 2 Regular Charmander(9), 1 Rare Beedrill(7), 1 Full Art Mewtwo-Ex(52) = 3,9+2,7r,52fr") 
                            while True:
                                user_input=input("Add Cards(q to quit)#:")
                                if user_input in ('q', 'Q', 'quit', 'Quit'):
                                    break
                                else:
                                    splitInputs=user_input.split(",")
                                    for i in splitInputs:
                                        i=i.strip()
                                        normalFlag=1 #always start off with 1 normal card
                                        reverseholoFlag=0 #default set to false
                                        fullartFlag=0 #default set to false 
                                        promoFlag=0 #default set to false

                                        number=i
                                        quantity=1
                                        if any(x in i for x in ["r", "R"]):
                                            i=i.replace('r','').replace('R','')
                                            number=i
                                            reverseholoFlag=1
                                        if any(x in i for x in ["f", "F"]):
                                            i=i.replace('f','').replace('F','')
                                            number=i
                                            fullartFlag=1
                                        if any(x in i for x in ["p", "P"]):
                                            i=i.replace('p','').replace('P','')
                                            number=i
                                            promoFlag=1
                                        if len(i.split('+')) ==2:
                                            i=i.split('+')
                                            number=i[0]
                                            quantity=int(i[1])
                                        ###### Check set and then adding into cardhistory and updating inventory #######3 
                                        mydb=mysql.connector.connect( host="localhost", user=username, password=password, database="pokemontcg")
                                        mycursor=mydb.cursor()
                                        sql="select * from cards where set_code='"+cardSet+"' and number='"+number+"'"; 
                                        mycursor.execute(sql)
                                        result=mycursor.fetchall()
                                        if len(result)!=0:
                                            code=result[0][0]
                                            name=result[0][1]
                                            cardSet=result[0][15]
                                            sql="update inventory SET `quantity-normal` = `quantity-normal`+"+str(quantity)+",`quantity-reverseholo` = `quantity-reverseholo`+"+str(quantity*reverseholoFlag)+",`quantity-fullart` = `quantity-fullart`+"+str(quantity*fullartFlag)+",`quantity-promo` = `quantity-promo`+"+str(quantity*promoFlag)+" where code='"+code+"';"
                                            mycursor.execute(sql)
                                            sql="insert into cardhistory(`code`, `name`, `set`, `insert_set`, `inserted_date`, `normal`, `reverseholo`, `fullart`, `promo` ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                                            mycursor.execute(sql, (code, name, cardSet, insertSet, datetime.now().strftime("%Y-%m-%d %H:%M"),normalFlag*quantity, reverseholoFlag*quantity, fullartFlag*quantity, promoFlag*quantity))
                                            mydb.commit()
                                            print("Completed adding %s %s Card Qty Normal:%s Reverse Holo:%s Full Art:%s Promo:%s into the inventory.."% (code, name,str(quantity), str(quantity*reverseholoFlag), str(quantity*fullartFlag), str(quantity*promoFlag)))
                                        else:

                                            print("Card number", i, " does not exist in database. Add the card set in first and retry again..")

                #Change setcode
                elif user_input in ('c', 'C','change', 'Change'):
                    insertSet=input("Please enter a track code(for set track/retrieval purposes):")
                    print("Your new input setcode is:", insertSet) 
                #help menu
                elif user_input in ('h', 'H','?', 'help'):
                    help_add_menu() 
                #remove card from inventory
                elif user_input in ('r', 'R','remove', 'Remove'):
                    print("Remove card from inventory")
                    while True:
                        cardSet=input("Type the set code(i.e. Evolutions xy12) you would like to use#(h for set list):")
                        cards=setChecker(cardSet)
                        if len(cards) <=0:
                            print("Invalid card set, returning..")
                            break 
                        quantity=0
                        print("Find the card number on bottom left corner and enter in the following format: NUMBER + (optional) any special rarity types(r-reverse holo, f-full art, p-promo) + (optional) quantity via '+' (if greater than 1 is needed), and comma for multiple cards.")
                        print("Example: 1 Regular Caterpie(3), 2 Regular Charmander(9), 1 Rare Beedrill(7), 1 Full Art Mewtwo-Ex(52) = 3,9+2,7r,52fr") 
                        while True:
                            user_input=input("Remove Cards(q to quit)#:")
                            if user_input in ('q', 'Q', 'quit', 'Quit'):
                                break
                            else:
                                splitInputs=user_input.split(",")
                                for i in splitInputs:
                                    i=i.strip()
                                    normalFlag=1 #always start off with 1 normal card
                                    reverseholoFlag=0 #default set to false
                                    fullartFlag=0 #default set to false 
                                    promoFlag=0 #default set to false
                                    number=i
                                    quantity=1
                                    if any(x in i for x in ["r", "R"]):
                                        i=i.replace('r','').replace('R','')
                                        number=i
                                        reverseholoFlag=1
                                    if any(x in i for x in ["f", "F"]):
                                        i=i.replace('f','').replace('F','')
                                        number=i
                                        fullartFlag=1
                                    if any(x in i for x in ["p", "P"]):
                                        i=i.replace('p','').replace('P','')
                                        number=i
                                        promoFlag=1
                                    if len(i.split('+')) ==2:
                                        i=i.split('+')
                                        number=i[0]
                                        quantity=int(i[1])
                                    cardCode=cardSet+"-"+number 
                                    #UPDATE inventory SET `quantity-normal` = `quantity-normal` - 1 WHERE code='swsh4-1' and `quantity-normal` >0;
                                    mydb=mysql.connector.connect( host="localhost", user=username, password=password, database="pokemontcg")
                                    mycursor=mydb.cursor()
                                    #Decrease normal card quantity
                                    sql="UPDATE inventory SET `quantity-normal`=`quantity-normal`-"+str(quantity*normalFlag)+" WHERE code='"+str(cardCode)+"' and `quantity-normal` >0;"
                                    mycursor.execute(sql)
                                    #Decrease reverse holo card quantity
                                    sql="UPDATE inventory SET `quantity-reverseholo`=`quantity-reverseholo` -"+str(quantity*reverseholoFlag)+" WHERE code='"+str(cardCode)+"' and `quantity-reverseholo` >0;"
                                    mycursor.execute(sql)
                                    #Decrease full art card quantity
                                    sql="UPDATE inventory SET `quantity-fullart`=`quantity-fullart`-"+str(quantity*fullartFlag)+" WHERE code='"+str(cardCode)+"' and `quantity-fullart` >0;"
                                    mycursor.execute(sql)
                                    #Decrease promo card quantity
                                    sql="UPDATE inventory SET `quantity-promo`=`quantity-promo`-"+str(quantity*promoFlag)+" WHERE code='"+str(cardCode)+"' and `quantity-promo` >0;"
                                    mycursor.execute(sql)
                                    mydb.commit()
                                    print("Removed %s Card Qty Normal:%s Reverse Holo:%s Full Art:%s Promo:%s from the inventory.."% (cardCode, str(quantity), str(quantity*reverseholoFlag), str(quantity*fullartFlag), str(quantity*promoFlag)))


                elif user_input in ('q', 'Q','quit'):
                    break 
                elif user_input in ('v', 'V','view', 'View'):
                    print("View inventory..")    
                    cardSet=input("Type the set code(i.e. Evolutions xy12) you would like to use#(h for set list):")
                    if cardSet in ('h', 'H','?', 'help'):
                        help_pokemon_menu()
                    elif cardSet in ('q', 'Q','quit', 'Quit'):
                        raise Found 
                    elif isinstance(cardSet,str):
                        if len(cardSet) >0:     
                            mydb=mysql.connector.connect( host="localhost", user=username, password=password, database="pokemontcg")
                            mycursor=mydb.cursor()
                            sql="select * from inventory where set_code='"+cardSet+"' ORDER BY CAST(`number` AS unsigned);"
                            mycursor.execute(sql)
                            result=mycursor.fetchall()
                            for i in result:
                                print(*i, sep="  ")
                    else:
                        print("No inventory of set "+cardSet+"..")

                elif not user_input:
                    raise ValueError('No input, try again..') 
            except Found:
                print("EXCEPT")
        except ValueError as e:
            print("Invalid input, try again..",e) 
######################################################################################################


############# SECTION FOR UPDATING SETS ##############################
def set_update():
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
############# SECTION FOR UPDATING CARDS ##############################
def cards_update(cardSet):
    mydb=mysql.connector.connect( host="localhost", user=username, password=password, database="pokemontcg")
    mycursor=mydb.cursor()
    cards=setChecker(cardSet)
    if len(cardSet) <=0:
        print("Invalid card set, returning..")
        return 1 
    cardCount,normalCardCount,trainerCardCount,rarePokemonCount=0,0,0,0
    pokemonCards,rarePokemonCards,trainerCards=[],[],[]
    for card in cards:
        #print("RETREAT",card.retreat_cost, "CONVERTED", card.converted_retreat_cost, "TYPES", card.types, "ATTACKS",card.attacks, "WEAKNESSES",card.weaknesses, "RESISTANCES",card.resistances)
        cardCount+=1

        #Part 1- Insert statement for card inventory  
        sql="select * from inventory where code='"+card.id+"'"
        mycursor.execute(sql)
        rows = mycursor.fetchall()
        if len(rows)!= 1:
            sql="INSERT INTO inventory (`code`, `set`, `set_code`, `number`, `name`, `quantity-normal`, `quantity-reverseholo`, `quantity-fullart`, `quantity-promo` ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val=(str(card.id), str(card.set), str(card.set_code),str(card.number), str(card.name), 0, 0, 0, 0)
            mycursor.execute(sql, val)
            mydb.commit()
        #################################################################

        #Part 2 - Checks if set exists, if so it tries to update or else inserts new statement 
        sql="select * from cards where id='"+card.id+"'"
        mycursor.execute(sql)
        rows = mycursor.fetchall()
        if len(rows)!= 1:
            print("Inserting card ", card.id, card.name, card.national_pokedex_number, card.image_url, card.image_url_hi_res, "SUBTYPE",card.subtype, "SUPERTYPE",card.supertype, "ABILITY",str(json.dumps(card.ability)), "ANCIENT", card.ancient_trait, card.hp, card.number, card.artist, card.rarity, card.series, card.set, card.set_code, "RETREAT", str(json.dumps(card.retreat_cost)), str(json.dumps(card.converted_retreat_cost)), "TEXT",str(json.dumps(card.text)))
            #Insert statement for new cards
            sql="INSERT INTO cards (`id`, `name`, `national_pokedex_number`, `image_url`, `image_url_hi_res`, `subtype`, `supertype`, `ability`, `ancient_trait`, `hp`, `number`, `artist`, `rarity`, `series`, `set`, `set_code`,`retreat_cost`, `converted_retreat_cost`, `text`) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val=(card.id, card.name, card.national_pokedex_number, card.image_url, card.image_url_hi_res, card.subtype, card.supertype, str(json.dumps(card.ability)), card.ancient_trait, card.hp, card.number, card.artist, card.rarity, card.series, card.set, card.set_code, str(json.dumps(card.retreat_cost)), str(json.dumps(card.converted_retreat_cost)), str(json.dumps(card.text)))
            mycursor.execute(sql, val)
        else:
            #print("Found set, attempt to update values..")
            sql="UPDATE cards SET `id`=%s, `name`=%s, `national_pokedex_number`=%s, `image_url`=%s, `image_url_hi_res`=%s,`subtype`=%s, `supertype`=%s, `ability`=%s, `ancient_trait`=%s, `hp`=%s, `number`=%s, `artist`=%s, `rarity`=%s, `series`=%s, `set`=%s, `set_code`=%s, `retreat_cost`=%s, `converted_retreat_cost`=%s, `text`=%s where id="+"'"+card.id+"'"
            val=(card.id, card.name, card.national_pokedex_number, card.image_url, card.image_url_hi_res, card.subtype, card.supertype, str(json.dumps(card.ability)), card.ancient_trait, card.hp, card.number, card.artist, card.rarity, card.series, card.set, card.set_code, str(json.dumps(card.retreat_cost)), str(json.dumps(card.converted_retreat_cost)), str(json.dumps(card.text)))
            mycursor.execute(sql, val)
            mydb.commit()
    print("Finished inserting and check cards for ",cardSet)
    return 0
     
######################################################################################################



def pokemon_cards_list(s):
     
    cards=Card.where(setCode=s)
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
        cardSetVal=input("Select Output 1) All Cards, 2) Rare Cards, 3) Trainer Cards, 4) Search for Cards 5) Go Back:")    
        switcher = { 
               "1": pokemonCards, 
               "2": rarePokemonCards, 
               "3": trainerCards, 
               "4": searchCards, 
         }           
        if cardSetVal =="5":
            break
        if cardSetVal =="4":
            cardSearchName=input("Enter card name(i.e. Charizard):")
            print(cardSearchName)
            for card in pokemonCards:
                x=re.search(cardSearchName, card['name'],re.IGNORECASE)
                if x:
                    print(card) 
   
        else:
            pokemonCardSet=switcher.get(cardSetVal, "") 
            #print("pokemonCardSet=",pokemonCardSet)
            sortVal=input("Select sort type[1:name, 2:number, 3:rarity]:")
            if sortVal in ("1","2","3"):
                switcher = { 
                    "1": "name", 
                    "2": "number", 
                    "3": "rarity",
                    #"4": "types",
                }           
                #No types yet
                sortValStr=switcher.get(sortVal, "") 
                sortedPokemonCards=sorted(pokemonCardSet, key=lambda e: e[sortValStr])
                print(sortedPokemonCards)
                print("\n")
                print("--------------------------------------------------")
                f = open("sets/"+user_input+".csv", "w")
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

   
print("###########################################################")
print("Miburi Pokemon Trading Card Game Collections App..")
print("Alpha Version 1.2.0")
print("Youtube/Instagram Channel: Miburi Official")
print("https://github.com/miburi/pokemon-tcg")
print("###########################################################")
while True:
    try:
        user_input=input("Enter what you would like to do#(h for command help list):")
        if user_input in ('h', 'H','?', 'help'):
            help_menu()
        elif user_input in ('i', 'I','inventory', 'Inventory', 'in'):
            add_card()
        elif user_input in ('q', 'Q','quit'):
            sys.exit(1)
        elif user_input in ('s', 'S','set'):
            print("Checking and updating sets...")
            set_update()
        elif user_input in ('p', 'Pokemon', 'pokemon'):
            while True: 
                user_input=input("Enter the set code(i.e. Evolutions xy12) you would like to use#(h for set list):")
                if user_input in ('h', 'H','?', 'help'):
                    help_pokemon_menu()
                elif user_input in ('q', 'Q','quit'):
                    break 
                elif isinstance(user_input,str):
                    if (cards_update(user_input) == 0):
                        pokemon_cards_list(user_input) 
        elif not user_input:
            raise ValueError('No input, try again..') 
    except ValueError as e:
        print("Invalid input, try again..",e)
    
sys.exit(1)
