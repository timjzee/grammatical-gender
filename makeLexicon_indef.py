import sys, string, pickle, random, copy
from numpy.random import choice

#############
# Variables #
#############

PARTICIPANT = int(sys.argv[1])
#PARTICIPANT = 1

GENERATION = int(sys.argv[2])                   # Each generation represents a day.
#GENERATION = 0

MAX_PARTICIPANT = int(sys.argv[3])

MAX_GENERATION = int(sys.argv[4])

INITIAL_LEXICON_SIZE = 300

if GENERATION <= 1220:
    UNKNOWN_INPUT_SIZE = 1
elif GENERATION > 1220:
    UNKNOWN_INPUT_SIZE = 2
KNOWN_INPUT_SIZE = 400 - UNKNOWN_INPUT_SIZE
OUTPUT_SIZE_DEF = 50
OUTPUT_SIZE_INDEF = 50
TOKEN_THRESHOLD = 5

lexicon_template = ["word", "plural (Y/N)", "generation_number", "=","=","=", "=","=","=", "=","=","=", "=","=","=", "=","=","=", "de/het"]

#############
# Functions #
#############

def makeDictionary(file_name):
    """Reads a textfile with file_name and creates a dictionary with a TiMBL friendly structure."""
    f = open(file_name, "r")
    line_list = f.readlines()
    f.close()
    template = ["Number of instances in Lexicon", "Plural (Y/N)", "Probability", "=","=","=", "=","=","=", "=","=","=", "=","=","=", "=","=","=", "de/het"]
    dictionary = {}
    for i in line_list:
        i2 = i[:-1]
        line=i2.split(',')
        key = line[0]
        plur = line[1]
        lab = line[-1]
        dictionary[key] = template[:]
        dictionary[key][1] = plur[:]
        dictionary[key][-1] = lab[:]
        # set number of instances in lexicon to zero
        dictionary[key][0] = 0
        freq = int(line[2])
        if freq == 0:
            freq = 1
        dictionary[key][2] = freq
        # Correct CELEX syllabification
        syls = line[4]
        phons = line[3]
        syls_list = syls.split('-')
        phons_list = phons.split('-')
        for j in range(len(syls_list)-1):
            if len(syls_list[j]) != len(phons_list[j]):
                if syls_list[j] in ["VC","CVC","CCVC","CCCVC"]:
                    syls_list[j] = syls_list[j][:-1]
        syls_new = '-'.join(syls_list)
        # Turn CELEX notation for phones and syllable pattern into TiMBL compatible format
        syls_rev = syls_new[::-1]
        phons_rev = phons[::-1]
        counter_for_insert = 1
        counter = 0
        insert_string = ""
        prev_k = ""
        for k in syls_rev:
            if prev_k != k:
                insert_string = ""
            if k == "C":
                if prev_k == "V" or prev_k == "-":
                    counter_for_insert +=1
                    if counter_for_insert > 15:
                        break
                insert_string = "".join([phons_rev[counter], insert_string])
                dictionary[key][(len(template)-1)-counter_for_insert] = insert_string
            if k == "V":
                if prev_k == "C" or prev_k == "":
                    counter_for_insert +=1
                    if counter_for_insert > 15:
                        break
                    insert_string = "".join([phons_rev[counter]])
                    dictionary[key][(len(template)-1)-counter_for_insert] = insert_string
                if prev_k == "-":
                    counter_for_insert +=2
                    if counter_for_insert > 15:
                        break
                    insert_string = "".join([phons_rev[counter]])
                    dictionary[key][(len(template)-1)-counter_for_insert] = insert_string
                if prev_k == "V":
                    counter -= 1
            prev_k = k[:]
            counter += 1
    return dictionary

