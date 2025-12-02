# 导入必要的库
import numpy as np
import pandas as pd
import os
import tarfile
import urllib.request
import re
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("环境设置完成!")

def download_imdb_data():
    """下载IMDb数据集"""
    url = "http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz"
    filename = "aclImdb_v1.tar.gz"
    
    if not os.path.exists("aclImdb"):
        print("正在下载IMDb数据集...")
        urllib.request.urlretrieve(url, filename)
        print("下载完成，正在解压...")
        
        with tarfile.open(filename, 'r:gz') as tar:
            tar.extractall()
        
        print("解压完成!")
        
        # 删除压缩包
        os.remove(filename)
    else:
        print("数据集已存在，跳过下载步骤。")

def load_imdb_data(data_dir="aclImdb", sample_size=None):
    """加载IMDb数据集，可选择部分样本"""
    train_dir = os.path.join(data_dir, 'train')
    test_dir = os.path.join(data_dir, 'test')
    
    def load_from_directory(directory, label_type, max_samples=None):
        texts = []
        labels = []
        dir_name = os.path.join(directory, label_type)
        label = 1 if label_type == 'pos' else 0
        
        files = os.listdir(dir_name)
        
        # 如果指定了最大样本数，则随机选择
        if max_samples and max_samples < len(files):
            import random
            files = random.sample(files, max_samples)
        
        for fname in files:
            if fname.endswith('.txt'):
                with open(os.path.join(dir_name, fname), 'r', encoding='utf-8') as f:
                    texts.append(f.read())
                labels.append(label)
        
        return texts, labels
    
    print("加载训练数据...")
    pos_train_texts, pos_train_labels = load_from_directory(train_dir, 'pos', sample_size)
    neg_train_texts, neg_train_labels = load_from_directory(train_dir, 'neg', sample_size)
    
    train_texts = pos_train_texts + neg_train_texts
    train_labels = pos_train_labels + neg_train_labels
    
    print("加载测试数据...")
    pos_test_texts, pos_test_labels = load_from_directory(test_dir, 'pos', sample_size//2 if sample_size else None)
    neg_test_texts, neg_test_labels = load_from_directory(test_dir, 'neg', sample_size//2 if sample_size else None)
    
    test_texts = pos_test_texts + neg_test_texts
    test_labels = pos_test_labels + neg_test_labels
    
    # 打乱数据
    def shuffle_data(texts, labels):
        indices = np.random.permutation(len(texts))
        return [texts[i] for i in indices], [labels[i] for i in indices]
    
    train_texts, train_labels = shuffle_data(train_texts, train_labels)
    test_texts, test_labels = shuffle_data(test_texts, test_labels)
    
    print(f"训练数据: {len(train_texts)} 条评论")
    print(f"测试数据: {len(test_texts)} 条评论")
    print(f"正面评论比例: {sum(train_labels)/len(train_labels):.2%}")
    
    return train_texts, train_labels, test_texts, test_labels

# 下载并加载数据
download_imdb_data()

# 为了快速训练，这里使用较小的样本集（可调整）
SAMPLE_SIZE = 25000  # 使用全部数据需要更多时间
train_texts, train_labels, test_texts, test_labels = load_imdb_data(sample_size=SAMPLE_SIZE)

# 查看数据示例
print("\n数据示例:")
print(f"正面评论示例: {train_texts[0][:200]}...")
print(f"标签: {'正面' if train_labels[0] == 1 else '负面'}")
print(f"\n负面评论示例: {train_texts[-1][:200]}...")
print(f"标签: {'正面' if train_labels[-1] == 1 else '负面'}")

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# 下载NLTK资源
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextPreprocessor:
    """文本预处理类，专为LSTM优化"""
    def __init__(self, max_vocab_size=20000, max_sequence_length=200):
        self.max_vocab_size = max_vocab_size
        self.max_sequence_length = max_sequence_length
        self.vocab = {}
        self.word_index = {}
        self.index_word = {}
        
    def clean_text(self, text):
        """清理文本"""
        # 转换为小写
        text = text.lower()
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', ' ', text)
        # 替换URLs
        text = re.sub(r'https?://\S+|www\.\S+', ' <url> ', text)
        # 替换数字
        text = re.sub(r'\d+', ' <num> ', text)
        # 处理缩写
        text = re.sub(r"won't", "will not", text)
        text = re.sub(r"can't", "can not", text)
        text = re.sub(r"n't", " not", text)
        text = re.sub(r"'ll", " will", text)
        text = re.sub(r"'ve", " have", text)
        # 去除标点符号（保留部分情感符号）
        text = re.sub(r'[^\w\s!?]', ' ', text)
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def tokenize(self, text):
        """分词"""
        return word_tokenize(text)
    
    def build_vocabulary(self, texts):
        """构建词汇表"""
        print("构建词汇表...")
        word_counts = Counter()
        
        for text in texts:
            cleaned_text = self.clean_text(text)
            tokens = self.tokenize(cleaned_text)
            word_counts.update(tokens)
        
        # 选择最常见的词
        most_common_words = word_counts.most_common(self.max_vocab_size - 2)  # -2 为 <pad> 和 <unk>
        
        # 创建词汇表
        self.word_index = {'<pad>': 0, '<unk>': 1}
        self.index_word = {0: '<pad>', 1: '<unk>'}
        
        for idx, (word, count) in enumerate(most_common_words):
            self.word_index[word] = idx + 2
            self.index_word[idx + 2] = word
        
        self.vocab_size = len(self.word_index)
        print(f"词汇表大小: {self.vocab_size}")
        
        return self.word_index
    
    def texts_to_sequences(self, texts):
        """将文本转换为序列"""
        sequences = []
        
        for text in texts:
            cleaned_text = self.clean_text(text)
            tokens = self.tokenize(cleaned_text)
            sequence = []
            
            for token in tokens:
                if token in self.word_index:
                    sequence.append(self.word_index[token])
                else:
                    sequence.append(self.word_index['<unk>'])
            
            # 截断或填充序列
            if len(sequence) > self.max_sequence_length:
                sequence = sequence[:self.max_sequence_length]
            else:
                sequence = sequence + [self.word_index['<pad>']] * (self.max_sequence_length - len(sequence))
            
            sequences.append(sequence)
        
        return np.array(sequences)

# 创建预处理器并构建词汇表
preprocessor = TextPreprocessor(max_vocab_size=20000, max_sequence_length=200)
preprocessor.build_vocabulary(train_texts)

# 将文本转换为序列
print("\n将文本转换为序列...")
X_train = preprocessor.texts_to_sequences(train_texts)
X_test = preprocessor.texts_to_sequences(test_texts)
y_train = np.array(train_labels)
y_test = np.array(test_labels)

print(f"训练数据形状: {X_train.shape}")
print(f"测试数据形状: {X_test.shape}")
print(f"标签形状: {y_train.shape}")

# 查看一个示例序列
print(f"\n示例序列（前20个token）: {X_train[0][:20]}")
print("对应的单词:", [preprocessor.index_word.get(idx, '<unk>') for idx in X_train[0][:20]])

import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (
    Embedding, Bidirectional, LSTM, Dense, 
    Dropout, SpatialDropout1D, GlobalMaxPooling1D,
    Conv1D, MaxPooling1D, Input, Concatenate
)
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import plot_model

print(f"TensorFlow版本: {tf.__version__}")

def build_bidirectional_lstm_model(vocab_size, max_sequence_length, embedding_dim=128):
    """
    构建双向LSTM模型
    
    参数:
    vocab_size: 词汇表大小
    max_sequence_length: 最大序列长度
    embedding_dim: 词向量维度
    """
    model = Sequential([
        # 嵌入层
        Embedding(
            input_dim=vocab_size, 
            output_dim=embedding_dim, 
            input_length=max_sequence_length,
            mask_zero=True,  # 忽略填充值
            name="embedding"
        ),
        
        # 空间Dropout，防止过拟合
        SpatialDropout1D(0.2, name="spatial_dropout"),
        
        # 第一个双向LSTM层
        Bidirectional(
            LSTM(64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2),
            name="bilstm_1"
        ),
        
        # 第二个双向LSTM层
        Bidirectional(
            LSTM(32, dropout=0.2, recurrent_dropout=0.2),
            name="bilstm_2"
        ),
        
        # 全连接层
        Dense(64, activation='relu', name="dense_1"),
        Dropout(0.5, name="dropout_1"),
        
        # 输出层
        Dense(1, activation='sigmoid', name="output")
    ])
    
    return model

def build_hybrid_model(vocab_size, max_sequence_length, embedding_dim=128):
    """
    构建混合模型：CNN + 双向LSTM
    这种架构通常能捕捉局部特征和序列依赖
    """
    inputs = Input(shape=(max_sequence_length,), name="input")
    
    # 嵌入层
    embedding = Embedding(
        vocab_size, 
        embedding_dim, 
        input_length=max_sequence_length,
        mask_zero=True,
        name="embedding"
    )(inputs)
    
    # 空间Dropout
    embedding = SpatialDropout1D(0.2, name="spatial_dropout")(embedding)
    
    # CNN部分用于捕捉局部特征
    conv1 = Conv1D(filters=64, kernel_size=3, padding='same', activation='relu', name="conv1d_1")(embedding)
    conv1 = MaxPooling1D(pool_size=2, name="maxpool_1")(conv1)
    
    conv2 = Conv1D(filters=32, kernel_size=3, padding='same', activation='relu', name="conv1d_2")(conv1)
    conv2 = MaxPooling1D(pool_size=2, name="maxpool_2")(conv2)
    
    # 双向LSTM部分用于捕捉序列依赖
    bilstm = Bidirectional(
        LSTM(64, dropout=0.2, recurrent_dropout=0.2, return_sequences=True),
        name="bilstm_1"
    )(conv2)
    
    # 全局最大池化
    pooled = GlobalMaxPooling1D(name="global_maxpool")(bilstm)
    
    # 全连接层
    dense1 = Dense(64, activation='relu', name="dense_1")(pooled)
    dense1 = Dropout(0.5, name="dropout_1")(dense1)
    
    dense2 = Dense(32, activation='relu', name="dense_2")(dense1)
    dense2 = Dropout(0.3, name="dropout_2")(dense2)
    
    # 输出层
    outputs = Dense(1, activation='sigmoid', name="output")(dense2)
    
    model = Model(inputs=inputs, outputs=outputs, name="hybrid_cnn_bilstm")
    
    return model

# 构建模型
print("构建双向LSTM模型...")
vocab_size = preprocessor.vocab_size
max_sequence_length = preprocessor.max_sequence_length

# 选择模型类型：'bilstm' 或 'hybrid'
MODEL_TYPE = 'hybrid'  # 可以改为 'bilstm'

if MODEL_TYPE == 'bilstm':
    model = build_bidirectional_lstm_model(vocab_size, max_sequence_length, embedding_dim=128)
    model_name = "bidirectional_lstm"
else:
    model = build_hybrid_model(vocab_size, max_sequence_length, embedding_dim=128)
    model_name = "hybrid_cnn_bilstm"

# 编译模型
optimizer = Adam(learning_rate=0.001)
model.compile(
    optimizer=optimizer,
    loss='binary_crossentropy',
    metrics=['accuracy', tf.keras.metrics.Precision(name='precision'), 
             tf.keras.metrics.Recall(name='recall')]
)

# 显示模型架构
model.summary()

# 可视化模型架构（需要安装graphviz）
try:
    plot_model(model, to_file=f'{model_name}_architecture.png', show_shapes=True, show_layer_names=True)
    print(f"模型架构已保存为 {model_name}_architecture.png")
except:
    print("无法生成模型架构图，请确保已安装graphviz")

# 设置回调函数
callbacks = [
    # 早停法：如果验证损失不再改善，则停止训练
    EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    ),
    
    # 模型检查点：保存最佳模型
    ModelCheckpoint(
        filepath=f'best_{model_name}_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    
    # 学习率调整：当指标停止改善时降低学习率
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-6,
        verbose=1
    )
]

# 训练模型
print("开始训练模型...")
history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=20,
    batch_size=64,
    callbacks=callbacks,
    verbose=1
)

