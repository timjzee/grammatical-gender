import sys, string, pickle, random
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

INITIAL_LEXICON_SIZE = 600

# In a later version the relatively arbitrary parameters below could be a function of GENERATION.

if GENERATION <= 980:
    UNKNOWN_INPUT_SIZE = 2
elif GENERATION > 980:
    UNKNOWN_INPUT_SIZE = 3
KNOWN_INPUT_SIZE = 400 - UNKNOWN_INPUT_SIZE
OUTPUT_SIZE = 100
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
        lab = line[-1]
        plur = line[1]
        dictionary[key] = template[:]
        dictionary[key][-1] = lab[:]
        dictionary[key][1] = plur[:]
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
        g = open("dic_list.pck", "rb")
        dic_list = pickle.load(g)
    except:
        dictionary1 = makeDictionary("first_1146_nouns_final.txt")
        dictionary2 = makeDictionary("remaining_nouns_final.txt")
        dic_list = [dictionary1, dictionary2]
        g = open("dic_list.pck", "wb")
        pickle.dump(dic_list, g)
    g.close()
    return dic_list

def updateDictionary(list_of_words, add_or_subtract):
    """Keeps track of how often words occur in the lexicon, by adding or subtracting an instance from the dictionary entries for list_of_words."""
    for word in list_of_words:
        for dictionary in both_dictionaries:
            if dictionary.get(word) != None:
                if add_or_subtract == "add":
                    dictionary[word][0] += 1
                elif add_or_subtract == "subtract":
                    dictionary[word][0] -= 1

def initializeLexicon():
    """Makes first lexicon from dictionary_1146 for leave_one_out classification."""
    wordlist = []
    wordcount = 0
    f = open("lexicon.train", "w")
    for word in dictionary_1146:                    # This loop does 3 things: it makes a wordlist to update the dictionary, it makes a line for each of those words, and it writes that line.
        wordcount += 1
        line = lexicon_template[:]                  # Each line is filled with:
        line[0] = word[:]                           # -Wordform
        line[1] = dictionary_1146[word][1][:]       # -Plural/Singular
        line[2] = "0"                               # -Generation Number
        for i in range(3,len(lexicon_template)):    # -All features and class for TiMBL
            line[i] = dictionary_1146[word][i][:]
        f.write(",".join(line))
        f.write("\n")
        wordlist.append(word[:])
        if wordcount == INITIAL_LEXICON_SIZE:       # Semi-random for each participant because order of dictionary is different every time it is created?
            break
    f.close()
    updateDictionary(wordlist, "add")

def makeExperimentSet():                                  # The result of these classification is not fed back into the lexicon as the original study was synchronic: i.e the different age groups consisted of different participants.
    """Makes a (very) small test set that is used to measure the accuracy in every generation; this simulates the materials used in the experiment by Blom et al. 2008."""
    f = open("stimuli.txt", "r")
    stimuli_list = f.readlines()
    f.close()
    g = open("experiment.test", "w")
    for stimulus in stimuli_list:
        stimulus = stimulus[:-1]
        line = [stimulus, dictionary_1146[stimulus][1], "Experiment"] + dictionary_1146[stimulus][3:]
        g.write(",".join(line)+"\n")
    g.close()

def getPreviousProduction():
    """Converts output from TiMBL classification to a structure that can be added to the lexicon"""
    f = open("production.test.out", "r")
    output_list = f.readlines()
    f.close()
    production_list = []
    word_list = []
    for i in output_list:
        i = i[:-1].split(",")
        i.pop(-2)
        production_list.append(i)
        word_list.append(i[0][:])
    updateDictionary(word_list, "add")
    return production_list

def getPreviousLexicon():
    """Converts previous lexicon.train file to a more useful structure"""
    f = open("lexicon.train", "r")
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
    for pair in dictionary_1146.items():
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
    for pair in dictionary_remaining.items():
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

def getNewInput():
    """Gets new tokens of both words that were in the previous lexicon AND words that weren't in the previous lexicon. For the first 1146 new words, it does this randomly. For the remaining words, it does this on the basis of their frequency in CELEX."""
    unkown_word_list = getUnknownWords()
    known_word_list = getKnownWords(KNOWN_INPUT_SIZE)
    new_word_list = unkown_word_list + known_word_list
    updateDictionary(new_word_list, "add")
    new_input_list = []
    f = open("noun_input.txt", "w")
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
    f = open("lexicon.train", "w")      # Opens and empties the previous "lexicon.train" file.
    for line in new_lexicon:
        f.write(",".join(line))
        f.write("\n")
    f.close()

