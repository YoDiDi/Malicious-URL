import sys
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
import urllib

import pickle
import html
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication,QLabel
from PyQt5.Qt import QLineEdit
from PyQt5.QtGui import QIcon

class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        btn1 = QPushButton("识别", self)
        btn1.move(140, 80)
        btn1.clicked.connect(self.buttonClicked)

        self.label1 = QLabel("请输入需要识别的URL：",self)
        self.label1.move(10,20)
        self.label1.resize(120, 40)

        self.textbox = QLineEdit(self)
        self.textbox.move(140, 20)
        self.textbox.resize(280, 40)
        self.statusBar()

        self.setGeometry(300, 300, 590, 250)
        self.setWindowTitle('识别URL系统')
        self.setWindowIcon(QIcon('1.png'))
        self.show()

    def buttonClicked(self):
        url = self.textbox.text()
        sender = self.sender()
        result = w.predict([url])
        self.statusBar().showMessage(result)

class WAF(object):

    def __init__(self):
        good_query_list = self.get_query_list('goodqueries.txt')
        bad_query_list = self.get_query_list('badqueries.txt')

        good_y = [0 for i in range(0, len(good_query_list))]
        bad_y = [1 for i in range(0, len(bad_query_list))]

        queries = bad_query_list + good_query_list
        y = bad_y + good_y

        # converting data to vectors  定义矢量化实例
        self.vectorizer = TfidfVectorizer(tokenizer=self.get_ngrams)

        # 把不规律的文本字符串列表转换成规律的 ( [i,j],tdidf值) 的矩阵X
        # 用于下一步训练分类器 lgs
        X = self.vectorizer.fit_transform(queries)

        # 使用 train_test_split 分割 X y 列表
        # X_train矩阵的数目对应 y_train列表的数目(一一对应)  -->> 用来训练模型
        # X_test矩阵的数目对应 	 (一一对应) -->> 用来测试模型的准确性
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, random_state=42)

        # 定理逻辑回归方法模型
        self.lgs = LogisticRegression()

        # 使用逻辑回归方法训练模型实例 lgs
        self.lgs.fit(X_train, y_train)

        # 使用测试值 对 模型的准确度进行计算
        print('模型的准确度:{}'.format(self.lgs.score(X_test, y_test)))

    # 对 新的请求列表进行预测
    def predict(self, new_queries):
        global tmp
        new_queries = [urllib.parse.unquote(url) for url in new_queries]
        X_predict = self.vectorizer.transform(new_queries)
        res = self.lgs.predict(X_predict)
        res_list = []
        for q, r in zip(new_queries, res):
            tmp = '正常请求' if r == 0 else '恶意请求'
            print('{}  {}'.format(q,tmp))

            if tmp == '正常请求':
                with open('goodqueries.txt','a+') as f:
                    # TODO 对文件名的修改，将good.txt改成goodqueries.txt，方便样本集的聚合，只读取goodqueries.txt与badqueries.txt两个样本集
                    f.writelines(q + '\n')
                    f.close()
            else :
                with open('badqueries.txt','a+') as f:
                    # TODO 对文件名的修改，bad.txt改成badqueries.txt，方便样本集的聚合，只读取goodqueries.txt与badqueries.txt两个样本集
                    f.writelines(q + '\n')
                    f.close()

            q_entity = html.escape(q)
            res_list.append({'url': q_entity, 'res': tmp})
        # print("预测的结果列表:{}".format(str(res_list)))
        return tmp

    # 得到文本中的请求列表打开文本文档中，提取数据
    def get_query_list(self, filename):
        directory = str(os.getcwd())
        # directory = str(os.getcwd())+'/module/waf'
        filepath = directory + "/" + filename
        data = open(filepath, 'r',encoding='utf-8').readlines()
        query_list = []
        for d in data:
            d = str(urllib.parse.unquote(d))  # converting url encoded data to simple string
            # print(d)   #输出数据
            query_list.append(d)
        return list(set(query_list))

    # tokenizer function, this will make 3 grams of each query
    def get_ngrams(self, query):
        tempQuery = str(query)
        ngrams = []
        for i in range(0, len(tempQuery) - 3):
            ngrams.append(tempQuery[i:i + 3])
        return ngrams

if __name__ == '__main__':

    with open('lgs.pickle', 'rb') as input:
        w = pickle.load(input)

app = QApplication(sys.argv)
ex = Example()
sys.exit(app.exec_())