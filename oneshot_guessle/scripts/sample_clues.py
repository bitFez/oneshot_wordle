import json
import random
import os

BASE = os.path.dirname(os.path.dirname(__file__))
DICT_PATH = os.path.join(BASE, 'oneshot_guessle', 'game', 'dicts', '5-letter-words.json')

def load_words():
    with open(DICT_PATH, 'r', encoding='utf8') as f:
        data = json.load(f)
    return [item['word'].lower() for item in data if len(item.get('word','')) == 5]

def sample_clues_for_target(target, candidates, sample_size=200, mode="regular"):
    target = target.lower()
    target_len = len(target)

    # sample candidates
    if len(candidates) > sample_size:
        sample = random.sample(candidates, sample_size)
    else:
        sample = list(candidates)

    # remove target and length mismatch
    sample = [w for w in sample if w != target and len(w) == target_len]
    if not sample:
        return []

    scored = []
    for cand in sample:
        bulls = sum(1 for i in range(min(len(cand), target_len)) if cand[i] == target[i])
        cows_set = set()
        for i, ch in enumerate(cand):
            if ch == target[i]:
                continue
            if ch in target:
                cows_set.add(ch)
        cows = len(cows_set)
        score = bulls * 3 + cows
        scored.append((cand, score, bulls, cows))

    scored.sort(key=lambda x: x[1], reverse=True)
    top_pool = [s[0] for s in scored[:20]] if len(scored) > 20 else [s[0] for s in scored]

    related = []
    if mode == "easy":
        # pick the best-scoring word as primary, then next best as related
        primary = top_pool[0] if top_pool else random.choice(sample)
        for w in top_pool:
            if w == primary:
                continue
            if w not in related:
                related.append(w)
            if len(related) == 4:
                break
    else:
        # regular: pick one random primary and then top related
        primary = random.choice(sample)
        for w in top_pool:
            if w == primary:
                continue
            if w not in related:
                related.append(w)
            if len(related) == 4:
                break

    if len(related) < 4:
        for w in sample:
            if w == primary or w in related:
                continue
            related.append(w)
            if len(related) == 4:
                break

    return [primary] + related[:4]

def main():
    random.seed(1)
    words = load_words()
    examples = random.sample(words, 10)
    for t in examples:
        clues_regular = sample_clues_for_target(t, words, mode="regular")
        clues_easy = sample_clues_for_target(t, words, mode="easy")
        print(f"TARGET: {t}")
        print(f"  regular: {clues_regular}")
        print(f"  easy:    {clues_easy}\n")

if __name__ == '__main__':
    main()
