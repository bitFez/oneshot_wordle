from .models import Word,WordsHard
import re
import inflect

p = inflect.engine()

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

    # normalize target once
    target_text = getattr(TARGET_WORD, "word", TARGET_WORD)
    target_text = str(target_text or "").lower()
    target_len = len(target_text)

    for clue_index in range(0, 5):
        cows, bulls = [], []
        row = '<div class="btn-group">'

        # normalize candidate (could be model instance or plain string)
        item = clues[clue_index]
        word_text = getattr(item, "word", item)
        word_text = str(word_text or "").lower()

        # compare only up to the min of target_len and actual candidate length
        compare_len = min(len(word_text), target_len, rowLen)

        for j in range(0, compare_len):
            ch = word_text[j]
            if ch == target_text[j]:
                letter = '<button class="form-control clue_form_size btn btn-success fw-bold text-center text-light disabled" type="text" size="1">' + ch.upper() + '</button>'
                alphabet[ord(ch) - 97]["colour"] = "success"
                bulls.append(ch)
                row += letter
            elif (ch in target_text) and (ch not in cows) and (ch not in bulls):
                letter = '<button class="form-control clue_form_size btn btn-warning fw-bold text-center text-light disabled" type="text" size="1">' + ch.upper() + '</button>'
                if alphabet[ord(ch) - 97]["colour"] == "secondary":
                    alphabet[ord(ch) - 97]["colour"] = "warning"
                row += letter
                cows.append(ch)
            else:
                letter = '<button class="form-control clue_form_size btn btn-secondary fw-bold text-center text-light disabled" type="text" size="1">' + ch.upper() + '</button>'
                if alphabet[ord(ch) - 97]["colour"] == "secondary":
                    alphabet[ord(ch) - 97]["colour"] = "dark"
                row += letter

        # if word shorter than rowLen, pad remaining positions with empty/neutral buttons
        if compare_len < rowLen:
            for _ in range(compare_len, rowLen):
                row += '<button class="form-control clue_form_size btn btn-secondary fw-bold text-center text-light disabled" type="text" size="1">&nbsp;</button>'

        row += '</div><br>'
        cluesRow.append(row)

    return cluesRow, alphabet

def get_random_clues(oneshotWord, **kwargs):
    """
        This function will cycle through clues until it produces a clues list that matches the 
        setting for the difficulty of the word. eg:
        easy: 2 yellow, 2 green clues
        normal: 1 green, 2 yellow clues
        hard: 2 green ,3 yellow clues
    """
    difficulty = kwargs.get("difficulty", None)
    if difficulty == "easy":
        bulls_diff, cows_diff = 2, 2
    elif difficulty == "hard":
        bulls_diff, cows_diff = 2, 3
    else:
        bulls_diff, cows_diff = 1, 3

    # This normalises the target word to a plain string. If the object 
    # is a model instance, it extracts the word as a string from the model.
    target = getattr(oneshotWord, "word", oneshotWord)
    target = str(target).lower()
    target_len = len(target)

    qs = WordsHard.objects if difficulty == "hard" else Word.objects

    max_attempts = 50
    attempt = 0
    while attempt < max_attempts:
        attempt += 1

        # sample a number of random candidates (slice to avoid huge query materialisation)
        sample = list(qs.order_by("?")[:20])
        # build clues_list of candidates that are not the target and same length as target
        clues_list = []
        for cand in sample:
            cand_word = str(getattr(cand, "word", cand)).lower()
            if cand_word == target:
                continue
            if len(cand_word) != target_len:
                continue
            # store the plain word string (simpler for downstream rendering)
            clues_list.append(cand_word)
            if len(clues_list) == 5:
                break

        # if we didn't collect 5 valid clues, try again
        if len(clues_list) < 5:
            continue

        # compute cows (unique letters in candidates that appear in target) and bulls (correct-position letters)
        cows = []
        bulls = []
        for cand in clues_list:
            cand_word = str(getattr(cand, "word", cand)).lower()
            # cows: any letter in candidate that's in target (add uniquely)
            for letter in cand_word:
                if letter in target and letter not in cows:
                    cows.append(letter)
            # bulls: same-position matches (safe because lengths match)
            for i in range(target_len):
                if cand_word[i] == target[i] and cand_word[i] not in bulls:
                    bulls.append(cand_word[i])
                    # ensure bull not counted also as cow
                    if cand_word[i] in cows:
                        cows.remove(cand_word[i])

        if len(bulls) == bulls_diff and len(cows) == cows_diff:
            # ensure we return a list of strings
            assert isinstance(clues_list, (list, tuple)), "get_random_clues must return a list"
            return list(clues_list)

    # fallback: gather the first 5 matching-length non-target words from DB
    fallback = []
    for cand in qs.all():
        cand_word = str(getattr(cand, "word", cand)).lower()
        if cand_word == target:
            continue
        if len(cand_word) != target_len:
            continue
        fallback.append(cand_word)
        if len(fallback) == 5:
            break

    return fallback

def check_plural(word: str) -> bool:
    """
    Heuristic plural check using inflect with safe normalisation and common exceptions.
    Returns True for likely plurals, False otherwise.
    """
    if not word:
        return False

    w = word.strip()

    # strip surrounding punctuation
    w = re.sub(r"^[^\w]+|[^\w]+$", "", w)

    # ignore possessives ("cat's" is singular possessive)
    if w.endswith("'s") or w.endswith("’s"):
        return False

    # short tokens are unlikely plurals
    if len(w) <= 2:
        return False

    # common uncountable/exception words that look plural but are not
    exceptions = {"news", "series", "species", "information", "offspring", "sheep", "fish"}
    if w.lower() in exceptions:
        return False

    # Use inflect on the lowercased token (inflect expects lowercase for best results)
    try:
        return bool(p.singular_noun(w.lower()))
    except Exception:
        # on any unexpected error, treat as non-plural to avoid excluding words
        return False
