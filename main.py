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
    length = len(word)
    if length > 7:
        return 1
    return 0

def get_rows(word, vowels):
    rows = []
    current_row = []
    for char in word:
        if char in vowels:
            current_row.append(char)
        else:
            if current_row:
                rows.append(current_row)
                current_row = []
    if current_row:
        rows.append(current_row)
    return rows

def get_syllables(word):
    vowels = 'aeiou'
    word = word.lower()
    vowel_count = sum(1 for char in word if char in vowels)

    if word.endswith('e'):
        vowel_count -= 1

    in_a_row = get_rows(word, vowels)
    for row in in_a_row:
        if len(row) > 1:
            vowel_count -= 1

    if word.endswith('le') or word.endswith('les'):
        if len(word) > 2 and word[-3] not in vowels:
            vowel_count += 1

    return max(0, vowel_count)

def get_counts(speeches):
    sentences, wordcounts, wordlengths,  wordspersentence, lettersperwords, largewords, largewordspercentage, syllables, syllablesperword, grade_level = [], [], [], [], [], [], [], [], [], []
    for speech in speeches:
        current_large = 0
        current_syllables = 0
        words = speech.split()
        wordslen = len(words)
        
        for word in words:
            current_syllables += get_syllables(word)
            current_large += get_large(word)

        syllables.append(current_syllables)
        syllablesperword.append(current_syllables / wordslen)
        largewords.append(current_large)
        largewordspercentage.append((current_large / wordslen) * 100)
        wordcounts.append(len(words))
        
        total_word_length = sum(len(word) for word in words if word.isalpha())
        wordlengths.append(total_word_length)
        
        sentence_count = sum(1 for char in speech if char in '.!?')
        sentences.append(sentence_count)
        
        wordspersentence.append(wordslen / sentence_count)
        lettersperwords.append(total_word_length / wordslen)
        grade_level.append(0.39 * (wordslen / sentence_count) + 11.8 * (current_syllables / wordslen) - 15.59)
        
    return sentences, wordcounts, wordlengths,  wordspersentence, lettersperwords,  largewords, largewordspercentage,  syllables, syllablesperword, grade_level

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

def calculate_gaussian(counts, mean, std):
    start = int(-2*std+mean)
    stop = int(2*std+mean) + 1
    sd1 = std + mean
    sd2 = mean - std
    distribution = []
    increment = abs(stop - start)/100
    print(increment)
    x = start
    while x < stop:
        distribution.append(x)
        x += increment
    gaussian = []
    for x in distribution:
        gaussian.append(get_gaussian(x, mean, std))
    return distribution, gaussian, sd1, sd2

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
    plt.close()   

def plot_gauss(bdistribution, bgaussian_values, adistribution, agaussian_values, title, bstd, astd, bsd1, bsd2, asd1, asd2, bmean, amean):
    directory = f'graphs/{title}'
    plt.figure()

    plt.plot(bdistribution, bgaussian_values, label='Before 1937', color='blue')
    plt.plot(adistribution, agaussian_values, label='After 1937', color='orange')

    plt.plot([bsd1, bsd1], [bgaussian_values[0], get_gaussian(bsd1, bmean, bstd)], color = 'green')
    plt.plot([bsd2, bsd2], [bgaussian_values[0], get_gaussian(bsd1, bmean, bstd)], color = 'green')
    plt.plot([asd1, asd1], [agaussian_values[0], get_gaussian(asd1, amean, astd)], color = 'green')
    plt.plot([asd2, asd2], [agaussian_values[0], get_gaussian(asd1, amean, astd)], color = 'green')
    plt.plot([bmean, bmean], [bgaussian_values[0], get_gaussian(bmean, bmean, bstd)])
    plt.plot([amean, amean], [agaussian_values[0], get_gaussian(amean, amean, astd)], color = 'red')

    plt.title(f'Gaussian Distribution of {title}')
    plt.xlabel(title)
    plt.ylabel('Probability Density')
    plt.legend()

    check_dir(directory)
    plt.savefig(f'{directory}/Gaussian {title}')
    plt.close()

def sub_plot(counts, dates, title):
    directory = f'graphs/{title}'
    grades = [9, 13, 16]
    fig = plt.figure()
    rows = len(counts)
    axs = fig.subplots(nrows=rows, ncols=1, sharex = True, sharey=False)
    
    for i in range(rows):
        axs[i].plot(dates, counts[i])
    
    for grade in grades:
        axs[1].plot([1789, 2021], [grade, grade], label = f"grade {grade}")

    plt.legend()
    plt.xlabel(title)
    check_dir(directory)
    plt.savefig(f'{directory}/Subplot Date Vs {title}')    
    plt.close()

def graph(counts, dates, title):
    splitdate = 1937
    beforecounts, aftercounts = split(counts, dates, splitdate)
    mean, median, std  = get_stats(counts)
    bmean,  bmedian, bstd = get_stats(beforecounts)
    amean,  amedian, astd = get_stats(aftercounts)
    distribution, gaussian_values, sd1, sd2 = calculate_gaussian(counts, mean, std)
    if title == "Syllables per Word":
        print (f"Distribution : \n{distribution} \n Gaussian values: {gaussian_values}")

    bdistribution, bgaussian_values, bsd1, bsd2 = calculate_gaussian(beforecounts, bmean, bstd)
    adistribution, agaussian_values, asd1, asd2 = calculate_gaussian(aftercounts, amean, astd)

    plot(bmean, bmedian, bstd, amean, amedian, astd, counts, dates, title, splitdate)
    plot_gauss(bdistribution, bgaussian_values, adistribution, agaussian_values, title, bstd, astd, bsd1, bsd2, asd1, asd2, bmean, amean)
    
    
def main():
    plt.style.use('bmh')
    check_dir("graphs")
    lines = open_addresses('addresses.txt')
    speechs, dates, presidents = load_addresses(lines)
    sentences, wordcounts, wordlengths,  wordspersentence, lettersperwords, largewords, largewordspercentage, syllables, syllablesperword, grade_level = get_counts(speechs)
    graph(sentences, dates, 'Sentences')
    graph(wordcounts, dates, 'Words')
    graph(lettersperwords, dates,  'Word Lengths')
    graph(wordlengths , dates, 'Letters')
    graph(wordspersentence,  dates, 'Words per Sentence')
    graph(largewords,  dates, 'Large Words')
    graph(largewordspercentage, dates, 'Large Words Percentage')
    graph(syllables,  dates, 'Syllables')
    graph(syllablesperword, dates, 'Syllables per Word')
    graph(grade_level, dates, 'Grade Level')
    sub_plot([syllablesperword, grade_level], dates, "Syllables Per Word, Grade Level")
    sub_plot([wordspersentence, grade_level, syllablesperword], dates, "Wordspersentence, Grade_level, Syllablesperword")
    
main()