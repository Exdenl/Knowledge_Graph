# src/inference_engine.py
import joblib
import jieba.posseg as pseg
import re
import os
from .utils import word2features

class Extractor:
    def __init__(self):
        model_path = "models/crf_model.pkl"
        if not os.path.exists(model_path):
            raise Exception("找不到模型文件，请先运行训练阶段！")
        self.model = joblib.load(model_path)
        # 新增：关系停用词表
        self.relation_stopwords = {
            '是', '有', '在', '即', '称', '论', '说', '诸如', '关于', 
            '包含', '包括', '作为', '被', '从而', '其中', '以及', '之类'
        }

    def extract(self, text):
        triples = []
        sentences = re.split(r'[。！？\n]', text)
        
        print("[抽取引擎] 开始使用 CRF 模型进行实体与关系挖掘...")
        for sent in sentences:
            if len(sent.strip()) < 5: continue
            
            words_pos = [(w.word, w.flag) for w in pseg.cut(sent)]
            features =[word2features(words_pos, i) for i in range(len(words_pos))]
            
            # 使用模型预测实体标签
            labels = self.model.predict([features])[0]
            
            entities =[w for (w, p), l in zip(words_pos, labels) if l == 'B-ENT' and len(w)>1]
            verbs = []
            for w, p in words_pos:
            # 过滤：长度必须大于1，且不在停用词表中
                if p.startswith('v') or p == 'vn':
                    if len(w) > 1 and w not in self.          relation_stopwords:
                        verbs.append(w)
            
            # 构建三元组
            if len(entities) >= 2 and len(verbs) >= 1:
                triples.append({"head": entities[0], "rel": verbs[0], "tail": entities[1]})
            elif len(entities) == 1 and len(verbs) >= 1:
                # 自动指代主角
                triples.append({"head": "艾伦·图灵", "rel": verbs[0], "tail": entities[0]})
                
        return triples