def makeNewProduction():
    """Chooses a new list of produced forms based on SUBTLEX frequencies, and constructs a test file out of that list for classification by TiMBL."""
    output_list = getKnownWords(OUTPUT_SIZE)
    f = open("production.test", "w")
    for token in output_list:
        dic_value = dictionary_remaining.get(token)
        if dic_value == None:
            dic_value = dictionary_1146.get(token)
        line_list = [token[:], dic_value[1], str(GENERATION+1)] + dic_value[3:]
        f.write(",".join(line_list)+"\n")
    f.close()

def getPreviousResults():
    h = open("experiment.test.out", "r")
    result_lines = h.readlines()
    h.close()
    N_total = 0
    N_het_de = 0
    N_de_het = 0
    N_correct = 0
    for line in result_lines:
        line = line[:-1]
        line_list = line.split(",")
        answer = line_list[-2]
        result = line_list[-1]
        if answer == "de":
            if result == "het":
                N_het_de += 1
            elif result == "de":
                N_correct += 1
        elif answer == "het":
            if result == "de":
                N_de_het += 1
            elif result == "het":
                N_correct += 1
        N_total += 1
    prev_results = [N_het_de, N_de_het, N_correct, N_total]
    return prev_results

def processExperimentResults():
    """Loads the outputfile of the previous generation's test set, matches the classification to the correct articles, calculates percentages for types of errors and accuracy, and writes those to a datastructure."""
    previous_results = getPreviousResults()
    if PARTICIPANT == 1 and GENERATION == 2:
        results_dict = {PARTICIPANT:{GENERATION-1:previous_results}}
        f = open("results.pck", "wb")
        pickle.dump(results_dict, f)
        f.close()
    else:
        g = open("results.pck", "rb")
        results_dict = pickle.load(g)
        g.close()
        if (GENERATION-1)==1:
            results_dict[PARTICIPANT] = {GENERATION-1:previous_results}
        else:
            results_dict[PARTICIPANT][GENERATION-1] = previous_results
        h = open("results.pck", "wb")
        pickle.dump(results_dict, h)
        h.close()
    return results_dict

def saveUpdatedDictionary():
    """Saves the updated dictionary to disk."""
    g = open("dic_list.pck", "wb")
    pickle.dump(both_dictionaries, g)
    g.close()

def provideExperimentSummary():
    """Takes individual results and provides a per generation overview of mistakes and accuracy across all simulated participants."""
    f = open("test_run_nouns_k1_w0_mO_n3_g1460_in400_out100_mem5.csv", "w")
    f.write("Participant,Generation,perc_het_instead_of_de,perc_de_instead_of_het,Accuracy\n")
    for participant in range(1,MAX_PARTICIPANT+1):
        for generation in range(1, MAX_GENERATION+1):
            perc_het_instead_of_de = results[participant][generation][0] / (results[participant][generation][3] / 2) * 100
            perc_de_instead_of_het = results[participant][generation][1] / (results[participant][generation][3] / 2) * 100
            accuracy = results[participant][generation][2] / results[participant][generation][3] * 100
            result_line = [str(participant), str(generation), str(perc_het_instead_of_de), str(perc_de_instead_of_het), str(accuracy)]
            f.write(",".join(result_line)+"\n")
    f.close()

################
# Main Program #
################

both_dictionaries = getDictionaries()
dictionary_1146 = both_dictionaries[0]
dictionary_remaining = both_dictionaries[1]

if GENERATION == 0:
    initializeLexicon()
    if PARTICIPANT == 1:
        makeExperimentSet()

elif GENERATION > 0 and GENERATION <= MAX_GENERATION:
    previous_production = getPreviousProduction()
    previous_lexicon = getPreviousLexicon()
    new_input = getNewInput()
    makeNewLexicon()
    makeNewProduction()
    if GENERATION > 1:
        results = processExperimentResults()

elif GENERATION > MAX_GENERATION:
    results = processExperimentResults()
    if PARTICIPANT == MAX_PARTICIPANT:
        provideExperimentSummary()

saveUpdatedDictionary()
