import numpy as np
import functools

from hmm import get_max_probability_states_by_outputs


def load_words_freq_pinyin(file_name):
    init_words_freq = {}
    emit_pinyin_freq = {}
    transmission_freq = {}
    with open(file_name, "r") as words:
        for line in words:
            fields = line.split()
            freq = int(fields[0])
            is_first = True
            last_word = ""
            for word_pinyin in fields[1:]:
                word, pinyin = word_pinyin.split("|")

                word_emit_pinyin_freq = emit_pinyin_freq.get(word, {})
                word_emit_pinyin_freq[pinyin] = word_emit_pinyin_freq.get(pinyin, 0) + freq
                emit_pinyin_freq[word] = word_emit_pinyin_freq

                if is_first:
                    init_words_freq[word] = init_words_freq.get(word, 0) + freq
                    is_first = False
                else:
                    word_transmission_freq = transmission_freq.get(last_word, {})
                    word_transmission_freq[word] = word_transmission_freq.get(word, 0) + freq
                    transmission_freq[last_word] = word_transmission_freq

                last_word = word

    return init_words_freq, transmission_freq, emit_pinyin_freq


def normal_probability(freq, total_freq):
    return freq * 1.0 / total_freq


def build_hmm(init_words_freq, transmission_freq, emit_pinyin_freq):
    init_words_probability = {}
    transmission_probability = {}
    reverse_emit_pinyin_probability = {}

    init_word_total_freq = np.sum(list(init_words_freq.values()))

    for init_word, freq in init_words_freq.items():
        init_words_probability[init_word] = normal_probability(freq, init_word_total_freq)

    reverse_transmit_dict = {}
    for from_word, to_words_freq in transmission_freq.items():
        for to_word in to_words_freq.keys():
            word_reverse_transmit_set = reverse_transmit_dict.get(to_word, set({}))
            word_reverse_transmit_set.add(from_word)
            reverse_transmit_dict[to_word] = word_reverse_transmit_set

    for from_word, to_words_freq in transmission_freq.items():
        to_word_total_freqs = np.sum(list(to_words_freq.values()))
        for to_word, to_word_freq in to_words_freq.items():
            words_transmission_probability = transmission_probability.get(from_word, {})
            words_transmission_probability[to_word] = normal_probability(to_word_freq, to_word_total_freqs)
            transmission_probability[from_word] = words_transmission_probability

    for word, pinyins_freq in emit_pinyin_freq.items():
        total_pinyin_freq = np.sum(list(pinyins_freq.values()))
        for pinyin, freq in pinyins_freq.items():
            pinyin_words_probability = reverse_emit_pinyin_probability.get(pinyin, {})
            pinyin_words_probability[word] = normal_probability(freq, total_pinyin_freq)
            reverse_emit_pinyin_probability[pinyin] = pinyin_words_probability

    return init_words_probability, transmission_probability, reverse_emit_pinyin_probability


# 加载完整拼音对应的拼音表 data/intact_pinyin.txt, 共 416 个
PINYIN_SET = set()
with open('data/intact_pinyin.txt', 'r', encoding='utf-8') as f:
    PINYIN_SET = set(s for s in f.read().split('\n'))

MAX_PINYIN_LEN = np.max(list(len(s) for s in PINYIN_SET))


def cut_pinyin(pinyin_str):
    pinyin_list = []
    for pinyin_len in range(MAX_PINYIN_LEN, 0, -1):
        if len(pinyin_str) >= pinyin_len and pinyin_str[0:pinyin_len] in PINYIN_SET:
            if len(pinyin_str) != pinyin_len:
                rest_pinyin_list = cut_pinyin(pinyin_str[pinyin_len:])
                if len(rest_pinyin_list) > 0:
                    for rest_pinyin_list in rest_pinyin_list:
                        pinyin_list.append([pinyin_str[0:pinyin_len]] + rest_pinyin_list)
            else:
                pinyin_list.append([pinyin_str[0:pinyin_len]])

    return pinyin_list


def get_hanzi_by_pinyin(pinyin_list, init_words_probability, transmission_probability, reverse_emit_pinyin_probability):
    hanzi_list = []
    hangzi_list_probability = 1

    next_process_index = 0

    while next_process_index != len(pinyin_list):
        max_probability_states, word_probability, rest_next_process_index = \
            get_max_probability_states_by_outputs(pinyin_list[next_process_index:], init_words_probability,
                                                  transmission_probability,
                                                  reverse_emit_pinyin_probability)
        if len(max_probability_states) == 0:
            break

        hanzi_list += max_probability_states
        hangzi_list_probability *= word_probability
        next_process_index += rest_next_process_index

    if next_process_index != len(pinyin_list):
        hanzi_list += pinyin_list[next_process_index:]

    return "-".join(hanzi_list), hangzi_list_probability, next_process_index == len(pinyin_list)


def get_all_pinyin_list(pinyin_list):
    all_pinyin_list = []
    max_word_len = 4
    for word_len in range(max_word_len, 0, -1):
        if len(pinyin_list) > word_len:
            rest_pinyin_list = get_all_pinyin_list(pinyin_list[word_len:])
            if len(rest_pinyin_list) > 0:
                for rest_pinyin_list in rest_pinyin_list:
                    all_pinyin_list.append(["'".join(pinyin_list[0:word_len])] + rest_pinyin_list)
        elif len(pinyin_list) == word_len:
            all_pinyin_list.append(["'".join(pinyin_list[0:word_len])])

    return all_pinyin_list


def get_all_hanzi_by_pinyin(pinyin_str, init_words_probability, transmission_probability,
                            reverse_emit_pinyin_probability):
    all_hanzi_list = []

    for raw_pinyin_list in cut_pinyin(pinyin_str):
        for combined_pinyin_list in get_all_pinyin_list(raw_pinyin_list):
            all_hanzi_list.append(
                get_hanzi_by_pinyin(combined_pinyin_list, init_words_probability, transmission_probability,
                                    reverse_emit_pinyin_probability))

    def my_comparator(hanzi_list_a, hanzi_list_b):
        if hanzi_list_a[2] == hanzi_list_b[2]:
            return hanzi_list_a[1] - hanzi_list_b[1]
        else:
            return hanzi_list_a[2] - hanzi_list_b[2]

    all_hanzi_list.sort(key=functools.cmp_to_key(my_comparator), reverse=True)

    return all_hanzi_list


for pylst in cut_pinyin('huijiakankan'):
    for lst in get_all_pinyin_list(pylst):
        print(lst)

# for lst in cut_pinyin('xiangmuguanli'):
#     print(lst)
# #
# if __name__ == '__main__':
#     init_words_freq, transmission_freq, emit_pinyin_freq = load_words_freq_pinyin(
#         "./data/global_words_freq_pinyin.txt")
#
#     init_words_probability, transmission_probability, reverse_emit_pinyin_probability = build_hmm(init_words_freq,
#                                                                                                   transmission_freq,
#                                                                                                   emit_pinyin_freq)