print("训练完成!")

# 保存最终模型
model.save(f'{model_name}_final.h5')
print(f"模型已保存为 {model_name}_final.h5")

# 加载最佳模型
from tensorflow.keras.models import load_model
best_model = load_model(f'best_{model_name}_model.h5')

# 评估模型
print("评估模型性能...")
test_loss, test_accuracy, test_precision, test_recall = best_model.evaluate(X_test, y_test, verbose=0)

print(f"\n测试集性能:")
print(f"损失: {test_loss:.4f}")
print(f"准确率: {test_accuracy:.4f}")
print(f"精确率: {test_precision:.4f}")
print(f"召回率: {test_recall:.4f}")

# 计算F1分数
test_f1 = 2 * (test_precision * test_recall) / (test_precision + test_recall)
print(f"F1分数: {test_f1:.4f}")

# 预测
y_pred_proba = best_model.predict(X_test, verbose=0)
y_pred = (y_pred_proba > 0.5).astype(int).flatten()

# 分类报告
from sklearn.metrics import classification_report, confusion_matrix
print("\n分类报告:")
print(classification_report(y_test, y_pred, target_names=['负面', '正面']))

# 混淆矩阵
cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['负面', '正面'], 
            yticklabels=['负面', '正面'])
ax.set_xlabel('预测标签', fontsize=12)
ax.set_ylabel('真实标签', fontsize=12)
ax.set_title('混淆矩阵', fontsize=14)
plt.show()

