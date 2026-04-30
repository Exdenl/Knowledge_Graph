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
        self.main_entity = "艾伦·图灵"
        
        # 实体黑名单：坚决不让这些词出现在图谱节点上
        self.entity_stopwords = {
            '诸如', '关于', '对于', '由于', '和子', '马赛克', '普通', '智慧', 
            '方面', '很多', '非常', '认为', '使得', '成为', '开始', '一个', 
            '一种', '没有', '具有', '以及'
        }
        
        # 关系黑名单：过滤无意义动词、认知类主观词
        self.rel_stopwords = {
            '是', '有', '在', '即', '称', '论', '说', '诸如', '关于', '使得',
            '包含', '包括', '作为', '被', '从而', '其中', '以及', '之类',
            '认为', '觉得', '流行', '出色', '可以', '可能', '导致', '进行', '开始'
        }

    def extract(self, text):
        triples =[]
        # 将分号(;)也加入切分，防止过长的从句导致错误匹配
        sentences = re.split(r'[。！？;\n]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 5: continue
            
            words_pos =[(w.word, w.flag) for w in pseg.cut(sent)]
            features =[word2features(words_pos, i) for i in range(len(words_pos))]
            labels = self.model.predict([features])[0]
            
            entities =[]
            # 记录所有实体，并限制实体长度 (太长的通常是切词失败的脏数据)
            for idx, ((w, p), l) in enumerate(zip(words_pos, labels)):
                if l.startswith('B-') and 1 < len(w) <= 15 and w not in self.entity_stopwords:
                    entities.append({"name": w, "type": l.split('-')[1], "pos": idx})
            
            # --- 核心逻辑 1：标准双实体关系抽取 ---
            if len(entities) >= 2:
                for i in range(len(entities) - 1):
                    e1, e2 = entities[i], entities[i+1]
                    
                    # 【高级特性1】 距离惩罚策略 (Distance Penalty)
                    # 如果两个实体中间隔了超过 12 个词，极有可能已经跨越了语义从句，强制截断，避免噪音
                    if e2['pos'] - e1['pos'] > 12:
                        continue
                    
                    complex_relations = []
                    for idx in range(e1['pos'] + 1, e2['pos']):
                        w, p = words_pos[idx]
                        
                        # 定位核心动词
                        if (p.startswith('v') or p == 'vn') and len(w) >= 1 and w not in self.rel_stopwords:
                            rel_phrase = w
                            
                            # 【高级特性2】 动态多级滑动窗口 (向左提取修饰成分)
                            left_ext = ""
                            # 向左看最多 2 个词 (例如捕获 "一直 被" 或 "曾 广泛")
                            for step in range(1, 3):
                                if idx - step > e1['pos']:
                                    left_w, left_p = words_pos[idx-step]
                                    if left_p in['p', 'd', 'c'] and left_w in['被', '曾', '已', '在', '向', '对', '将', '广泛', '一直']:
                                        left_ext = left_w + left_ext # 注意拼装顺序
                                    else:
                                        break # 遇到不符合的词性立即中断扩展
                            rel_phrase = left_ext + rel_phrase
                                    
                            # 【高级特性2】 动态多级滑动窗口 (向右提取补语成分)
                            right_ext = ""
                            # 向右看最多 2 个词 (例如捕获 "为 了" 或 "发展 成")
                            for step in range(1, 3):
                                if idx + step < e2['pos']:
                                    right_w, right_p = words_pos[idx+step]
                                    if right_p in['p', 'u', 'v', 'vd'] and right_w in['为', '于', '了', '过', '到', '出', '成']:
                                        right_ext = right_ext + right_w
                                    else:
                                        break
                            rel_phrase = rel_phrase + right_ext
                            
                            complex_relations.append(rel_phrase)
                    
                    # 抽取成功
                    if complex_relations:
                        triples.append({
                            "head": {"name": e1['name'], "type": e1['type']}, 
                            "rel": complex_relations[-1],  # 启发式规则：取最靠近宾语的复杂动词短语
                            "tail": {"name": e2['name'], "type": e2['type']}
                        })
                        
            # --- 核心逻辑 2：弱指代消解与省略主语的情况 (Zero Anaphora) ---
            # 有些句子只有一个实体，比如："就被任命为剑桥大学研究员"
            elif len(entities) == 1:
                e1 = entities[0]
                
                # 寻找该实体前面的最近动词
                for idx in range(e1['pos'] - 1, -1, -1):
                    w, p = words_pos[idx]
                    if (p.startswith('v') or p == 'vn') and len(w) > 1 and w not in self.rel_stopwords:
                        rel_phrase = w
                        
                        # 向右简单扩展一次（如：任命 -> 任命为）
                        if idx + 1 < e1['pos']:
                            right_w, right_p = words_pos[idx+1]
                            if right_p in ['p', 'u'] and right_w in ['为', '于', '了', '到']:
                                rel_phrase += right_w
                                
                        # 如果句子以代词开头，或者这个动词非常靠前，我们大胆将其主语补全为“艾伦·图灵”
                        if sent.startswith(("他", "其", "图灵")) or idx < 4:
                            triples.append({
                                "head": {"name": self.main_entity, "type": "PER"}, 
                                "rel": rel_phrase, 
                                "tail": {"name": e1['name'], "type": e1['type']}
                            })
                        break # 只找最靠近实体的动词
                        
        return triples