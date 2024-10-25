import math
import statistics as stats
import matplotlib.pyplot as plt
import os

def open_addresses(file):
    with open(file) as f:
        lines = f.readlines()
        lines =  [line.strip() for line in lines]
        return lines

def get_president_tokens(line):
    name, date, terms = '', None,  None
    words = line.split()
    for i in words:    
        if i.isalpha():
            name += ' '  + i
        elif i.isdigit():
            if int(i) < 5:
                terms = int(i)
            else:
                date = int(i)
    president = {'name': name, 'terms': terms, 'date': date}
    return president, date

def load_addresses(lines):
    president  = {'name': '', 'date': '', 'terms': ''}
    speechs, dates, presidents = [], [], []
    current_speech, current_date, current_president  = '', 0, None
    for line in lines:
        if line.startswith('$'):
            if current_president:
                speechs.append(current_speech)
                dates.append(current_date)
                presidents.append(current_president)
            current_president, current_date = get_president_tokens(line)
            current_speech = ''
        elif current_president:
            current_speech += line + ' '
    return speechs, dates, presidents

def get_large(word):
    length = 0
    large = 0
    for char in word:
        if char.isalpha():
            length += 1
    if  length > 7:
        large = 1
    return large

def get_syllables(word):
    vowels = 'aeiou'
    word = word.lower()
    vowel_count = sum(1 for char in word if char in vowels)
    if word.endswith('e'):
        vowel_count -= 1
    
    diphthongs = ["au", "oy", "oo"]
    triphthongs = ["iou"]

    for diphthong in diphthongs:
        if diphthong in word:
            vowel_count -= 1
            break
    
    for triphthong in triphthongs:
        if triphthong in word:
            vowel_count -= 1
            break
    
    if word.endswith("le") or word.endswith("les"):
        if len(word) > 2 and word[-3] not in vowels:
            vowel_count += 1

    return max(vowel_count, 0)

def get_counts(speeches):
    sentences, wordcounts, wordlengths,  wordspersentence, lettersperwords, largewords, largewordspercentage, syllables, syllablesperword = [], [], [], [], [], [], [], [], []
    for speech in speeches:
        current_large = 0
        current_syllables = 0
        words = speech.split()
        wordslen = len(words)
        for word in words:
            current_syllables += get_syllables(word)
            current_large  += get_large(word)
        
        # get syllables
        syllables.append(current_syllables)
        syllablesperword.append(current_syllables/wordslen)
        for syllable  in syllablesperword:
            print(syllable)
        # get words that are greater than 7
        largewords.append(current_large)
        # get the percentage of words  that are greater than 7
        largewordspercentage.append((current_large/wordslen)*100)
        # get the number of words
        wordcounts.append(len(words))
        # get the total length of the words that are in the alphabet
        total_word_length = sum(len(word) for word in words if word.isalpha())
        wordlengths.append(total_word_length)
        # gets the setence count
        sentence_count = sum(1 for char in speech if char in '.!?')
        sentences.append(sentence_count)
        # gets the words per setence
        wordspersentence.append(wordslen/sentence_count)
        # gets the percentage of letters per word
        lettersperwords.append((total_word_length/wordslen))
    
    return sentences, wordcounts, wordlengths,  wordspersentence, lettersperwords,  largewords, largewordspercentage,  syllables, syllablesperword

def get_stats(counts):
    mean, median, std = stats.mean(counts),  stats.median(counts), stats.stdev(counts)
    return mean, median, std

def split(counts, dates, splitdate):
    beforecounts, aftercounts = [], []
    for count, date in zip(counts, dates):
        if date < splitdate:
            beforecounts.append(count)
        else:
            aftercounts.append(count)

    return beforecounts, aftercounts

def get_gaussian(x, mean, std):
    return 1/(std*(2*math.pi)**(.5)) * math.e**(-.5*((x-mean)/std)**2)

def calculate_gaussian(counts):
    mean, median, stddev = get_stats(counts) if counts else (0, 0, 0)
    start = int(mean - 2 * stddev)
    stop = int(mean + 2 * stddev)
    distribution = list(range(start, stop))
    gaussian_values = [get_gaussian(x, mean, stddev) for x in distribution]
    return distribution, gaussian_values

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def plot(bmean, bmedian, bstd, amean, amedian, astd, counts, dates, title, splitdate):
    directory = f'graphs/{title}'
    plt.figure()
    before = [1789, splitdate]
    after = [splitdate, 2021]
    
    plt.plot(dates, counts)
    # before
    plt.plot(before, [bmean, bmean], 'y', label='Mean')
    plt.plot(before, [bmedian, bmedian], 'r', label='Median')
    plt.plot(before, [bmean + bstd, bmean + bstd], 'g', label='Standard Dev')
    plt.plot(before, [bmean - bstd, bmean - bstd], 'g')
    # after
    plt.plot(after, [amean, amean], 'y')
    plt.plot(after, [amedian, amedian], 'r')
    plt.plot(after, [amean + astd, amean + astd], 'g')
    plt.plot(after, [amean - astd, amean - astd], 'g')

    plt.legend()
    plt.xlabel(title)
    check_dir(directory)
    plt.savefig(f'{directory}/Date Vs {title}')    

def plot_gauss(bdistribution, bgaussian_values, adistribution, agaussian_values, title):
    directory = f'graphs/{title}'
    plt.figure()

    # print(f"{title}\nBefore")
    # print(bdistribution)
    # print(bgaussian_values)
    # print(f"{title}\nAfter")
    # print(adistribution)
    # print(bgaussian_values)

    plt.plot(bdistribution, bgaussian_values, label='Before 1937', color='blue')
    plt.plot(adistribution, agaussian_values, label='After 1937', color='orange')
    plt.title(f'graphs/Gaussian Distribution of {title}')
    plt.xlabel(title)
    plt.ylabel('graphs/Probability Density')
    plt.legend()
    check_dir(directory)
    plt.savefig(f'{directory}/Gaussian {title}')

def graph(counts, dates, title):
    splitdate = 1937
    beforecounts, aftercounts = split(counts, dates, splitdate)
    mean, median, std  = get_stats(counts)
    bmean,  bmedian, bstd = get_stats(beforecounts)
    amean,  amedian, astd = get_stats(aftercounts)
    distribution, gaussian_values = calculate_gaussian(counts)
    bdistribution, bgaussian_values = calculate_gaussian(beforecounts)
    adistribution, agaussian_values = calculate_gaussian(aftercounts)
    print(title)
    # for date  in dates:
        # print(f'date: {date},  counts: {counts[dates.index(date)]}')
    plot(bmean, bmedian, bstd, amean, amedian, astd, counts, dates, title, splitdate)
    plot_gauss(bdistribution, bgaussian_values, adistribution, agaussian_values, title)

def main():
    check_dir("graphs")
    lines = open_addresses('addresses.txt')
    speechs, dates, presidents = load_addresses(lines)
    sentences, wordcounts, wordlengths,  wordspersentence, lettersperwords, largewords, largewordspercentage, syllables, syllablesperword = get_counts(speechs)
    graph(sentences, dates, 'Sentences')
    graph(wordcounts, dates, 'Words')
    graph(lettersperwords, dates,  'Word Lengths')
    graph(wordlengths , dates, 'Letters')
    graph(wordspersentence,  dates, 'Words per Sentence')
    graph(largewords,  dates, 'Large Words')
    graph(largewordspercentage, dates, 'Large Words Percentage')
    graph(syllables,  dates, 'Syllables')
    graph(syllablesperword, dates, 'Syllables per Word')
main()