# 绘制训练历史
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 准确率
axes[0, 0].plot(history.history['accuracy'], label='训练准确率', linewidth=2)
axes[0, 0].plot(history.history['val_accuracy'], label='验证准确率', linewidth=2)
axes[0, 0].set_xlabel('Epoch', fontsize=12)
axes[0, 0].set_ylabel('准确率', fontsize=12)
axes[0, 0].set_title('训练和验证准确率', fontsize=14)
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 损失
axes[0, 1].plot(history.history['loss'], label='训练损失', linewidth=2)
axes[0, 1].plot(history.history['val_loss'], label='验证损失', linewidth=2)
axes[0, 1].set_xlabel('Epoch', fontsize=12)
axes[0, 1].set_ylabel('损失', fontsize=12)
axes[0, 1].set_title('训练和验证损失', fontsize=14)
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 精确率
axes[1, 0].plot(history.history['precision'], label='训练精确率', linewidth=2)
axes[1, 0].plot(history.history['val_precision'], label='验证精确率', linewidth=2)
axes[1, 0].set_xlabel('Epoch', fontsize=12)
axes[1, 0].set_ylabel('精确率', fontsize=12)
axes[1, 0].set_title('训练和验证精确率', fontsize=14)
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# 召回率
axes[1, 1].plot(history.history['recall'], label='训练召回率', linewidth=2)
axes[1, 1].plot(history.history['val_recall'], label='验证召回率', linewidth=2)
axes[1, 1].set_xlabel('Epoch', fontsize=12)
axes[1, 1].set_ylabel('召回率', fontsize=12)
axes[1, 1].set_title('训练和验证召回率', fontsize=14)
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 绘制ROC曲线
from sklearn.metrics import roc_curve, auc
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC曲线 (AUC = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='随机分类器')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('假正率', fontsize=12)
plt.ylabel('真正率', fontsize=12)
plt.title('接收者操作特征曲线', fontsize=14)
plt.legend(loc="lower right")
plt.grid(True, alpha=0.3)
plt.show()

