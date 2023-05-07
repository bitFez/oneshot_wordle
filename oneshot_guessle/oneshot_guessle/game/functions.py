

def guess_result(guess, target_word):
    # Display the result of the guess
    row='<div class="btn-group">'
                    
    for j in range(0,5):
        letter_color = 'l'+str(j+1)+'_color'
        if guess[j] in target_word:
            letter= '<button style="height:60px;width:60px;" class="form-control btn btn-warning fw-bold text-center text-light fs-5 disabled" type="text", size="1">'+guess[j].upper()+'</button>'
            #alphabet_formset[ord(clues[clue][j])-97].cleaned_data['l_color'] = 'btn-warning'
            if guess[j] == target_word[j]:
                letter= '<button style="height:60px;width:60px;" class="form-control btn btn-success fw-bold text-center text-light fs-5 disabled" type="text", size="1">'+guess[j].upper()+'</button>'
                #alphabet_formset[ord(clues[clue][j])-97].cleaned_data['l_color'] = 'btn-success'
            row+=letter
        else:
            letter= '<button style="height:60px;width:60px;" class="form-control btn btn-secondary fw-bold text-center text-light fs-5 disabled" type="text", size="1">'+guess[j].upper()+'</button>'
            #alphabet_formset[ord(clues[clue][j])-97].cleaned_data['l_color'] = 'btn-secondary'
            row+=letter
    row+='</div><br>'      
    
    return row