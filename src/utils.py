# src/utils.py
def word2features(sent, i):
    """提取CRF模型需要的自然语言特征"""
    word, postag = sent[i][0], sent[i][1]
    features = {
        'bias': 1.0,
        'word': word,
        'postag': postag,
        'word.length': len(word),
        'is_numeric': word.isdigit(),
        'prev_tag': sent[i-1][1] if i > 0 else 'BOS',
        'next_tag': sent[i+1][1] if i < len(sent)-1 else 'EOS',
    }
    return features