def load_glove_embeddings(embedding_dim=100):
    """
    加载预训练的GloVe词向量
    
    参数:
    embedding_dim: 词向量维度，可选 50, 100, 200, 300
    """
    glove_path = f'glove.6B.{embedding_dim}d.txt'
    embeddings_index = {}
    
    # 检查文件是否存在
    if not os.path.exists(glove_path):
        print(f"GloVe文件不存在，正在下载...")
        import requests
        url = f'http://nlp.stanford.edu/data/glove.6B.zip'
        r = requests.get(url, allow_redirects=True)
        
        with open('glove.6B.zip', 'wb') as f:
            f.write(r.content)
        
        # 解压文件
        import zipfile
        with zipfile.ZipFile('glove.6B.zip', 'r') as zip_ref:
            zip_ref.extractall()
        
        print("GloVe下载并解压完成!")
    
    # 加载词向量
    print(f"加载GloVe词向量 ({embedding_dim}维)...")
    with open(glove_path, 'r', encoding='utf-8') as f:
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
    
    print(f'加载了 {len(embeddings_index)} 个词向量')
    return embeddings_index

def create_embedding_matrix(word_index, embeddings_index, embedding_dim):
    """
    创建嵌入矩阵
    
    参数:
    word_index: 词汇表索引
    embeddings_index: 预训练词向量字典
    embedding_dim: 词向量维度
    """
    embedding_matrix = np.zeros((len(word_index), embedding_dim))
    
    for word, i in word_index.items():
        if word == '<pad>' or word == '<unk>':
            continue
        
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            # 找到的词向量
            embedding_matrix[i] = embedding_vector
        else:
            # 未找到的词向量，使用随机初始化
            embedding_matrix[i] = np.random.normal(scale=0.6, size=(embedding_dim,))
    
    # 为特殊标记设置特定的向量
    # <pad> 标记设为全零向量
    embedding_matrix[0] = np.zeros(embedding_dim)
    
    # <unk> 标记设为随机向量
    embedding_matrix[1] = np.random.normal(scale=0.6, size=(embedding_dim,))
    
    return embedding_matrix

