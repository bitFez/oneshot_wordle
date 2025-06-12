import requests

SCRABBLE_LETTER_VALUES = {
        'A': 1, 'E': 1, 'I': 1, 'O': 1, 'N': 1, 'R': 1, 'T': 1, 'L': 1, 'S': 1, 'U': 1,
        'D': 2, 'G': 2,
        'B': 3, 'C': 3, 'M': 3, 'P': 3,
        'F': 4, 'H': 4, 'V': 4, 'W': 4, 'Y': 4,
        'K': 5,
        'J': 8, 'X': 8,
        'Q': 10, 'Z': 10
    }

SCORE_NUMBERS = {
    1:"1️⃣", 2:"2️⃣", 3:"3️⃣", 4:"4️⃣", 5:"5️⃣",
    6:"6️⃣", 7:"7️⃣", 8:"8️⃣", 9:"9️⃣", 10:"🔟",
}

def check_word_definition(word):
    """
    Checks if a word exists in the dictionary and returns its definition.
    Returns None if the word doesn't exist or API fails.
    """
    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        
        # Successful response (word exists)
        if response.status_code == 200:
            data = response.json()
            # Get the first definition from the first meaning
            definition = data[0]['meanings'][0]['definitions'][0]['definition']
            return definition
        
        # Word not found
        elif response.status_code == 404:
            return None
        
    except (requests.exceptions.RequestException, KeyError, IndexError):
        # Handle API errors or malformed responses
        return None



def process_valid_submissions(valid_submissions:list):
    """
    Processes valid submissions from the user.
    
    """
    print("process_valid_submissions called with:", valid_submissions)
    score = 0
    score_breakdown = []
    score_breakdown_numbers = []
    definitions = []
    words = []
    for submission in valid_submissions:
        word = "".join(submission)
        result_definition = check_word_definition(word)
        if result_definition:
            temp = ""
            for letter in word:
                value = SCRABBLE_LETTER_VALUES[letter.upper()]
                score += value
                temp += SCORE_NUMBERS[value]
            score_breakdown.append(temp)
            score_breakdown_numbers.append(score)
            definitions.append(result_definition)
            words.append(f"{word} {temp} : {result_definition}")
        else:
            score_breakdown.append("0️⃣0️⃣0️⃣0️⃣0️⃣")
            score_breakdown_numbers.append(0)
            words.append(f"{word}  0️⃣0️⃣0️⃣0️⃣0️⃣ : Not found in dictionary")
    score_breakdown.append(f"Total Score: {score}")
    return score_breakdown, score_breakdown_numbers, definitions, words