def getDictionaries():
    """Sets up the dictionaries that are used to make the training files and check the classifications."""
    try:
        g = open("dic_list_indef.pck", "rb")
        dic_list = pickle.load(g)
        h = open("master_dic_list.pck", "rb")
        master_dic_list = pickle.load(h)
    except:
        dictionary1 = makeDictionary("first_1146_nouns_final.txt")
        dictionary2 = makeDictionary("remaining_nouns_final.txt")
        dic_list = [dictionary1, dictionary2]
        master_dic_list = copy.deepcopy(dic_list)
        g = open("dic_list_indef.pck", "wb")
        pickle.dump(dic_list, g)
        h = open("master_dic_list.pck", "wb")
        pickle.dump(master_dic_list, h)
    g.close()
    h.close()
    return dic_list, master_dic_list

def updateDictionary(list_of_words, add_or_subtract):
    """Keeps track of how often words occur in the lexicon, by adding or subtracting an instance from the dictionary entries for list_of_words."""
    for word in list_of_words:
        for dictionary in both_dictionaries:
            if dictionary.get(word) != None:
                if add_or_subtract == "add":
                    dictionary[word][0] += 1
                elif add_or_subtract == "subtract":
                    dictionary[word][0] -= 1
        for master_dic in master_dictionaries:
            if master_dic.get(word) != None:
                if add_or_subtract == "add":
                    master_dic[word][0] += 1
                elif add_or_subtract == "subtract":
                    master_dic[word][0] -= 1

def initializeLexicon():
    """Makes first lexicon from dictionary_1146 for leave_one_out classification."""
    nouns = list(dictionary_1146.keys())
    initial_nouns = random.sample(nouns, INITIAL_LEXICON_SIZE)
    f = open("indef_lexicon.txt", "w")
    for word in initial_nouns:                    # This loop does 3 things: it makes a wordlist to update the dictionary, it makes a line for each of those words, and it writes that line.
        line = lexicon_template[:]                  # Each line is filled with:
        line[0] = word[:]                           # -Wordform
        line[1] = dictionary_1146[word][1][:]       # -Plural/Singular
        line[2] = "0"                               # -Generation Number
        for i in range(3,len(lexicon_template)):    # -All features and 'class'
            line[i] = dictionary_1146[word][i][:]
        f.write(",".join(line)+"\n")
    f.close()
    updateDictionary(initial_nouns, "add")

def getPreviousProduction():
    """Gets previous generation's production from 2 sources: the output file of the TiMBL classification of indef nouns that also have definite representation(s), and the file with nouns that only have an indefinite exemplar."""
    f = open("indef_production.test.out", "r")
    output_list = f.readlines()
    f.close()
    g = open("excl_indef_production.txt", "r")
    excl_output_list = g.readlines()
    g.close()
    production_list = []
    word_list = []
    for line in output_list:
        llist = line[:-1].split(",")
        llist.pop(-1)
        noun = llist[0][:]
        for dictionary in both_dictionaries:
            if noun in dictionary:
                llist[-1] = dictionary[noun][-1][:]
                break
        production_list.append(llist)
        word_list.append(noun)
    for line2 in excl_output_list:
        llist2 = line2[:-1].split(",")
        llist2.pop(-1)
        production_list.append(llist2)
        word_list.append(llist2[0][:])
    updateDictionary(word_list, "add")
    return production_list

def getPreviousLexicon():
    """Converts previous indef_lexicon.txt file to a more useful structure"""
    f = open("indef_lexicon.txt", "r")
    prev_lexicon_list = f.readlines()
    f.close()
    prev_lexicon = []
    for i in prev_lexicon_list:
        i = i[:-1].split(",")
        prev_lexicon.append(i)
    return prev_lexicon