def build_bilstm_with_glove(vocab_size, max_sequence_length, embedding_matrix, embedding_dim, trainable=False):
    """
    使用预训练GloVe词向量构建双向LSTM模型
    
    参数:
    vocab_size: 词汇表大小
    max_sequence_length: 最大序列长度
    embedding_matrix: 嵌入矩阵
    embedding_dim: 词向量维度
    trainable: 是否微调词向量
    """
    model = Sequential([
        # 使用预训练词向量的嵌入层
        Embedding(
            input_dim=vocab_size, 
            output_dim=embedding_dim, 
            input_length=max_sequence_length,
            weights=[embedding_matrix],
            trainable=trainable,  # 是否在训练中更新词向量
            mask_zero=True,
            name="glove_embedding"
        ),
        
        SpatialDropout1D(0.3, name="spatial_dropout"),
        
        # 双向LSTM层
        Bidirectional(
            LSTM(128, return_sequences=True, dropout=0.3, recurrent_dropout=0.3),
            name="bilstm_1"
        ),
        
        Bidirectional(
            LSTM(64, dropout=0.3, recurrent_dropout=0.3),
            name="bilstm_2"
        ),
        
        Dense(128, activation='relu', name="dense_1"),
        Dropout(0.5, name="dropout_1"),
        
        Dense(64, activation='relu', name="dense_2"),
        Dropout(0.3, name="dropout_2"),
        
        Dense(1, activation='sigmoid', name="output")
    ])
    
    return model

# 使用GloVe词向量
print("\n使用预训练GloVe词向量...")
EMBEDDING_DIM = 100  # 可以使用 50, 100, 200, 300

# 加载GloVe词向量
glove_embeddings = load_glove_embeddings(embedding_dim=EMBEDDING_DIM)

# 创建嵌入矩阵
embedding_matrix = create_embedding_matrix(
    preprocessor.word_index, 
    glove_embeddings, 
    EMBEDDING_DIM
)

print(f"嵌入矩阵形状: {embedding_matrix.shape}")

# 计算覆盖率
found_words = np.sum(np.any(embedding_matrix[2:], axis=1))  # 排除特殊标记
total_words = len(preprocessor.word_index) - 2  # 排除特殊标记
coverage = found_words / total_words
print(f"词汇表覆盖率: {coverage:.2%}")

# 构建使用GloVe的模型
glove_model = build_bilstm_with_glove(
    vocab_size=vocab_size,
    max_sequence_length=max_sequence_length,
    embedding_matrix=embedding_matrix,
    embedding_dim=EMBEDDING_DIM,
    trainable=True  # 微调词向量
)

# 编译模型
glove_model.compile(
    optimizer=Adam(learning_rate=0.0005),
    loss='binary_crossentropy',
    metrics=['accuracy', tf.keras.metrics.Precision(name='precision'), 
             tf.keras.metrics.Recall(name='recall')]
)

glove_model.summary()

# 训练GloVe模型
print("训练使用GloVe词向量的模型...")
glove_history = glove_model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=15,
    batch_size=64,
    callbacks=[
        EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True),
        ModelCheckpoint('best_glove_model.h5', monitor='val_accuracy', save_best_only=True)
    ],
    verbose=1
)

# 评估GloVe模型
print("\n评估GloVe模型...")
glove_test_loss, glove_test_accuracy, glove_test_precision, glove_test_recall = glove_model.evaluate(X_test, y_test, verbose=0)

print(f"GloVe模型测试集性能:")
print(f"准确率: {glove_test_accuracy:.4f}")
print(f"精确率: {glove_test_precision:.4f}")
print(f"召回率: {glove_test_recall:.4f}")

glove_test_f1 = 2 * (glove_test_precision * glove_test_recall) / (glove_test_precision + glove_test_recall)
print(f"F1分数: {glove_test_f1:.4f}")

# 保存GloVe模型
glove_model.save('bilstm_with_glove_final.h5')

# 比较不同模型的性能
model_names = ['双向LSTM', 'CNN+双向LSTM', '双向LSTM+GloVe']
accuracies = [test_accuracy, glove_test_accuracy, glove_test_accuracy]  # 这里需要调整

