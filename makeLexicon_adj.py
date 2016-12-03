import sys, string, pickle, random
from numpy.random import choice

#############
# Variables #
#############

PARTICIPANT = int(sys.argv[1])
#PARTICIPANT = 1

GENERATION = int(sys.argv[2])
#GENERATION = 0

MAX_PARTICIPANT = int(sys.argv[3])

MAX_GENERATION = int(sys.argv[4])
#MAX_GENERATION = 1

INITIAL_LEXICON_SIZE = 120

if GENERATION <= 300:
    if GENERATION%3 == 0:
        NEW_UNKNOWN_INPUT = 1
    else:
        NEW_UNKNOWN_INPUT = 0
elif GENERATION > 300:
    if GENERATION%2 == 0:
        NEW_UNKNOWN_INPUT = 1
    else:
        NEW_UNKNOWN_INPUT = 0

KNOWN_INPUT_SIZE = 200 - NEW_UNKNOWN_INPUT
OUTPUT_SIZE = 30

TOKEN_THRESHOLD = 5

#############
# Functions #
#############

def makeDictionary(file_name):
    f = open(file_name, "r")
    line_list = f.readlines()
    f.close()

    template = ["number of instances in lexicon", "Probability", "=","=","=", "=","=","=", "=","=","=", "=","=","=", "=","=","="]
    dictionary = {}

    for i in line_list:
        i2 = i[:-1]
        line=i2.split(',')
        key = line[0]
        syls = line[3]
        phons = line[2]
        dictionary[key] = template[:]
        dictionary[key][0] = 0
        freq = int(line[1])
        if freq == 0:
            freq = 1
        dictionary[key][1] = freq
        syls_list = syls.split('-')
        phons_list = phons.split('-')
        for j in range(len(syls_list)-1):
            if len(syls_list[j]) != len(phons_list[j]):
                if syls_list[j] in["VC","CVC","CCVC","CCCVC"]:
                    syls_list[j] = syls_list[j][:-1]
        syls_new = '-'.join(syls_list)
        syls_rev = syls_new[::-1]
        phons_rev = phons[::-1]
        counter_for_insert = 0
        counter = 0
        insert_string = ""
        prev_k = ""
        for k in syls_rev:
            if prev_k != k:
                insert_string = ""
            if k == "C":
                if prev_k == "V" or prev_k == "-":
                    counter_for_insert +=1
                    if counter_for_insert > 14:
                        break
                insert_string = "".join([phons_rev[counter], insert_string])
                dictionary[key][(len(template)-1)-counter_for_insert] = insert_string
            if k == "V":
                if prev_k == "C" or prev_k == "":
                    counter_for_insert +=1
                    if counter_for_insert > 14:
                        break
                    insert_string = "".join([phons_rev[counter]])
                    dictionary[key][(len(template)-1)-counter_for_insert] = insert_string
                if prev_k == "-":
                    counter_for_insert +=2
                    if counter_for_insert > 14:
                        break
                    insert_string = "".join([phons_rev[counter]])
                    dictionary[key][(len(template)-1)-counter_for_insert] = insert_string
                if prev_k == "V":
                    counter -= 1
            prev_k = k[:]
            counter += 1
    return dictionary

def getDictionaries():
    try:
        g = open("adjective_dict_list.pck", "rb")
        adj_dict_list = pickle.load(g)
    except:
        dictionary1 = makeDictionary("first_195_adjectives_final.txt")
        dictionary2 = makeDictionary("remaining_adjectives_final.txt")
        adj_dict_list = [dictionary1, dictionary2]
        g = open("adjective_dict_list.pck", "wb")
        pickle.dump(adj_dict_list, g)
    g.close()
    return adj_dict_list

def updateDictionary(list_of_words, add_or_subtract):
    """Keeps track of how often words occur in the lexicon, by adding or subtracting an instance from the dictionary entries for list_of_words."""
    for word in list_of_words:
        for dictionary in all_adjectives:
            if dictionary.get(word) != None:
                if add_or_subtract == "add":
                    dictionary[word][0] += 1
                elif add_or_subtract == "subtract":
                    dictionary[word][0] -= 1

def getArticleAndEnding(definiteness, adjective, noun, noun_plural, noun_classification):
    if definiteness == "indef":
        if noun_plural == "N":
            article = "een"
        elif noun_plural == "Y":
            article = "="
        if noun_classification == "de":
            ending = "schwa"
        elif noun_classification == "het":
            ending = "0"
    elif definiteness == "def":
        article = noun_classification[:]
        ending = "schwa"

    dic_key = remaining_605.get(adjective)
    if dic_key != None:
        transcription = remaining_605[adjective][2:]
    elif dic_key == None:
        transcription = first_195[adjective][2:]
    for vowel in ["@","e","i","a"]:                                             # exceptions due to phonology
        if transcription[-2:] == [vowel,'=']:
            ending = "0"
    if adjective in ["gratis", "super", "live", "standaard", "eersteklas"]:     # exceptions due to history / borrowing
        ending = "0"
    return article, ending, transcription

