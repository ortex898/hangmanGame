import pygame
import random
import string

#Initialize Pygame
pygame.init()

#Screen setup
winHeight = 480
winWidth = 1000
win = pygame.display.set_mode((winWidth, winHeight))
pygame.display.set_caption("Adaptive AI Hangman")

#Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
LIGHT_BLUE = (102, 255, 255)

#Fonts
btn_font = pygame.font.SysFont("arial", 20)
guess_font = pygame.font.SysFont("monospace", 24)
lost_font = pygame.font.SysFont("arial", 45)

#Load hangman images
hangmanPics = [pygame.image.load(f'hangman{i}.png') for i in range(7)]

#Global variables
word = ''
buttons = []
guessed = []
limbs = 0
game_over = False
game_result_message = ""

#Load word list
with open('words.txt') as f:
    dictionary = [line.strip().lower() for line in f]

letter_stats = {l: [0, 0] for l in string.ascii_lowercase}


def redraw_game_window():
    win.fill(GREEN)

    #If game over, display result message
    if game_over:
        label = lost_font.render(game_result_message, 1, BLACK)
        word_reveal = lost_font.render(f'The word was: {word.upper()}', 1, BLACK)
        info = guess_font.render("Press any key to start a new game.", 1, BLACK)
        win.blit(label, (winWidth / 2 - label.get_width() / 2, 150))
        win.blit(word_reveal, (winWidth / 2 - word_reveal.get_width() / 2, 220))
        win.blit(info, (winWidth / 2 - info.get_width() / 2, 300))
        pygame.display.update()
        return

    #Draw buttons (letters)
    for button in buttons:
        if button[4]:
            pygame.draw.circle(win, BLACK, (button[1], button[2]), button[3])
            pygame.draw.circle(win, button[0], (button[1], button[2]), button[3] - 2)
            label = btn_font.render(chr(button[5]), 1, BLACK)
            win.blit(label, (button[1] - label.get_width() / 2, button[2] - label.get_height() / 2))

    #Draw guessed word
    spaced = spaced_out(word, guessed)
    label1 = guess_font.render(spaced, 1, BLACK)
    win.blit(label1, (winWidth / 2 - label1.get_width() / 2, 400))

    #Draw hangman image
    pic = hangmanPics[limbs]
    win.blit(pic, (winWidth / 2 - pic.get_width() / 2 + 20, 150))
    pygame.display.update()


def score(word_state, guessed, incorrect_guesses):
    revealed = len([c for c in word_state if c.isalpha()])
    return revealed - incorrect_guesses * 2


def minimax(word_state, guessed, depth, maximizing_player, incorrect_guesses):
    if depth == 0 or '_' not in word_state or incorrect_guesses >= 6:
        return score(word_state, guessed, incorrect_guesses)

    if maximizing_player:
        max_eval = float('-inf')
        for letter in string.ascii_lowercase:
            if letter not in guessed:
                new_guessed = guessed + [letter]
                new_word_state = spaced_out(word, new_guessed)
                new_incorrect_guesses = incorrect_guesses + (1 if letter not in word else 0)
                eval_val = minimax(new_word_state, new_guessed, depth - 1, False, new_incorrect_guesses)
                max_eval = max(max_eval, eval_val)
        return max_eval
    else:
        min_eval = float('inf')
        for letter in string.ascii_lowercase:
            if letter not in guessed:
                new_guessed = guessed + [letter]
                new_word_state = spaced_out(word, new_guessed)
                new_incorrect_guesses = incorrect_guesses + (1 if letter not in word else 0)
                eval_val = minimax(new_word_state, new_guessed, depth - 1, True, new_incorrect_guesses)
                min_eval = min(min_eval, eval_val)
        return min_eval


def update_letter_stats(word, actions):
    word_set = set(word)
    for letter in actions:
        letter = letter.lower()
        if letter in letter_stats:
            letter_stats[letter][1] += 1  
            if letter in word_set:
                letter_stats[letter][0] += 1  


def get_letter_success_rate(letter):
    correct, total = letter_stats[letter]
    if total == 0:
        return 0.5  
    return correct / total

def spaced_out(word, guessed=[]):
    return ' '.join(c.upper() if c == ' ' or c in guessed else '_' for c in word)

def get_candidate_words(current_pattern, guessed_letters, dictionary):
   
    pattern_letters = current_pattern.split()
    length = len(pattern_letters)
    revealed_letters = {c.lower() for c in pattern_letters if c != '_'}
    wrong_letters = {l for l in guessed_letters if l not in revealed_letters}
    
    candidates = []
    for w in dictionary:
        if len(w) != length:
            continue
        
        match = True
        for i, pchar in enumerate(pattern_letters):
            if pchar == '_':
                pass
            else:
                if w[i] != pchar.lower():
                    match = False
                    break
        
        if any(l in w for l in wrong_letters):
            match = False
                
        if match:
            candidates.append(w)
    return candidates


def ai_guess():
    
    current_pattern = spaced_out(word, guessed)
    candidates = get_candidate_words(current_pattern, guessed, dictionary)

    not_guessed = [l for l in string.ascii_lowercase if l not in guessed]

    if candidates and not_guessed:
        letter_frequency = {l:0 for l in not_guessed}
        for w in candidates:
            for ch in w:
                if ch in letter_frequency:
                    letter_frequency[ch] += 1

        best_letter = None
        best_freq = -1
        for l in letter_frequency:
            if letter_frequency[l] > best_freq:
                best_freq = letter_frequency[l]
                best_letter = l

        if best_letter is not None:
            return best_letter

    vowels = 'aeiou'
    vowel_candidates = [v for v in vowels if v in not_guessed]
    if vowel_candidates:
        vowel_candidates.sort(key=lambda v: get_letter_success_rate(v), reverse=True)
        return vowel_candidates[0]

    best_score = float('-inf')
    best_letter = None
    for letter in not_guessed:
        new_guessed = guessed + [letter]
        state_eval = minimax(spaced_out(word, new_guessed), new_guessed, 2, False, limbs)
        rate = get_letter_success_rate(letter)
        combined_eval = state_eval * rate
        if combined_eval > best_score:
            best_score = combined_eval
            best_letter = letter

    return best_letter if best_letter else random.choice(not_guessed)


def end_game(winner=False):
    global game_over, game_result_message
    # Update stats
    update_letter_stats(word, guessed)

    if winner:
        game_result_message = 'You Won!'
    else:
        game_result_message = 'You Lost!'
    game_over = True


def reset_game():
    global limbs, guessed, buttons, word, game_over
    limbs = 0
    guessed = []
    word = random.choice(dictionary)
    for button in buttons:
        button[4] = True
    game_over = False


#Set up buttons
increase = round(winWidth / 13)
for i in range(26):
    x = 25 + (increase * (i % 13))
    y = 40 if i < 13 else 85
    buttons.append([LIGHT_BLUE, x, y, 20, True, 65 + i])

#Start game
word = random.choice(dictionary)
in_play = True
clock = pygame.time.Clock()

while in_play:
    clock.tick(60) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            in_play = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                in_play = False
            if game_over:
                reset_game()

    if not game_over:
        if spaced_out(word, guessed).count('_') > 0 and limbs < 6:
            ai_letter = ai_guess()
            guessed.append(ai_letter)
            button_index = ord(ai_letter.upper()) - 65
            buttons[button_index][4] = False

            if ai_letter not in word:
                limbs += 1
                if limbs == 6:
                    end_game(winner=False)
            elif spaced_out(word, guessed).count('_') == 0:
                end_game(winner=True)
            
            pygame.time.wait(300)

    redraw_game_window()

pygame.quit()