# 如果是用bilstm模型，则第一个是bilstm，如果是hybrid模型，则第一个是hybrid
if MODEL_TYPE == 'bilstm':
    model_names[0] = '双向LSTM'
    accuracies[0] = test_accuracy
elif MODEL_TYPE == 'hybrid':
    model_names[0] = 'CNN+双向LSTM'
    accuracies[0] = test_accuracy

# 添加GloVe模型的准确率
if 'glove_test_accuracy' in locals():
    accuracies[2] = glove_test_accuracy

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(model_names[:len(accuracies)], accuracies, 
              color=['#3498db', '#2ecc71', '#e74c3c'], alpha=0.8)

# 添加数值标签
for bar, acc in zip(bars, accuracies):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{acc:.4f}', ha='center', va='bottom', fontsize=12)

ax.set_ylabel('准确率', fontsize=12)
ax.set_title('不同模型在IMDb情感分析任务上的性能比较', fontsize=14)
ax.set_ylim([0, 1.0])
ax.grid(True, alpha=0.3, axis='y')
plt.show()

# 模型总结
print("=" * 60)
print("模型总结")
print("=" * 60)
print(f"1. 模型类型: {model_name}")
print(f"2. 词汇表大小: {vocab_size}")
print(f"3. 序列最大长度: {max_sequence_length}")
print(f"4. 训练样本数: {len(X_train)}")
print(f"5. 测试样本数: {len(X_test)}")
print(f"6. 最终准确率: {test_accuracy:.4f}")
print(f"7. 最终F1分数: {test_f1:.4f}")

if 'glove_test_accuracy' in locals():
    print(f"\n使用GloVe词向量:")
    print(f"  词向量维度: {EMBEDDING_DIM}")
    print(f"  词汇表覆盖率: {coverage:.2%}")
    print(f"  准确率: {glove_test_accuracy:.4f}")
    print(f"  F1分数: {glove_test_f1:.4f}")

class SentimentAnalyzer:
    """情感分析器，使用训练好的模型进行预测"""
    def __init__(self, model, preprocessor, model_type='bilstm'):
        self.model = model
        self.preprocessor = preprocessor
        self.model_type = model_type
        
    def predict_sentiment(self, text):
        """预测单条文本的情感"""
        # 将文本转换为序列
        sequence = self.preprocessor.texts_to_sequences([text])
        
        # 预测
        prediction = self.model.predict(sequence, verbose=0)[0][0]
        
        # 判断情感
        sentiment = "正面" if prediction > 0.5 else "负面"
        confidence = prediction if prediction > 0.5 else 1 - prediction
        
        # 获取关键情感词
        cleaned_text = self.preprocessor.clean_text(text)
        tokens = self.preprocessor.tokenize(cleaned_text)
        
        # 找出在词汇表中的情感词
        emotion_words = []
        for token in tokens[:10]:  # 只检查前10个词
            if token in self.preprocessor.word_index:
                emotion_words.append(token)
        
        return {
            'sentiment': sentiment,
            'confidence': float(confidence),
            'probability': float(prediction),
            'emotion_words': emotion_words[:5]  # 返回前5个情感词
        }
    
    def analyze_examples(self, examples):
        """分析多个示例"""
        print("情感分析演示:")
        print("=" * 80)
        
        results = []
        for i, example in enumerate(examples):
            result = self.predict_sentiment(example)
            results.append(result)
            
            print(f"示例 {i+1}:")
            print(f"  文本: {example[:100]}..." if len(example) > 100 else f"  文本: {example}")
            print(f"  情感: {result['sentiment']}")
            print(f"  置信度: {result['confidence']:.2%}")
            print(f"  情感词: {', '.join(result['emotion_words']) if result['emotion_words'] else '未识别到明显情感词'}")
            print("-" * 80)
        
        return results

# 创建情感分析器
analyzer = SentimentAnalyzer(best_model, preprocessor)

# 测试示例
test_examples = [
    "This movie was absolutely fantastic! The acting was superb and the plot was engaging from start to finish.",
    "A complete waste of time. Poor acting, terrible script, and boring direction.",
    "It was okay. Not great, but not terrible either. Some parts were good, others were mediocre.",
    "I loved this film! The characters were well-developed and the story was emotionally moving.",
    "One of the worst movies I've ever seen. I can't believe I wasted two hours of my life on this.",
    "The cinematography was beautiful, but the story felt weak and predictable.",
    "An excellent performance by the lead actor, though the supporting cast was weak.",
    "Boring, predictable, and overrated. I don't understand the positive reviews.",
]

