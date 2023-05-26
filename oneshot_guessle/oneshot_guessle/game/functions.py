from .models import Word,WordsHard

def guess_result(guess, target_word, alphabet):

    # Display the result of the guess
    row='<div class="btn-group">'
                    
    for j in range(0,len(target_word)):
        if guess[j] in target_word:
            letter= '<button class="form-control clue_form_size btn btn-warning fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
            if alphabet[ord(guess[j])-97]["colour"]=="secondary":
                alphabet[ord(guess[j])-97]["colour"]="warning"
            if guess[j] == target_word[j]:
                letter= '<button class="form-control clue_form_size btn btn-success fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
                alphabet[ord(guess[j])-97]["colour"]="success"
            row+=letter
        else:
            letter= '<button class="form-control clue_form_size btn btn-secondary fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
            row+=letter
    row+='</div>'      
    
    return row, alphabet

def get_clues_rows(clues, TARGET_WORD, **kwargs):
    difficulty= kwargs.get('difficulty', None)
    if difficulty=="hard":
        rowLen = 6
    else:
        rowLen = 5
    alphabet = {0:{'colour':'secondary', 'letter':'a','id':'id_alphabet-0-l_color'}, 
                1:{'colour':'secondary', 'letter':'b', 'id':'id_alphabet-1-l_color'},
                2:{'colour':'secondary', 'letter':'c','id':'id_alphabet-2-l_color'}, 
                3:{'colour':'secondary', 'letter':'d','id':'id_alphabet-3-l_color'},
                4:{'colour':'secondary', 'letter':'e','id':'id_alphabet-4-l_color'}, 
                5:{'colour':'secondary', 'letter':'f', 'id':'id_alphabet-5-l_color'},
                6:{'colour':'secondary', 'letter':'g','id':'id_alphabet-6-l_color'}, 
                7:{'colour':'secondary', 'letter':'h','id':'id_alphabet-7-l_color'},
                8:{'colour':'secondary', 'letter':'i','id':'id_alphabet-8-l_color'}, 
                9:{'colour':'secondary', 'letter':'j', 'id':'id_alphabet-9-l_color'},
                10:{'colour':'secondary', 'letter':'k', 'id':'id_alphabet-10-l_color'}, 
                11:{'colour':'secondary', 'letter':'l', 'id':'id_alphabet-11-l_color'},
                12:{'colour':'secondary', 'letter':'m', 'id':'id_alphabet-12-l_color'}, 
                13:{'colour':'secondary', 'letter':'n', 'id':'id_alphabet-13-l_color'},
                14:{'colour':'secondary', 'letter':'o', 'id':'id_alphabet-14-l_color'}, 
                15:{'colour':'secondary', 'letter':'p', 'id':'id_alphabet-15-l_color'},
                16:{'colour':'secondary', 'letter':'q', 'id':'id_alphabet-16-l_color'}, 
                17:{'colour':'secondary', 'letter':'r','id':'id_alphabet-17-l_color'},
                18:{'colour':'secondary', 'letter':'s', 'id':'id_alphabet-18-l_color'}, 
                19:{'colour':'secondary', 'letter':'t', 'id':'id_alphabet-19-l_color'},
                20:{'colour':'secondary', 'letter':'u', 'id':'id_alphabet-20-l_color'}, 
                21:{'colour':'secondary', 'letter':'v', 'id':'id_alphabet-21-l_color'},
                22:{'colour':'secondary', 'letter':'w', 'id':'id_alphabet-22-l_color'},
                23:{'colour':'secondary', 'letter':'x', 'id':'id_alphabet-23-l_color'}, 
                24:{'colour':'secondary', 'letter':'y', 'id':'id_alphabet-24-l_color'},
                25:{'colour':'secondary', 'letter':'z','id':'id_alphabet-25-l_color'}
                }
    cluesRow = []
    for clue in range(0,5):
        cows,bulls=[],[]
        row='<div class="btn-group">'
        word = clues[clue]                
        for j in range(0,rowLen):
            if word[j] == TARGET_WORD[j]:
                letter= '<button class="form-control clue_form_size btn btn-success fw-bold text-center text-light disabled" type="text", size="1">'+word[j].upper()+'</button>'
                alphabet[ord(word[j])-97]["colour"]="success"
                bulls.append(word[j])
                row+=letter
            elif (word[j] in TARGET_WORD) and (word[j] not in cows) and (word[j] not in bulls):
                letter= '<button class="form-control clue_form_size btn btn-warning fw-bold text-center text-light disabled" type="text", size="1">'+word[j].upper()+'</button>'
                if alphabet[ord(word[j])-97]["colour"]=="secondary":
                    alphabet[ord(word[j])-97]["colour"]="warning"
                row+=letter
                cows.append(word[j])
            else:
                letter= '<button class="form-control clue_form_size btn btn-secondary fw-bold text-center text-light disabled" type="text", size="1">'+word[j].upper()+'</button>'
                row+=letter
        row+='</div><br>'

        cluesRow.append(row)
    return cluesRow, alphabet

def get_random_clues(oneshotWord, **kwargs):
    difficulty= kwargs.get('difficulty', None)
    if difficulty=="easy":
        bulls_diff = 2
        cows_diff = 2
    elif difficulty=="hard":
        bulls_diff = 2
        cows_diff = 3
    else:
        bulls_diff = 1
        cows_diff = 3

    cows,bulls = [], []
    newclue=5
    # checks to make sure that there are no more than 1 correct placed guesses
    # and no more than 2 incorrect placed guesses
    cows_list = len(cows)
    bulls_list = len(bulls)
    while not(bulls_list == bulls_diff and cows_list ==cows_diff):
        cows,bulls = [], []
        if difficulty=="hard":
            clues = WordsHard.objects.order_by('?')
        else:
            clues = Word.objects.order_by('?')
        
        clue1,clue2,clue3,clue4,clue5 = clues[0],clues[1],clues[2],clues[3],clues[4]
        
        # This makes sure that none of the clues are the same as the daily word
        while clue1==oneshotWord:
            clue1=clues[newclue]
            newclue+=1
        while clue2==oneshotWord:
            clue2=clues[newclue]
            newclue+=1
        while clue3==oneshotWord:
            clue3=clues[newclue]
            newclue+=1
        while clue4==oneshotWord:
            clue4=clues[newclue]
            newclue+=1
        while clue5==oneshotWord:
            clue5=clues[newclue]
            newclue+=1
        clues_list = [clue1,clue2,clue3,clue4,clue5]
        
        print(f"oneshotword: {oneshotWord} -- Clues: {clues_list}")
        # checking for cows (letters that are in the word but not in the correct place
        for word in clues_list:
            for letter in word.word:
                if letter in oneshotWord:
                    if letter not in cows:
                        cows.append(letter)
        
        # checking for bulls (letters in a word that are in the correct place)
        for word in clues_list:
            
            for char in range(0,len(oneshotWord)):
                # checks if each character in the clues are in the same place as the daily word
                if word.word[char]==oneshotWord[char]:
                    # makes sure the letter is not already in the list of bulls
                    # before adding the word to the list
                    if word.word[char] not in bulls:
                        bulls.append(word.word[char])
                        # Checks if the bull is already in the cows. It should be!
                        if word.word[char] in cows:
                            # find the index position of the cow and remove it.
                            placement = cows.index(word.word[char])
                            cows.pop(placement)
                            
        cows_list = len(cows)
        bulls_list = len(bulls)                        
        
        # print(f"Cows: {cows_list} -- Bulls: {bulls_list}")
    return clues_list