def getUnknownWords():
    candidate_list = []
    frequency_list = []
    total_freq = 0
    beginner_dict_empty = True
    for pair in master_dictionary_1146.items():
        if pair[1][0] == 0:
            candidate_list.append(pair[0][:])
            frequency_list.append(pair[1][2])
            total_freq += pair[1][2]
    if len(candidate_list) != 0:        # i.e. if some words in the beginner dictionary are not yet in the lexicon
        beginner_dict_empty = False
    unknown_words = []
    amount = 0
    if not beginner_dict_empty:        # i.e. if some words in the beginner dictionary are not yet in the lexicon
        if len(candidate_list) >= UNKNOWN_INPUT_SIZE:
            amount = UNKNOWN_INPUT_SIZE
            probability_list = [freq/total_freq for freq in frequency_list]
            new_words = list(choice(candidate_list, amount, replace=False, p=probability_list))
            unknown_words.extend(new_words)
            return unknown_words
        elif len(candidate_list) < UNKNOWN_INPUT_SIZE:
            amount = len(candidate_list)
            probability_list = [freq/total_freq for freq in frequency_list]
            new_words = list(choice(candidate_list, amount, replace=False, p=probability_list))
            unknown_words.extend(new_words)

    rem_amount = UNKNOWN_INPUT_SIZE - amount        # the following block of code applies if the beginner dictionary is completely out of unknown words or if the amount of unknown words in it was lower than the requested amount of unknown words
    candidate_list = []
    frequency_list = []
    total_freq = 0
    for pair in master_dictionary_remaining.items():
        if pair[1][0] == 0:
            candidate_list.append(pair[0][:])
            frequency_list.append(pair[1][2])
            total_freq += pair[1][2]
    probability_list = [f/total_freq for f in frequency_list]
    new_words = list(choice(candidate_list, rem_amount, replace=False, p=probability_list))
    unknown_words.extend(new_words)
    return unknown_words

def getKnownWords(amount):
    """Takes a variable describing how many tokens should be returned. Is used to get both input and output of known words."""
    candidate_list = []
    frequency_list = []
    total_freq = 0
    for dictionary in both_dictionaries:
        for pair in dictionary.items():
            if pair[1][0] != 0:
                candidate_list.append(pair[0][:])
                frequency_list.append(pair[1][2])
                total_freq += pair[1][2]
    probability_list = [f/total_freq for f in frequency_list]
    known_words = list(choice(candidate_list, amount, replace=True, p=probability_list))   # replace=True because it is quite normal for frequent words to be heard more than once a day. A subsequent version might incorporate 'burstiness' of word probability.
    return known_words

def getKnownInputWords(amount):
    """Takes a variable describing how many tokens should be returned. Is used to get both input and output of known words."""
    candidate_list = []
    frequency_list = []
    total_freq = 0
    for dictionary in master_dictionaries:
        for pair in dictionary.items():
            if pair[1][0] != 0:
                candidate_list.append(pair[0][:])
                frequency_list.append(pair[1][2])
                total_freq += pair[1][2]
    probability_list = [f/total_freq for f in frequency_list]
    known_words = list(choice(candidate_list, amount, replace=True, p=probability_list))   # replace=True because it is quite normal for frequent words to be heard more than once a day. A subsequent version might incorporate 'burstiness' of word probability.
    return known_words

def getNewInput():
    """Gets new tokens of both words that were in the previous lexicon AND words that weren't in the previous lexicon. For the first 1146 new words, it does this randomly. For the remaining words, it does this on the basis of their frequency in CELEX."""
    unkown_word_list = getUnknownWords()
    known_word_list = getKnownInputWords(KNOWN_INPUT_SIZE)
    new_word_list = unkown_word_list + known_word_list
    updateDictionary(new_word_list, "add")
    new_input_list = []
    f = open("indef_noun_input.txt", "w")
    for word in new_word_list:
        dic_value = dictionary_remaining.get(word)
        if dic_value == None:
            dic_value = dictionary_1146.get(word)
        line_list = [word, dic_value[1], str(GENERATION)] + dic_value[3:]
        new_input_list.append(line_list)
        f.write(",".join(line_list)+"\n")
    f.close()
    return new_input_list