results = analyzer.analyze_examples(test_examples)

# 统计结果
sentiments = [result['sentiment'] for result in results]
positive_count = sentiments.count('正面')
negative_count = sentiments.count('负面')

print("\n统计结果:")
print(f"正面情感: {positive_count} 条")
print(f"负面情感: {negative_count} 条")
print(f"平均置信度: {np.mean([r['confidence'] for r in results]):.2%}")

def sentiment_analysis_pipeline(text, model_path=None, preprocessor=None):
    """
    完整的情感分析流程
    
    参数:
    text: 要分析的文本
    model_path: 模型文件路径（可选）
    preprocessor: 预处理器对象（可选）
    
    返回:
    情感分析结果字典
    """
    # 如果提供了模型路径，则加载模型
    if model_path and os.path.exists(model_path):
        from tensorflow.keras.models import load_model
        model = load_model(model_path)
    else:
        model = best_model  # 使用当前训练的模型
    
    # 如果提供了预处理器，则使用它
    if not preprocessor:
        preprocessor = TextPreprocessor(max_vocab_size=20000, max_sequence_length=200)
        # 注意：这里需要已经构建好的词汇表
    
    # 创建分析器
    analyzer = SentimentAnalyzer(model, preprocessor)
    
    # 分析文本
    result = analyzer.predict_sentiment(text)
    
    return result

# 使用示例
print("部署示例:")
print("=" * 80)

sample_text = "This is an amazing movie with brilliant performances and a captivating story."
result = sentiment_analysis_pipeline(sample_text)

print(f"输入文本: {sample_text}")
print(f"分析结果: {result['sentiment']} (置信度: {result['confidence']:.2%})")
print(f"详细概率: {result['probability']:.4f}")

# 批量处理函数
def batch_sentiment_analysis(texts, model_path=None):
    """
    批量情感分析
    
    参数:
    texts: 文本列表
    model_path: 模型文件路径
    
    返回:
    结果列表
    """
    results = []
    
    for text in texts:
        result = sentiment_analysis_pipeline(text, model_path)
        results.append(result)
    
    return results

# 批量处理示例
batch_texts = [
    "I really enjoyed this movie!",
    "The worst film I've seen this year.",
    "Average movie, nothing special.",
]

batch_results = batch_sentiment_analysis(batch_texts)

print("\n批量处理结果:")
for i, (text, result) in enumerate(zip(batch_texts, batch_results)):
    print(f"{i+1}. '{text}' -> {result['sentiment']} ({result['confidence']:.2%})")

print("=" * 80)
print("双向LSTM情感分析模型优化建议")
print("=" * 80)

print("""
1. 数据层面优化:
   - 使用全部数据（50,000条评论）而不是子集
   - 数据增强：通过同义词替换、回译等方法增加训练数据
   - 处理类别不平衡（如果存在）

2. 模型架构优化:
   - 增加LSTM层数（但要注意梯度消失问题）
   - 使用注意力机制增强重要词的影响力
   - 尝试Transformer架构（如BERT）
   - 调整嵌入维度、LSTM单元数等超参数

3. 训练策略优化:
   - 使用更复杂的学习率调度策略（如余弦退火）
   - 增加正则化（如权重衰减）
   - 使用标签平滑技术
   - 尝试不同的优化器（如AdamW）

4. 特征工程优化:
   - 使用更先进的预训练词向量（如FastText、ELMo）
   - 结合字符级特征
   - 添加情感词典特征
   - 使用句法分析信息

5. 集成方法:
   - 创建多个不同架构的模型进行集成
   - 使用投票法或加权平均法结合预测结果
   - 尝试堆叠泛化（Stacking）

6. 部署优化:
   - 将模型转换为TensorFlow Lite格式以部署到移动设备
   - 使用TensorFlow Serving进行服务器端部署
   - 优化推理速度（如使用量化）
""")

print("\n总结:")
print(f"- 当前模型在测试集上达到了 {test_accuracy:.2%} 的准确率")
print(f"- 使用预训练词向量（如GloVe）通常能提升模型性能")
print(f"- 双向LSTM能有效捕捉文本中的上下文信息")
print(f"- 混合架构（CNN+LSTM）能同时捕捉局部和全局特征")