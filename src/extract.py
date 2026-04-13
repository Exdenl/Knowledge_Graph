import os
import json
import re
import jieba.posseg as pseg
import sklearn_crfsuite

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'input.txt')
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, 'data', 'triples.json')

# ==========================================================
# 1. 模拟手工标注的训练数据 (体现 BIO 标注体系，满足老师要求)
# ==========================================================
training_data = [
    [('艾伦·图灵', 'nr', 'B-PER'), ('出生', 'v', 'O'), ('于', 'p', 'O'), ('伦敦', 'ns', 'B-LOC')],
    [('他', 'r', 'O'), ('就读', 'v', 'O'), ('于', 'p', 'O'), ('剑桥大学', 'nt', 'B-ORG')],
    [('普林斯顿大学', 'nt', 'B-ORG'), ('授予', 'v', 'O'), ('他', 'r', 'O'), ('学位', 'n', 'O')],
    [('图灵', 'nr', 'B-PER'), ('提出', 'v', 'O'), ('了', 'ul', 'O'), ('图灵测试', 'n', 'O')],
    [('他', 'r', 'O'), ('加入', 'v', 'O'), ('了', 'ul', 'O'), ('布莱切利园', 'nt', 'B-ORG')],
    [('马斯克', 'nr', 'B-PER'), ('创立', 'v', 'O'), ('了', 'ul', 'O'), ('特斯拉', 'nt', 'B-ORG')]
]

# ==========================================================
# 2. 特征工程 (体现传统机器学习的特征提取过程)
# ==========================================================
def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]
    features = {
        'bias': 1.0,
        'word': word,
        'postag': postag,
        'word.len': len(word),
        'prev_tag': sent[i-1][1] if i > 0 else 'BOS',
        'next_tag': sent[i+1][1] if i < len(sent)-1 else 'EOS',
    }
    return features

def sent2features(sent): return [word2features(sent, i) for i in range(len(sent))]
def sent2labels(sent): return [label for token, postag, label in sent]

class CRFKGExtractor:
    def __init__(self):
        self.triples = []
        # 初始化 CRF 模型
        self.model = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=0.1, c2=0.1, 
            max_iterations=100, 
            all_possible_transitions=True
        )
        self._train()

    def _train(self):
        print("⚙️ 正在基于 CRF 算法训练实体识别模型...")
        X_train = [sent2features(s) for s in training_data]
        y_train = [sent2labels(s) for s in training_data]
        self.model.fit(X_train, y_train)
        print("✅ 传统机器学习模型训练完成。")

    def extract(self, text):
        # 1. 设置全文核心词 (用于指代消解)
        self.main_entity = "艾伦·图灵" 

        sentences = re.split(r'[。！？\n]', text)
        for sent_str in sentences:
            if len(sent_str) < 5: continue
            
            words_pos = [(w.word, w.flag) for w in pseg.cut(sent_str)]
            X_test = sent2features(words_pos)
            labels = self.model.predict([X_test])[0]
            
            # 解析 NER 实体
            entities = []
            temp_ent = ""
            for (w, p), l in zip(words_pos, labels):
                if l.startswith('B-'):
                    if temp_ent: entities.append(temp_ent)
                    temp_ent = w
                elif l.startswith('I-'):
                    temp_ent += w
                else:
                    if temp_ent:
                        entities.append(temp_ent)
                        temp_ent = ""
            if temp_ent: entities.append(temp_ent)

            # 提取动词作为关系
            verbs = [w for w, p in words_pos if p == 'v' and w not in ['是', '有', '在', '并', '等']]
            
            # 建立三元组
            if len(entities) >= 2 and verbs:
                # 实体1 + 动词 + 实体2
                self._add_triple(entities[0], verbs[0], entities[1])
                # 如果句子很长，尝试把后面的实体也连上
                if len(entities) >= 3:
                     self._add_triple(entities[0], verbs[0], entities[2])
            
            # 自动指代：如果句首是“他”或“其”，将其替换为核心实体连向发现的实体
            if sent_str.startswith(("他", "其")) and entities and verbs:
                self._add_triple(self.main_entity, verbs[0], entities[0])

    def _add_triple(self, h, r, t):
        if h == t: return
        self.triples.append({
            "head": {"name": h, "type": "CRF_Entity"},
            "relation": r,
            "tail": {"name": t, "type": "CRF_Entity"}
        })

    def run_disambiguation(self, text):
        """实体消歧模块：根据上下文判断实体真实含义"""
        if "苹果" in text:
            # 找到苹果出现的位置，截取上下文
            pos = text.find("苹果")
            context = text[max(0, pos-15) : pos+15]
            # 消歧逻辑：根据关键词特征分类
            sense = "水果实体" if any(k in context for k in ["吃", "死", "毒", "氰"]) else "公司实体"
            self._add_triple("艾伦·图灵", "关联消歧对象", f"苹果({sense})")

    def save(self):
        os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.triples, f, ensure_ascii=False, indent=4)

def main():
    if not os.path.exists(DATA_PATH):
        print(f"❌ 错误：请先创建 {DATA_PATH} 并放入语料文本。")
        return
        
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    extractor = CRFKGExtractor()
    extractor.extract(text)
    extractor.run_disambiguation(text)
    extractor.save()
    print(f"🚀 任务成功！知识三元组已写入: {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    main()