def forgetOldTokens(overfull_lexicon):
    """Deletes oldest tokens of a word from the lexicon if the token count in the dictionaries reaches a certain threshold."""
    delete_list = []
    for dictionary in both_dictionaries:
        for pair in dictionary.items():
            if pair[1][0] > TOKEN_THRESHOLD:
                amount_over_threshold = pair[1][0] - TOKEN_THRESHOLD
                for i in range(amount_over_threshold):  # This adds multiple instances of the same word to the delete list if the token count exceeds the token threshold by more than 1.
                    delete_list.append(pair[0][:])
    if len(delete_list) > 0:                            # If there is anything to delete.
        for token in delete_list:
            candidate_list = []
            index_counter = 0
            for line in overfull_lexicon:
                if line[0] == token:
                    candidate = []
                    candidate.append(int(line[2]))  # gets the generation number
                    candidate.append(index_counter) # gets the index number of the line in the lexicon
                    candidate_list.append(candidate[:])
                index_counter += 1
            min_gen = min([i[0] for i in candidate_list])   # determines the earliest generation that occurs in the lexicon for this number
            for j in candidate_list:
                if j[0] == min_gen:
                    overfull_lexicon.pop(j[1])              # deletes the token with the lowest generation from the lexicon.
                    break                           # We need to break in case there are multiple candidates with the lowest generation number.
        updateDictionary(delete_list, "subtract")
    return overfull_lexicon                     # Which is no longer overfull.

def makeNewLexicon():
    """Combines previous_production, previous_lexicon, and new_input into a new lexicon training file for TiMBL."""
    temp_lexicon = previous_lexicon + previous_production + new_input
    new_lexicon = forgetOldTokens(temp_lexicon)
    f = open("indef_lexicon.txt", "w")      # Opens and empties the previous "indef_lexicon.txt" file.
    for line in new_lexicon:
        f.write(",".join(line))
        f.write("\n")
    f.close()

def makeNewDefProduction():
    """Chooses a new list of produced forms based on SUBTLEX frequencies, and constructs a text file out of that list that is added to the TiMBL test file by makeLexicon.py."""
    output_list = getKnownWords(OUTPUT_SIZE_DEF)
    f = open("def_production_from_indef.txt", "w")
    for token in output_list:
        dic_value = dictionary_remaining.get(token)
        if dic_value == None:
            dic_value = dictionary_1146.get(token)
        line_list = [token[:], dic_value[1], str(GENERATION+1)] + dic_value[3:]
        f.write(",".join(line_list)+"\n")
    f.close()

def makeNewIndefProduction():
    output_list = getKnownWords(OUTPUT_SIZE_INDEF)
    f = open("indef_production_from_indef.txt", "w")
    for token in output_list:
        dic_value = dictionary_remaining.get(token)
        if dic_value == None:
            dic_value = dictionary_1146.get(token)
        line_list = [token[:], dic_value[1], str(GENERATION+1)] + dic_value[3:]
        f.write(",".join(line_list)+"\n")
    f.close()

def saveUpdatedDictionary():
    """Saves the updated dictionary to disk."""
    g = open("dic_list_indef.pck", "wb")
    pickle.dump(both_dictionaries, g)
    g.close()
    h = open("master_dic_list.pck", "wb")
    pickle.dump(master_dictionaries, h)
    h.close()

################
# Main Program #
################

both_dictionaries, master_dictionaries = getDictionaries()
dictionary_1146 = both_dictionaries[0]
dictionary_remaining = both_dictionaries[1]
master_dictionary_1146 = master_dictionaries[0]
master_dictionary_remaining = master_dictionaries[1]

if GENERATION == 0:
    initializeLexicon()

elif GENERATION > 0 and GENERATION <= MAX_GENERATION:
    if GENERATION == 1:
        previous_production = []
    elif GENERATION != 1:
        previous_production = getPreviousProduction()
    previous_lexicon = getPreviousLexicon()
    new_input = getNewInput()
    makeNewLexicon()
    makeNewDefProduction()
    makeNewIndefProduction()

saveUpdatedDictionary()