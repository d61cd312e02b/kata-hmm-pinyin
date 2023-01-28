from pypinyin import pinyin, NORMAL
import jieba
from pypinyin_dict.phrase_pinyin_data import cc_cedict

cc_cedict.load()


def all_chinese(word):
    '''
     判断一个字符串是否全由汉字组成, 用于过滤文本
     '''
    return all('\u4e00' <= ch <= '\u9fff' for ch in word)


def preprocess_words_data(file_name):
    with open(file_name, "r") as words:
        for line in words:
            fields = line.split()
            if len(fields) == 2:
                (word, freq) = fields
                if all_chinese(word):
                    words_pinyin = get_words_pinyin(word)
                    words_jieba = get_jieba_word(word)
                    start_index = 0
                    print(freq, end=" ")
                    for word in words_jieba:
                        print(word, do_get_pinyin_str(words_pinyin[start_index:start_index + len(word)]), end=" ",
                              sep="|")
                        start_index = start_index + len(word)
                    print()


def do_get_pinyin_str(py_list):
    words_pin_list = []
    for py_word_list in py_list:
        words_pin_list.append(py_word_list[0])

    return "'".join(words_pin_list)


def get_words_pinyin(word):
    return pinyin(word, style=NORMAL)


def get_jieba_word(word):
    return list(jieba.cut(word))


preprocess_words_data("data/global_wordfreq.release.txt")