def initializeLexicon():
    f = open("lexicon.train", "r")
    lines = f.readlines()
    f.close()
    correct_lines = random.sample(lines, int(INITIAL_LEXICON_SIZE / 4))
    correct_nouns = []
    for line in correct_lines:
        line_list = line[:-1].split(",")
        new_list = [line_list[0], line_list[1], line_list[-1]]
        correct_nouns.append(new_list)

    g = open("production.test.out", "r")
    lines2 = g.readlines()
    g.close()
    output_lines = random.sample(lines2, int(INITIAL_LEXICON_SIZE / 4))
    output_nouns = []
    for line2 in output_lines:
        line_list2 = line2[:-1].split(",")
        new_list2 = [line_list2[0], line_list2[1], line_list2[-1]]
        output_nouns.append(new_list2)

    i = open("indef_lexicon.txt", "r")
    lines3 = i.readlines()
    i.close()
    indef_lines = random.sample(lines3, int(INITIAL_LEXICON_SIZE / 2))
    indef_nouns = []
    for line3 in indef_lines:
        line_list3 = line3[:-1].split(",")
        new_list3 = [line_list3[0], line_list3[1], line_list3[-1]]
        indef_nouns.append(new_list3)

    adjectives = list(first_195.keys())
    initial_adjectives = random.sample(adjectives, INITIAL_LEXICON_SIZE)

    h = open("adj_lexicon.train", "w")

    for adj in initial_adjectives:
        if len(correct_nouns) > 0:
            noun = correct_nouns.pop()
            def_indef = "def"
        elif len(correct_nouns) == 0 and len(output_nouns) > 0:
            noun = output_nouns.pop()
            def_indef = "def"
        else:
            noun = indef_nouns.pop()
            def_indef = "indef"

        article, classification, adjective_phon = getArticleAndEnding(def_indef, adj, noun[0], noun[1], noun[2])
        if def_indef == "indef":
            lexicon_line = [adj] + [str(GENERATION)] + [article] + adjective_phon + [noun[0], "="] + [classification]
        elif def_indef == "def":
            lexicon_line = [adj] + [str(GENERATION)] + [article] + adjective_phon + [noun[0], noun[2]] + [classification]
        h.write(",".join(lexicon_line)+"\n")
    updateDictionary(initial_adjectives, "add")
    h.close()

def makeExperimentSet():
    f = open("stimuli_adj.txt", "r")
    lines = f.readlines()
    f.close()
    adjectives = [line[:-1] for line in lines]
    adjectives_copy = adjectives[:]

    g = open("experiment.test.out", "r")
    lines2 = g.readlines()
    noun_lists = [line[:-1].split(",") for line in lines2]

    h = open("adj_experiment.test", "w")
    for noun_list in noun_lists:
        if len(adjectives) > 0:
            adjective = adjectives.pop(adjectives.index(random.choice(adjectives)))
        elif len(adjectives) == 0:
            adjective = adjectives_copy.pop(adjectives_copy.index(random.choice(adjectives_copy)))
        if noun_list[-2] == "de":
            classification = "schwa"
        elif noun_list[-2] == "het":
            classification = "0"
        experiment_line_list = [adjective, "Experiment", "een"] + first_195[adjective][2:] + [noun_list[0], noun_list[-1], classification]
        h.write(",".join(experiment_line_list) + "\n")
    h.close()

def getPreviousProduction():
    """Converts output from TiMBL classification to a structure that can be added to the lexicon"""
    f = open("adj_production.test.out", "r")
    output_list = f.readlines()
    f.close()
    production_list = []
    word_list = []
    for line in output_list:
        line_list = line[:-1].split(",")
        line_list.pop(-2)
        production_list.append(line_list)
        word_list.append(line_list[0][:])
    updateDictionary(word_list, "add")
    return production_list

def getPreviousLexicon():
    """Converts previous adj_lexicon.train file to a more useful structure"""
    f = open("adj_lexicon.train", "r")
    prev_lexicon_list = f.readlines()
    f.close()
    prev_lexicon = []
    for line in prev_lexicon_list:
        line_list = line[:-1].split(",")
        prev_lexicon.append(line_list)
    return prev_lexicon

