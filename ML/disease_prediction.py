import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree._tree import TREE_UNDEFINED


class PredictDisease:
    def __init__(self):
        # training = pd.read_csv('ML\\training.csv')
        training = pd.read_csv('https://raw.githubusercontent.com/therealrahulsahu/MajorProject/master/ML/training.csv?token=AKMU2BQARK7V5PRRDOBXINTAHUV4I')
        feature_names = training.columns[:-1]
        x = training[feature_names]
        y = training['prognosis']
        self.reduced_data = training.groupby(training['prognosis']).max()

        self.__le = preprocessing.LabelEncoder()
        self.__le.fit(y)
        y = self.__le.transform(y)

        clf = DecisionTreeClassifier()
        clf = clf.fit(x, y)
        self.tree = clf.tree_

        self.feature_name = [
            feature_names[i] if i != TREE_UNDEFINED else "undefined!"
            for i in self.tree.feature
        ]
        self.__make_first_list(self.feature_name)
        self.symptoms_present = []

    def __make_first_list(self, data):
        i = 0
        self.__indexed_disease = {}
        while i < len(data):
            if data[i] != 'undefined!':
                self.__indexed_disease[data[i]] = i
            i += 1
        self.__first_sym_list = list(self.__indexed_disease.keys())

    def get_disease_list(self):
        return self.__first_sym_list

    def __get_disease(self, node):
        node = node[0]
        val = node.nonzero()
        disease = self.__le.inverse_transform(val[0])
        return disease

    def predict(self, name):
        node = self.__indexed_disease[name]
        if 1 <= self.tree.threshold[node]:
            node = self.tree.children_left[node]
        else:
            node = self.tree.children_right[node]

        if self.tree.feature[node] == TREE_UNDEFINED:
            return self.__may_have(node)
        else:
            return {
                'final': int(0),
                'name': self.feature_name[node],
                'node': int(node),
            }

    def recurse_predict(self, node, choice):
        node = np.int64(node)
        if choice <= self.tree.threshold[node]:
            node = self.tree.children_left[node]
        else:
            node = self.tree.children_right[node]

        if self.tree.feature[node] == TREE_UNDEFINED:
            return self.__may_have(node)
        else:
            return {
                'final': int(0),
                'name': self.feature_name[node],
                'node': int(node),
            }

    def __may_have(self, node):
        node = np.int64(node)
        present_disease = self.__get_disease(self.tree.value[node])
        red_cols = self.reduced_data.columns
        symptoms_given = red_cols[self.reduced_data.loc[present_disease].values[0].nonzero()]
        return {
            'final': int(1),
            'node': int(node),
            'may_be_list': list(symptoms_given),
        }

    def final_result(self, node, symptoms_present):
        node = np.int64(node)
        present_disease = self.__get_disease(self.tree.value[node])

        red_cols = self.reduced_data.columns
        symptoms_given = red_cols[self.reduced_data.loc[present_disease].values[0].nonzero()]

        return {
            'final': int(2),
            'disease': present_disease[0],
            'c_level': float((1.0 * len(symptoms_present) / len(symptoms_given)))
        }
