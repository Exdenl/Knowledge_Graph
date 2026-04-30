# src/utils.py
def word2features(sent, i):
    """
    提取基于上下文滑动窗口的词法与句法特征 (Feature Engineering)
    """
    word, postag = sent[i][0], sent[i][1]
    
    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word.length': len(word),
        'postag': postag,
        
        # 【新增】词汇形态学特征
        'word.is_numeric': word.isdigit(),
        'word.is_alpha': word.isalpha(),           # 是否为纯字母(如英文人名/公式)
        'word.prefix_1': word[0],                  # 首字特征
        'word.suffix_1': word[-1],                 # 尾字特征 (如:"学"->学科,"局"->机构)
    }
    
    # 向左滑动窗口 (Context Window -1)
    if i > 0:
        word1, postag1 = sent[i-1][0], sent[i-1][1]
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:postag': postag1,
        })
    else:
        features['BOS'] = True  # 句子开头标识 (Beginning of Sentence)

    # 向右滑动窗口 (Context Window +1)
    if i < len(sent) - 1:
        word1, postag1 = sent[i+1][0], sent[i+1][1]
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:postag': postag1,
        })
    else:
        features['EOS'] = True  # 句子结尾标识 (End of Sentence)

    return features