def getUnknownWord():
    candidate_list = []
    freq_list = []
    total_freq = 0
    for pair in first_195.items():
        if pair[1][0] == 0:
            candidate_list.append(pair[0][:])
            freq_list.append(pair[1][1])
            total_freq += pair[1][1]
    if len(candidate_list) != 0:        # i.e. if some words in the beginner dictionary are not yet in the lexicon
        probability_list = [freq/total_freq for freq in freq_list]
        new_word = list(choice(candidate_list, 1, replace=True, p=probability_list))
        return new_word
    else:                               # i.e. if all words in the beginner dictionary occur at least once in the lexicon
        candidate_list = []
        freq_list = []
        total_freq = 0
        for pair in remaining_605.items():
            if pair[1][0] == 0:
                candidate_list.append(pair[0][:])
                freq_list.append(pair[1][1])
                total_freq += pair[1][1]
        probability_list = [freq/total_freq for freq in freq_list]
        new_word = list(choice(candidate_list, 1, replace=True, p=probability_list))
        return new_word

def getKnownWords(amount):
    """Takes a variable describing how many tokens should be returned. Is used to get both input and output of known words. In the future this function will take a list of nouns as an argument. This way the adjectives that frequently occur with those nouns can be chosen."""
    candidate_list = []
    frequency_list = []
    total_freq = 0
    for dictionary in all_adjectives:
        for pair in dictionary.items():
            if pair[1][0] != 0:
                candidate_list.append(pair[0][:])
                frequency_list.append(pair[1][1])
                total_freq += pair[1][1]
    probability_list = [f/total_freq for f in frequency_list]
    known_words = list(choice(candidate_list, amount, replace=True, p=probability_list))   # replace=True because it is quite normal for frequent words to be heard more than once a day. A subsequent version might incorporate 'burstiness' of word probability.
    return known_words

def getNewInput():
    """Gets new tokens of both words that were in the previous lexicon AND words that weren't in the previous lexicon. It does this randomly. In the future this selection should be based on the 2-gram frequency of adjective-noun pair."""
    if NEW_UNKNOWN_INPUT == 1:
        unkown_word_list = getUnknownWord()
    elif NEW_UNKNOWN_INPUT == 0:
        unkown_word_list = []
    known_word_list = getKnownWords(KNOWN_INPUT_SIZE)
    new_word_list = unkown_word_list + known_word_list
    updateDictionary(new_word_list, "add")

    f = open("noun_input.txt", "r")
    def_noun_lines = f.readlines()
    f.close()
    def_noun_lists = [def_noun_line[:-1].split(",") for def_noun_line in def_noun_lines]
    def_noun_triplets = [[def_choice[0], def_choice[1], def_choice[-1]] for def_choice in random.sample(def_noun_lists, int((KNOWN_INPUT_SIZE+NEW_UNKNOWN_INPUT)/2))]

    g = open("indef_noun_input.txt", "r")
    indef_noun_lines = g.readlines()
    g.close()
    indef_noun_lists = [indef_noun_line[:-1].split(",") for indef_noun_line in indef_noun_lines]
    indef_noun_triplets = [[indef_choice[0], indef_choice[1], indef_choice[-1]] for indef_choice in random.sample(indef_noun_lists, int((KNOWN_INPUT_SIZE+NEW_UNKNOWN_INPUT)/2))]

    new_input_list = []
    for word in new_word_list:
        if len(def_noun_triplets) != 0:
            noun_triplet = def_noun_triplets.pop()
            def_indef = "def"
        elif len(def_noun_triplets) == 0:
            noun_triplet = indef_noun_triplets.pop()
            def_indef = "indef"
        article, classification, adjective_phon = getArticleAndEnding(def_indef, word, noun_triplet[0], noun_triplet[1], noun_triplet[2])
        if def_indef == "def":
            line_list = [word, str(GENERATION), article] + adjective_phon + [noun_triplet[0], noun_triplet[2]] + [classification]
        elif def_indef == "indef":
            line_list = [word, str(GENERATION), article] + adjective_phon + [noun_triplet[0], "="] + [classification]
        new_input_list.append(line_list)
    return new_input_list

def forgetOldTokens(overfull_lexicon):
    """Deletes oldest tokens of a word from the lexicon if the token count in the dictionaries reaches a certain threshold."""
    delete_list = []
    for dictionary in all_adjectives:
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
                    candidate.append(int(line[1]))  # gets the generation number
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
    f = open("adj_lexicon.train", "w")      # Opens and empties the previous "adj_lexicon.train" file.
    for line in new_lexicon:
        f.write(",".join(line)+"\n")
    f.close()

