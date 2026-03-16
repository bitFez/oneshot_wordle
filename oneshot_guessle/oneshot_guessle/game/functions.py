from .models import Word,WordsHard
import re
import inflect
import random

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
    """Return five clue words for `oneshotWord`.

    New behaviour: pick one random clue plus four words that are more closely
    related to the target word. Relatedness is computed by a simple score:
    score = 3*bulls + cows (bulls = same-position matches, cows = unique shared
    letters excluding bulls). This produces clues that are more informative and
    generally easier for players.
    """
    difficulty = kwargs.get("difficulty", None)

    # Normalise target
    target = getattr(oneshotWord, "word", oneshotWord)
    target = str(target).lower()
    target_len = len(target)

    qs = WordsHard.objects if difficulty == "hard" else Word.objects

    # determine bulls cap: regular/default => 3, hard => 4, easy => no cap
    is_easy = difficulty == "easy"
    is_hard = difficulty == "hard"
    if is_easy:
        bulls_cap = None
    else:
        bulls_cap = 4 if is_hard else 3

    # sample a batch of candidates randomly for scoring (avoid iterating entire DB)
    sample_size = 200
    sample_qs = list(qs.order_by("?")[:sample_size])

    # build candidate words of the same length and not equal to target
    candidates = []
    for cand in sample_qs:
        cand_word = str(getattr(cand, "word", cand)).lower()
        if cand_word == target:
            continue
        if len(cand_word) != target_len:
            continue
        candidates.append(cand_word)

    # if sampling didn't yield enough candidates, fall back to scanning the DB
    if len(candidates) < 10:
        candidates = []
        for cand in qs.all():
            cand_word = str(getattr(cand, "word", cand)).lower()
            if cand_word == target:
                continue
            if len(cand_word) != target_len:
                continue
            candidates.append(cand_word)

    # if still not enough, return simple fallback list
    if not candidates:
        return []

    # compute similarity scores for each candidate
    scored = []
    # also track bulls letters per candidate to allow enforcing caps later
    bulls_letters_map = {}
    for cand in candidates:
        bulls_letters = {cand[i] for i in range(min(len(cand), target_len)) if cand[i] == target[i]}
        bulls = len(bulls_letters)
        # cows: unique letters in cand that appear in target but not counted as bulls
        cows_set = set()
        for i, ch in enumerate(cand):
            if i < len(target) and ch == target[i]:
                continue
            if ch in target:
                cows_set.add(ch)
        cows = len(cows_set)
        score = bulls * 3 + cows
        scored.append((cand, score, bulls, cows))
        bulls_letters_map[cand] = bulls_letters

    # sort descending by score
    scored.sort(key=lambda x: x[1], reverse=True)

    # choose top candidates (keep some headroom for randomness)
    top_pool = [s[0] for s in scored[:20]] if len(scored) > 20 else [s[0] for s in scored]

    # pick primary + related according to difficulty
    related = []
    if difficulty == "easy":
        # easy: pick the highest-scoring candidate as primary (most informative)
        primary = top_pool[0] if top_pool else random.choice(candidates)
        # prepare accumulated bull positions and letters from primary
        primary_positions = {i for i, ch in enumerate(primary) if i < target_len and ch == target[i]}
        accumulated_positions = set(primary_positions)
        accumulated_bulls = set(bulls_letters_map.get(primary, set()))
        for w in top_pool:
            if w == primary:
                continue
            # bulls letters and positions for candidate
            w_bulls = bulls_letters_map.get(w, set())
            w_positions = {i for i, ch in enumerate(w) if i < target_len and ch == target[i]}
            # enforce bulls cap for non-easy modes
            if bulls_cap is not None and len(accumulated_bulls.union(w_bulls)) > bulls_cap:
                continue
            # skip candidate if adding it would reveal all positions
            if len(accumulated_positions.union(w_positions)) == target_len:
                continue
            if w not in related:
                related.append(w)
                accumulated_positions.update(w_positions)
                accumulated_bulls.update(w_bulls)
            if len(related) == 4:
                break
    else:
        # regular (default): pick one random primary and then the top related words
        # try to pick a random primary that will allow keeping total unique bulls <= 3
        # fallback to any random primary after a few attempts
        max_primary_attempts = 10
        primary = None
        for _ in range(max_primary_attempts):
            cand_primary = random.choice(candidates)
            primary_bulls = set(bulls_letters_map.get(cand_primary, set()))
            if bulls_cap is None or len(primary_bulls) <= bulls_cap:
                primary = cand_primary
                break
        if primary is None:
            primary = random.choice(candidates)

        # accumulate bulls letters and add related words only if they don't push unique bulls > 3
        accumulated_bulls = set(bulls_letters_map.get(primary, set()))
        # also track bull positions to avoid revealing full word
        primary_positions = {i for i, ch in enumerate(primary) if i < target_len and ch == target[i]}
        accumulated_positions = set(primary_positions)
        for w in top_pool:
            if w == primary:
                continue
            # bulls letters for candidate
            w_bulls = bulls_letters_map.get(w, set())
            # bull positions for candidate
            w_positions = {i for i, ch in enumerate(w) if i < target_len and ch == target[i]}
            # if adding this candidate would exceed allowed unique bulls, skip it
            if bulls_cap is not None and len(accumulated_bulls.union(w_bulls)) > bulls_cap:
                continue
            # if adding this candidate would reveal all positions, skip it
            if len(accumulated_positions.union(w_positions)) == target_len:
                continue
            if w not in related:
                related.append(w)
                accumulated_bulls.update(w_bulls)
                accumulated_positions.update(w_positions)
            if len(related) == 4:
                break

    # if there aren't enough related words, pad from candidates
    if len(related) < 4:
        # build current accumulated bulls and positions from primary + related
        current_positions = {i for i, ch in enumerate(primary) if i < target_len and ch == target[i]}
        current_bulls = set(bulls_letters_map.get(primary, set()))
        for r in related:
            current_positions.update({i for i, ch in enumerate(r) if i < target_len and ch == target[i]})
            current_bulls.update(bulls_letters_map.get(r, set()))

        for w in candidates:
            if w == primary or w in related:
                continue
            w_positions = {i for i, ch in enumerate(w) if i < target_len and ch == target[i]}
            w_bulls = bulls_letters_map.get(w, set())
            # enforce bulls cap when present
            if bulls_cap is not None and len(current_bulls.union(w_bulls)) > bulls_cap:
                continue
            # ensure adding won't reveal full word
            if len(current_positions.union(w_positions)) == target_len:
                continue
            related.append(w)
            current_positions.update(w_positions)
            current_bulls.update(w_bulls)
            if len(related) == 4:
                break

    clues_list = [primary] + related[:4]
    # If easy mode accidentally reveals all positions across the five clues,
    # attempt to repair by replacing/removing one related word so the union of
    # bull positions is strictly less than the target length.
    def revealed_positions_for_list(lst):
        pos = set()
        for w in lst:
            for i, ch in enumerate(w):
                if i < target_len and ch == target[i]:
                    pos.add(i)
        return pos

    # repair loop (only necessary for easy mode but safe to run generally)
    positions = revealed_positions_for_list(clues_list)
    if len(positions) == target_len:
        # try to replace one related word with a less-revealing candidate
        pool = top_pool + [w for w in candidates if w not in top_pool]
        # ensure uniqueness
        pool = [w for w in pool if w not in clues_list]

        replaced = False
        # try each related slot to see if a replacement exists
        for idx in range(len(related)):
            # build baseline positions excluding this related
            baseline = revealed_positions_for_list([primary] + [r for j, r in enumerate(related[:4]) if j != idx])
            for cand in pool:
                cand_pos = {i for i, ch in enumerate(cand) if i < target_len and ch == target[i]}
                if len(baseline.union(cand_pos)) < target_len:
                    # perform replacement
                    related[idx] = cand
                    replaced = True
                    break
            if replaced:
                break

        if not replaced:
            # as a fallback, remove the related word that contributes the most new
            # positions and then attempt to pad with any candidate that doesn't
            # complete the set of positions.
            contrib = []
            base_primary = revealed_positions_for_list([primary])
            for r in related[:4]:
                contrib.append((r, len(revealed_positions_for_list([primary, r]) - base_primary)))
            # sort by contribution descending and drop the highest contributor
            contrib.sort(key=lambda x: x[1], reverse=True)
            if contrib:
                to_remove = contrib[0][0]
                related = [r for r in related if r != to_remove]

            # rebuild current positions and try to pad with safe candidates
            current_positions = revealed_positions_for_list([primary] + related)
            for cand in pool:
                if cand in related:
                    continue
                cand_pos = {i for i, ch in enumerate(cand) if i < target_len and ch == target[i]}
                if len(current_positions.union(cand_pos)) == target_len:
                    continue
                related.append(cand)
                current_positions.update(cand_pos)
                if len(related) >= 4:
                    break

    # ensure we return a list of strings
    return list([primary] + related[:4])

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
