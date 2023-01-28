# 基于隐马尔可夫模型的拼音输入法demo

参考了[简易拼音输入法（拼音转汉字）](https://github.com/OrangeX4/simple-pinyin) 中的部分数据处理的逻辑和训练数据，感谢作者的分享。


## 数据是哪里来的

   - 词库: [北京语言大学语言智能研究院](http://bcc.blcu.edu.cn/)提供的[BCC汉语词频表](http://bcc.blcu.edu.cn/downloads/resources/BCC_LEX_Zh.zip)
   - 分词: [jieba](https://github.com/fxsjy/jieba)
   - 拼音标注: [汉字拼音转换工具（Python 版](https://github.com/mozillazg/python-pinyin)
   - 完整拼音列表: https://github.com/OrangeX4/simple-pinyin/blob/main/pinyin/data/intact_pinyin.txt

## 模型是怎么设计的

   - 隐马尔可夫模型是基于词句前后关系和词频来做推断的，要尽量保留语料之间的上下文信息，但是有不能把所有的挨在一起的字连起来，所以采用了分词处理。
     比如：
        "中国商业联合会"这个词, 处理后是"北京|bei'jing 昌平|chang'ping 火车站|huo'che'zhan "
     只会建立"北京"->"昌平"->"火车站"这三个词关系，不会在"平"->"火"、"京"->"昌" 建立关系，避免干扰。
     因此马尔可夫模型的状态用的是"词"，考虑词与词之间的关系。

   - 模型是怎么训练的

     采用监督学习的方式，用词频估计概率，具体可以参考李航的<<统计学习>> 隐马尔可夫模型-学习算法-监督学习方法章节。
     或者直接看下simple-pinyin.py中"load_words_freq_pinyin"这个方法，不复杂。

  - 拼音的分割

    因为是以词为单位的, 拼音切割后，还要按不同的词长进行组合，枚举了所有的可能。
    比如"huijiakankan"，回家看看这个短语的拼音有20几种可能，可能会有一些奇怪的，比如"hui'ji'a'kan"这个是啥？

    ```
        ["hui'jia'kan'kan"]
        ["hui'jia'kan", 'kan']
        ["hui'jia", "kan'kan"]
        ["hui'jia", 'kan', 'kan']
        ['hui', "jia'kan'kan"]
        ['hui', "jia'kan", 'kan']
        ['hui', 'jia', "kan'kan"]
        ['hui', 'jia', 'kan', 'kan']
        ["hui'ji'a'kan", 'kan']
        ["hui'ji'a", "kan'kan"]
        ["hui'ji'a", 'kan', 'kan']
        ["hui'ji", "a'kan'kan"]
        ["hui'ji", "a'kan", 'kan']
        ["hui'ji", 'a', "kan'kan"]
        ["hui'ji", 'a', 'kan', 'kan']
        ['hui', "ji'a'kan'kan"]
        ['hui', "ji'a'kan", 'kan']
        ['hui', "ji'a", "kan'kan"]
        ['hui', "ji'a", 'kan', 'kan']
        ['hui', 'ji', "a'kan'kan"]
        ['hui', 'ji', "a'kan", 'kan']
        ['hui', 'ji', 'a', "kan'kan"]
        ['hui', 'ji', 'a', 'kan', 'kan']
    ```

  - 拼音序列转汉字流程

    - 对于语料包含的语句可以一次匹配成功， 比如："北京-昌平-火车站"。
    - 于不没有覆盖的语句hmm在跑的是时候会遇到失败，返回已经匹配的字句，和下次待匹配的pinyin位置。
      比如："我-看-还-行-呀"，因为"我"和"看"之间的联系没有建立，会失败。
      输入："wo-kan-hai-xing-ya" 会返回"我"，位置1，提示下次从1匹配。
      迭代处理后把整体概率相乘作为了"我-看-还-行-呀"出现的概率，这个概率的方法可能还需要改进一下，因为没有区分，是不是模型直接"连"起来的。

    总体来说就是枚举了所有的可能，然后去跑hmm然后按概率排序，在hmm.ipynb的末尾有一些例子，有兴趣可以看下。

## 待改进的地方

   - 现在的分词，有些得方处理的不好
     比如："北京大学法学院"是作为一个整体进模型的，应该拆成"北京大学-法学院"，甚至"北京-大学-法学院"。
     采用jieba中的全匹配方式，可以缓解这个问题，不过就是可能出现错误的连接，需要平衡，就没搞了。

   - 枚举所有的pinyin序列有点暴力。。。。
     明显可以做一些剪枝，对于模型不含的拼音序列，可以直接过滤掉。

   - 用一些长句子分词后训练可能会更好
     可以搞一些小说试一下？