def makeNewProduction():
    """Chooses a new list of produced forms based on SUBTLEX frequencies, and constructs a test file out of that list for classification by TiMBL."""
    output_list = getKnownWords(OUTPUT_SIZE)

    f = open("production.test.out", "r")
    def_noun_lines = f.readlines()
    f.close()
    def_noun_lists = [def_noun_line[:-1].split(",") for def_noun_line in def_noun_lines]
    def_noun_triplets = [[def_noun_choice[0], def_noun_choice[1], def_noun_choice[-1]] for def_noun_choice in random.sample(def_noun_lists, int(OUTPUT_SIZE/2))]

    g = open("indef_production.test.out", "r")
    indef_noun_lines1 = g.readlines()
    g.close()
    h = open("excl_indef_production.txt")
    indef_noun_lines2 = h.readlines()
    h.close()
    indef_noun_lines = indef_noun_lines1 + indef_noun_lines2
    indef_noun_lists = [indef_noun_line[:-1].split(",") for indef_noun_line in indef_noun_lines]
    indef_noun_triplets = [[indef_noun_choice[0], indef_noun_choice[1], indef_noun_choice[-1]] for indef_noun_choice in random.sample(indef_noun_lists, int(OUTPUT_SIZE/2))]

    i = open("adj_production.test", "w")
    for adjective in output_list:
        if len(def_noun_triplets) > 0:
            noun_triplet = def_noun_triplets.pop()
            def_indef = "def"
        elif len(def_noun_triplets) == 0:
            noun_triplet = indef_noun_triplets.pop()
            def_indef = "indef"
        if noun_triplet[2] == "=":                                              # this indicates that the noun in question only occurs in the indefinite noun lexicon and thus does not have an abstract "de/het" feature.
            article, classification, adjective_phon = getArticleAndEnding(def_indef, adjective, noun_triplet[0], noun_triplet[1], "de")             # the classification that comes out of getArticleAndEnding() doesn't actually matter as it gets replaced by the TiMBL classfication it is only added because test and training files need to have the same format.
        else:
            article, classification, adjective_phon = getArticleAndEnding(def_indef, adjective, noun_triplet[0], noun_triplet[1], noun_triplet[2])
        line_list = [adjective, str(GENERATION), article] + adjective_phon + [noun_triplet[0], noun_triplet[2]] + [classification]
        i.write(",".join(line_list)+"\n")
    i.close()

def getPreviousResults():
    h = open("adj_experiment.test.out", "r")
    result_lines = h.readlines()
    h.close()
    N_total = 0
    N_schwa_instead_of_zero = 0
    N_zero_instead_of_schwa = 0
    N_correct = 0
    for line in result_lines:
        line = line[:-1]
        line_list = line.split(",")
        correct_answer = line_list[-2]
        actual_answer = line_list[-1]
        if correct_answer == "schwa":
            if actual_answer == "0":
                N_zero_instead_of_schwa += 1
            elif actual_answer == "schwa":
                N_correct += 1
        elif correct_answer == "0":
            if actual_answer == "schwa":
                N_schwa_instead_of_zero += 1
            elif actual_answer == "0":
                N_correct += 1
        N_total += 1
    prev_results = [N_zero_instead_of_schwa, N_schwa_instead_of_zero, N_correct, N_total]
    return prev_results

def processExperimentResults():
    """Loads the outputfile of the previous generation's test set, matches the classification to the correct articles, calculates percentages for types of errors and accuracy, and writes those to a datastructure."""
    previous_results = getPreviousResults()
    if PARTICIPANT == 1 and GENERATION == 2:
        results_dict = {PARTICIPANT:{GENERATION-1:previous_results}}
        f = open("adj_results.pck", "wb")
        pickle.dump(results_dict, f)
        f.close()
    else:
        g = open("adj_results.pck", "rb")
        results_dict = pickle.load(g)
        g.close()
        if (GENERATION-1)==1:
            results_dict[PARTICIPANT] = {GENERATION-1:previous_results}
        else:
            results_dict[PARTICIPANT][GENERATION-1] = previous_results
        h = open("adj_results.pck", "wb")
        pickle.dump(results_dict, h)
        h.close()
    return results_dict

def saveUpdatedDictionary():
    """Saves the updated dictionary to disk."""
    g = open("adjective_dict_list.pck", "wb")
    pickle.dump(all_adjectives, g)
    g.close()

