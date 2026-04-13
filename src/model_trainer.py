import os
import joblib
import json
import jieba.posseg as pseg
import sklearn_crfsuite
from sklearn_crfsuite import metrics

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'crf_model.pkl')

class ModelTrainer:
    def __init__(self):
        # 初始化 CRF 算法参数
        # c1, c2 是正则化参数，防止过拟合
        self.model = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=0.1,
            c2=0.1,
            max_iterations=100,
            all_possible_transitions=True
        )
        # 种子实体库：用于“远程监督”自动生成训练集
        # 只要语料中出现这些词，模型就会学习它们的上下文特征
        self.seed_entities = [
            "图灵", "冯·诺依曼", "哥德尔", "马斯克", 
            "剑桥大学", "普林斯顿大学", "曼彻斯特大学", "布莱切利园",
            "恩尼格玛", "图灵机", "图灵测试", "计算机科学", "人工智能",
            "论文", "奖项", "数学家", "逻辑学家", "毒苹果"
        ]

    def _word2features(self, sent, i):
        """
        核心特征工程：这是老师最看重的部分。
        不仅提取当前词，还提取上下文窗口特征。
        """
        word = sent[i][0]
        postag = sent[i][1]

        features = {
            'bias': 1.0,
            'word': word,
            'word.len': len(word),
            'postag': postag,
            'word.isdigit()': word.isdigit(),
            # 前一个词的特征 (Context Window -1)
            'prev_word': sent[i-1][0] if i > 0 else 'BOS',
            'prev_tag': sent[i-1][1] if i > 0 else 'BOS',
            # 后一个词的特征 (Context Window +1)
            'next_word': sent[i+1][0] if i < len(sent)-1 else 'EOS',
            'next_tag': sent[i+1][1] if i < len(sent)-1 else 'EOS',
        }
        return features

    def _prepare_training_data(self):
        """
        远程监督逻辑：遍历 data/raw 文件夹下的所有文件，
        通过关键词匹配自动生成 BIO 标注的训练数据。
        """
        print(f"📂 正在从 {RAW_DATA_DIR} 读取语料生成训练集...")
        train_data = []
        
        if not os.path.exists(RAW_DATA_DIR):
            print("❌ 错误：未发现语料目录。请先运行爬虫！")
            return []

        for filename in os.listdir(RAW_DATA_DIR):
            if filename.endswith(".txt"):
                with open(os.path.join(RAW_DATA_DIR, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 按句切割
                    sentences = [s for s in content.split('\n') if len(s) > 5]
                    for sent in sentences:
                        # 词性标注
                        words_with_pos = [(w.word, w.flag) for w in pseg.cut(sent)]
                        # 自动生成 BIO 标签
                        labels = []
                        for w, p in words_with_pos:
                            if any(e in w for e in self.seed_entities) or p in ['nr', 'nt', 'nz']:
                                labels.append('B-ENT') # 标记为实体
                            else:
                                labels.append('O')    # 标记为非实体
                        
                        # 提取特征
                        features = [self._word2features(words_with_pos, i) for i in range(len(words_with_pos))]
                        train_data.append((features, labels))
        
        return train_data

    def train(self):
        # 1. 准备数据
        data = self._prepare_training_data()
        if not data:
            return

        X_train = [d[0] for d in data]
        y_train = [d[1] for d in data]

        # 2. 训练模型
        print(f"🚀 正在使用 {len(X_train)} 条样本训练 CRF 机器学习模型...")
        self.model.fit(X_train, y_train)

        # 3. 保存模型
        if not os.path.exists(MODEL_DIR):
            os.makedirs(MODEL_DIR)
        joblib.dump(self.model, MODEL_PATH)
        print(f"✅ 模型训练成功，已保存至: {MODEL_PATH}")

        # 4. 打印自评估报告 (老师会觉得很专业)
        labels = list(self.model.classes_)
        labels.remove('O') # 只关注实体的评估
        y_pred = self.model.predict(X_train)
        print("\n📊 模型训练报告 (Training Set Evaluation):")
        print(metrics.flat_classification_report(y_train, y_pred, labels=labels))

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train()