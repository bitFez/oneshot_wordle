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
            if alphabet[ord(guess[j])-97]["colour"] in ["light", "secondary"]:
                alphabet[ord(guess[j])-97]["colour"]="warning"
            if guess[j] == target_word[j]:
                letter= '<button class="form-control clue_form_size btn btn-success fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
                alphabet[ord(guess[j])-97]["colour"]="success"
            row+=letter
        else:
            letter= '<button class="form-control clue_form_size btn btn-secondary fw-bold text-center text-light disabled" type="text", size="1">'+guess[j].upper()+'</button>'
            # Mark as dark only if it was light/secondary (user guessed a letter not in target)
            if alphabet[ord(guess[j])-97]["colour"] in ["light", "secondary"]:
                alphabet[ord(guess[j])-97]["colour"]="dark"
            row+=letter
    row+='</div>'      
    
    return row, alphabet

def get_clues_rows(clues, TARGET_WORD, **kwargs):
    difficulty= kwargs.get('difficulty', None)
    if difficulty=="hard":
        rowLen = 6
    else:
        rowLen = 5
    alphabet = {0:{'colour':'light', 'letter':'a','id':'id_alphabet-0-l_color'}, 
                1:{'colour':'light', 'letter':'b', 'id':'id_alphabet-1-l_color'},
                2:{'colour':'light', 'letter':'c','id':'id_alphabet-2-l_color'}, 
                3:{'colour':'light', 'letter':'d','id':'id_alphabet-3-l_color'},
                4:{'colour':'light', 'letter':'e','id':'id_alphabet-4-l_color'}, 
                5:{'colour':'light', 'letter':'f', 'id':'id_alphabet-5-l_color'},
                6:{'colour':'light', 'letter':'g','id':'id_alphabet-6-l_color'}, 
                7:{'colour':'light', 'letter':'h','id':'id_alphabet-7-l_color'},
                8:{'colour':'light', 'letter':'i','id':'id_alphabet-8-l_color'}, 
                9:{'colour':'light', 'letter':'j', 'id':'id_alphabet-9-l_color'},
                10:{'colour':'light', 'letter':'k', 'id':'id_alphabet-10-l_color'}, 
                11:{'colour':'light', 'letter':'l', 'id':'id_alphabet-11-l_color'},
                12:{'colour':'light', 'letter':'m', 'id':'id_alphabet-12-l_color'}, 
                13:{'colour':'light', 'letter':'n', 'id':'id_alphabet-13-l_color'},
                14:{'colour':'light', 'letter':'o', 'id':'id_alphabet-14-l_color'}, 
                15:{'colour':'light', 'letter':'p', 'id':'id_alphabet-15-l_color'},
                16:{'colour':'light', 'letter':'q', 'id':'id_alphabet-16-l_color'}, 
                17:{'colour':'light', 'letter':'r','id':'id_alphabet-17-l_color'},
                18:{'colour':'light', 'letter':'s', 'id':'id_alphabet-18-l_color'}, 
                19:{'colour':'light', 'letter':'t', 'id':'id_alphabet-19-l_color'},
                20:{'colour':'light', 'letter':'u', 'id':'id_alphabet-20-l_color'}, 
                21:{'colour':'light', 'letter':'v', 'id':'id_alphabet-21-l_color'},
                22:{'colour':'light', 'letter':'w', 'id':'id_alphabet-22-l_color'},
                23:{'colour':'light', 'letter':'x', 'id':'id_alphabet-23-l_color'}, 
                24:{'colour':'light', 'letter':'y', 'id':'id_alphabet-24-l_color'},
                25:{'colour':'light', 'letter':'z','id':'id_alphabet-25-l_color'}
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
                if alphabet[ord(ch) - 97]["colour"] in ["light", "secondary"]:
                    alphabet[ord(ch) - 97]["colour"] = "warning"
                row += letter
                cows.append(ch)
            else:
                letter = '<button class="form-control clue_form_size btn btn-secondary fw-bold text-center text-light disabled" type="text" size="1">' + ch.upper() + '</button>'
                # Keep as 'secondary' if it appears in clues but not in target
                if alphabet[ord(ch) - 97]["colour"] == "light":
                    alphabet[ord(ch) - 97]["colour"] = "secondary"
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

try:
    from nltk.corpus import wordnet as wn
    HAVE_WORDNET = True
except Exception:
    HAVE_WORDNET = False

def check_plural(word: str) -> bool:
    """
    Return True for tokens we should treat like plurals/invalid targets:
      - actual plural nouns (inflect detects)
      - past-tense forms ending with -ed
      - third-person singular verb forms ending with -s (best-effort via WordNet fallback)
    This intentionally does NOT special-case very short words because your lists are 5/6 letters.
    """
    if not word:
        return False

    w = word.strip()
    # strip surrounding punctuation
    w = re.sub(r"^[^\w]+|[^\w]+$", "", w)

    # ignore possessives ("cat's" is singular possessive) — keep as non-plural target
    if w.endswith("'s") or w.endswith("’s"):
        return False

    lw = w.lower()

    # quick reject: probable past-tense verbs
    if lw.endswith("ed"):
        return True

    # inflect: True if token is a plural noun
    try:
        if p.singular_noun(lw):
            return True
    except Exception:
        pass

    # if token ends with 's' it might be a 3rd-person verb form (annuls) — try WordNet if available
    if lw.endswith("s"):
        # check WordNet for verb senses of the token or its stem (drop final 's')
        stem = lw[:-1]
        if HAVE_WORDNET:
            try:
                if wn.synsets(lw, pos=wn.VERB) or wn.synsets(stem, pos=wn.VERB):
                    return True
            except Exception:
                # fall back to simple heuristic below
                pass
        # simple heuristic fallback: treat most -s endings as invalid (exclude) only if the stem looks like a verb:
        # we conservatively treat common endings that are NOT plural nouns as verbs (e.g. words ending 'ss','us','is')
        if any(lw.endswith(suf) for suf in ("ss", "us", "is")):
            return False
        # treat other -s endings as likely verb-form for purposes of excluding from daily target
        return True

    return False