def makeExceptionsSet():
    list_of_exceptions = []
    for dictionary in all_adjectives:
        for adjective in dictionary:
            for vowel in ["@", "e", "i", "a"]:
                if dictionary[adjective][-2:] == [vowel,"="]:
                    adjective_phon = dictionary[adjective][2:]
                    list_of_exceptions.append([adjective, adjective_phon])
            if adjective in ["gratis", "super", "live", "standaard", "eersteklas"]:
                adjective_phon = dictionary[adjective][2:]
                list_of_exceptions.append([adjective, adjective_phon])

    num_of_de_nouns = int(len(list_of_exceptions) / 2)
    num_of_het_nouns = len(list_of_exceptions) - num_of_de_nouns
    f = open("first_1146_nouns_final.txt", "r")
    noun_lines = f.readlines()
    f.close()
    noun_lists = [noun_line[:-1].split(",") for noun_line in noun_lines]
    de_pairs = [[noun_list[0],noun_list[-1]] for noun_list in noun_lists if noun_list[1] == "N" and noun_list[-1] == "de"]
    het_pairs =[[noun_list[0],noun_list[-1]] for noun_list in noun_lists if noun_list[1] == "N" and noun_list[-1] == "het"]

    g = open("adj_exceptions.test", "w")
    for adj_phon_pair in list_of_exceptions:
        if num_of_de_nouns > 0:
            noun_pair = random.choice(de_pairs)
            de_pairs.remove(noun_pair)
            num_of_de_nouns -= 1
        elif num_of_de_nouns == 0:
            noun_pair = random.choice(het_pairs)
            het_pairs.remove(noun_pair)
        adj = adj_phon_pair[0]
        phon = adj_phon_pair[1]
        article = "een"
        classification = "0"
        write_list = [adj, "Exception", article] + phon + noun_pair + [classification]
        g.write(",".join(write_list)+"\n")
    g.close()

def getExceptionsAccuracy():
    f = open("adj_exceptions.test.out", "r")
    lines = f.readlines()
    f.close()
    result_lists = [line[:-1].split(",") for line in lines]

    num_of_items = 0
    num_correct = 0
    for result in result_lists:
        num_of_items += 1
        if result[-1] == result[-2]:                                            # oftewel als het antwoord "0" is
            num_correct += 1
    accuracy = num_correct / num_of_items * 100

    if PARTICIPANT == 1:
        g = open("exceptions_results_test.csv", "w")
        g.write("Particpant,Accuracy\n")
        g.write(str(PARTICIPANT)+","+str(accuracy)+"\n")
        g.close()
    elif PARTICIPANT > 1:
        g = open("exceptions_results_test.csv", "a")
        g.write(str(PARTICIPANT)+","+str(accuracy)+"\n")
        g.close()

def provideExperimentSummary():
    """Takes individual results and provides a per generation overview of mistakes and accuracy across all simulated participants."""
    f = open("test_run_adjectives_k1_w1_mO_n3_g1460_in200_out30_mem5.csv", "w")
    f.write("Participant,Generation,perc_zero_instead_of_schwa,perc_schwa_instead_of_zero,Accuracy\n")

    for participant in range(1,MAX_PARTICIPANT+1):
        for generation in range(1, MAX_GENERATION+1):
            perc_zero_instead_of_schwa = results[participant][generation][0] / (results[participant][generation][3] / 2) * 100
            perc_schwa_instead_of_zero = results[participant][generation][1] / (results[participant][generation][3] / 2) * 100
            accuracy = results[participant][generation][2] / results[participant][generation][3] * 100
            result_line = [str(participant), str(generation), str(perc_zero_instead_of_schwa), str(perc_schwa_instead_of_zero), str(accuracy)]
            f.write(",".join(result_line)+"\n")
    f.close()

################
# Main Program #
################

all_adjectives = getDictionaries()
first_195 = all_adjectives[0]
remaining_605 = all_adjectives[1]

if GENERATION == 0:
    initializeLexicon()

elif GENERATION > 0 and GENERATION <= MAX_GENERATION:
    makeExperimentSet()                                                         # Every generation a new experiment set (i.e. new combinations of the 10 nouns and 8 adjectives) is made because Blom et al. are not clear about which combinations were used in the original experiment.
    previous_production = getPreviousProduction()
    previous_lexicon = getPreviousLexicon()
    new_input = getNewInput()
    makeNewLexicon()
    makeNewProduction()
    if GENERATION > 1:
        processExperimentResults()
    if GENERATION == MAX_GENERATION:
        makeExceptionsSet()

elif GENERATION > MAX_GENERATION:
    results = processExperimentResults()
    getExceptionsAccuracy()
    if PARTICIPANT == MAX_PARTICIPANT:
        provideExperimentSummary()

saveUpdatedDictionary()
