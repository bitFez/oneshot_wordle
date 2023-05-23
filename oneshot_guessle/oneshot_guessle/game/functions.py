from .models import Word,WordsHard

def guess_result(guess, target_word, alphabet):

    # Display the result of the guess
    row='<div class="btn-group">'
                    
    for j in range(0,len(target_word)):
        letter_color = 'l'+str(j+1)+'_color'
        if guess[j] in target_word:
            letter= '<button class="form-control clue_form_size btn btn-warning fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
            if alphabet[f'{guess[j]}']=="secondary":
                alphabet[f'{guess[j]}']="warning"
            #alphabet_formset[ord(clues[clue][j])-97].cleaned_data['l_color'] = 'btn-warning'
            if guess[j] == target_word[j]:
                letter= '<button class="form-control clue_form_size btn btn-success fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
                alphabet[f'{guess[j]}']="success"
                #alphabet_formset[ord(clues[clue][j])-97].cleaned_data['l_color'] = 'btn-success'
            row+=letter
        else:
            letter= '<button class="form-control clue_form_size btn btn-secondary fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
            #alphabet_formset[ord(clues[clue][j])-97].cleaned_data['l_color'] = 'btn-secondary'
            row+=letter
    row+='</div>'      
    
    return row, alphabet

def get_clues_rows(clues, TARGET_WORD, **kwargs):
    difficulty= kwargs.get('difficulty', None)
    if difficulty=="hard":
        rowLen = 6
    else:
        rowLen = 5
    alphabet = {'id_alphabet-0-l_color':{'colour':'secondary', 'letter':'a'}, 'id_alphabet-1-l_color':{'colour':'secondary', 'letter':'b'},
                'id_alphabet-2-l_color':{'colour':'secondary', 'letter':'c'},'id_alphabet-3-l_color':{'colour':'secondary', 'letter':'d'},
                'id_alphabet-4-l_color':{'colour':'secondary', 'letter':'e'},'id_alphabet-5-l_color':{'colour':'secondary', 'letter':'f'},
                'id_alphabet-6-l_color':{'colour':'secondary', 'letter':'g'},'id_alphabet-7-l_color':{'colour':'secondary', 'letter':'h'},
                'id_alphabet-8-l_color':{'colour':'secondary', 'letter':'i'},'id_alphabet-9-l_color':{'colour':'secondary', 'letter':'j'},
                'id_alphabet-10-l_color':{'colour':'secondary', 'letter':'k'},'id_alphabet-11-l_color':{'colour':'secondary', 'letter':'l'},
                'id_alphabet-12-l_color':{'colour':'secondary', 'letter':'m'},'id_alphabet-13-l_color':{'colour':'secondary', 'letter':'n'},
                'id_alphabet-14-l_color':{'colour':'secondary', 'letter':'o'},'id_alphabet-15-l_color':{'colour':'secondary', 'letter':'p'},
                'id_alphabet-16-l_color':{'colour':'secondary', 'letter':'q'},'id_alphabet-17-l_color':{'colour':'secondary', 'letter':'r'},
                'id_alphabet-18-l_color':{'colour':'secondary', 'letter':'s'},'id_alphabet-19-l_color':{'colour':'secondary', 'letter':'t'},
                'id_alphabet-20-l_color':{'colour':'secondary', 'letter':'u'},'id_alphabet-21-l_color':{'colour':'secondary', 'letter':'v'},
                'id_alphabet-22-l_color':{'colour':'secondary', 'letter':'x'},'id_alphabet-23-l_color':{'colour':'secondary', 'letter':'y'},
                'id_alphabet-24-l_color':{'colour':'secondary', 'letter':'z'}
                }
    cluesRow = []
    for clue in range(0,5):
        cows,bulls=[],[]
        row='<div class="btn-group">'
        guess = clues[clue]                
        for j in range(0,rowLen):
            letter_color = 'l'+str(j+1)+'_color'
            if guess[j] == TARGET_WORD[j]:
                letter= '<button class="form-control clue_form_size btn btn-success fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
                alphabet[f'[0]{guess[j]}']="success"
                # alphabet_formset[ord(guess[j])-97].data['l_color'] = 'btn-success'
                bulls.append(guess[j])
                row+=letter
            elif guess[j] in TARGET_WORD and guess[j] not in cows and guess[j] not in bulls:
                letter= '<button class="form-control clue_form_size btn btn-warning fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
                if alphabet[f'{guess[j]}']=="secondary":
                    alphabet[f'{guess[j]}']="warning"
                # alphabet_formset[ord(guess[j])-97].data['l_color'] = 'btn-warning'
                row+=letter
                cows.append(guess[j])
            else:
                letter= '<button class="form-control clue_form_size btn btn-secondary fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
                # alphabet_formset[ord(guess[j])-97].data['l_color'] = 'btn-secondary'
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

