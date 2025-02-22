from flask import Flask, request, jsonify, render_template
import numpy as np

app = Flask(__name__)

# 存储不同阶数判断矩阵对应的随机一致性指标
random_index_dict = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


class EvaluateLibrary:
    def __init__(self, judgment_matrix):
        # 存储传入的判断矩阵
        self.judgment_matrix = judgment_matrix

    # 层次分析法寻找权重
    def ahp(self):
        # 获取判断矩阵
        matrix = self.judgment_matrix
        # 获取判断矩阵的阶数
        matrix_order = matrix.shape[0]

        # 检查矩阵阶数是否在有效范围内
        if matrix_order not in random_index_dict:
            print(f"矩阵阶数 {matrix_order} 不在有效范围内，请使用 1 - 10 阶的矩阵。")
            return None

        # 计算判断矩阵每列元素之和
        column_sums = matrix.sum(axis=0)
        # 对判断矩阵进行列归一化处理
        normalized_matrix = matrix / column_sums

        # 计算归一化矩阵每行元素之和
        row_sums_of_normalized_matrix = normalized_matrix.sum(axis=1)
        print(row_sums_of_normalized_matrix)
        # 计算去权重向量，由行求和求占比
        # 保留5位小数   也可以这样：weight_vector = [round(num, 5) for num in weight_vector]
        weight_vector = np.around(row_sums_of_normalized_matrix / matrix_order, 5)
        print(f"权重向量：{weight_vector}")

        # 计算判断矩阵与权重向量的乘积
        matrix_times_weight_vector = np.dot(matrix, weight_vector)
        # 计算判断矩阵的最大特征根
        max_eigenvalue = np.sum(matrix_times_weight_vector / (matrix_order * weight_vector))

        # 计算一致性指标
        consistency_index = (max_eigenvalue - matrix_order) / (matrix_order - 1)
        # 获取当前矩阵阶数对应的随机一致性指标
        random_index = random_index_dict[matrix_order]
        # 计算一致性比例
        consistency_ratio = consistency_index / random_index

        if consistency_ratio < 0.1:
            print("一致性检验通过，CR =", consistency_ratio)
            return weight_vector
        else:
            print("一致性检验未通过，CR =", consistency_ratio)
            return None


class FuzzyComprehensiveEvaluation:
    def __init__(self, weights, fuzzy_matrices, score_standard):
        """
        初始化综合评价类s
        :param weights: 权重列表，包含一级指标和二级指标的权重
        :param fuzzy_matrices: 模糊评价矩阵列表，每个矩阵对应一个一级指标
        :param score_standard: 评分标准，如 [100, 80, 60, 40, 0]
        """
        self.weights = weights
        self.fuzzy_matrices = fuzzy_matrices
        self.score_standard = score_standard
        self.S = []
        self.normalized_matrices = []

    def normalize_fuzzy_matrix(self, matrix):
        """
        归一化模糊评价矩阵
        :param matrix: 输入的模糊评价矩阵
        :return: 归一化后的模糊评价矩阵
        """
        row_sums = matrix.sum(axis=1, keepdims=True)
        normalized_matrix = matrix / row_sums
        return np.round(normalized_matrix, 5)

    def calculate_comprehensive_score(self):
        """
        计算综合评价得分
        :return: 综合评价得分
        """
        # 归一化模糊评价矩阵
        normalized_matrices = [self.normalize_fuzzy_matrix(matrix) for matrix in self.fuzzy_matrices]
        print(normalized_matrices)
        self.normalized_matrices = normalized_matrices
        # 计算一级指标的综合评价结果
        S1 = [np.round(np.dot(weights, matrix), 6) for weights, matrix in zip(self.weights[1:], normalized_matrices)]
        # 将一级指标的综合评价结果组合成矩阵
        print(S1)
        S = np.array(S1)
        print(S)
        self.S = S
        # 计算最终的综合评价结果
        S_final = np.round(np.dot(self.weights[0], S), 4)

        # 计算综合得分
        final_score = round(np.dot(S_final, self.score_standard), 2)

        return S_final, final_score

    def calculate_every_secondary_item_score(self):
        '''计算每一个一级指标下二级指标各项得分'''
        result = {}
        for i, matrix in enumerate(self.normalized_matrices):
            # 对每行与标准分进行点乘
            scores = np.dot(matrix, self.score_standard)
            for j in range(len(scores)):
                result[f"第{i + 1}项一级指标的第{j + 1}二级指标（A{i + 1}{j + 1}）的得分："] = round(scores[j], 2)
        return result

    def calculate_every_secondary_score(self):
        '''计算每一个一级指标下二级指标得分'''
        result = {}
        S = self.S
        secondary_scores = np.dot(S, self.score_standard)
        for j in range(len(secondary_scores)):
            result[f"第{j + 1}项指标的二级指标的总得分："] = round(secondary_scores[j], 2)
        return result


@app.route('/')
def index():
    return render_template('综合指标计算.html')  # 确保在 templates 目录下有 index.html 文件

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # 获取请求的 JSON 数据
        data = request.json
        print("收到的数据:", data)

        primary_matrices = []
        for key, matrix in data.get('primaryMatrices', {}).items():
            if matrix:
                primary_matrices.append(np.array(matrix, dtype=float))
            else:
                print(f"警告: primaryMatrices 中 {key} 矩阵为空")

        secondary_matrices = []
        for key, matrix in data.get('secondaryMatrices', {}).items():
            if matrix:
                secondary_matrices.append(np.array(matrix, dtype=float))
            else:
                print(f"警告: secondaryMatrices 中 {key} 矩阵为空")

        fuzzy_evaluation_matrices = []
        for key, matrix in data.get('fuzzyevaluationMatrices', {}).items():
            if matrix:
                fuzzy_evaluation_matrices.append(np.array(matrix, dtype=float))
            else:
                print(f"警告: fuzzy-evaluation-matrices 中 {key} 矩阵为空")

        print("一级指标矩阵:", primary_matrices)
        print("二级指标矩阵:", secondary_matrices)
        print("模糊评价矩阵:", fuzzy_evaluation_matrices)

        score_standard = data.get("score_standard", [100, 80, 60, 40, 0])

        primary_matrices = []
        for key, matrix in data.get('primaryMatrices', {}).items():
            if matrix:
                primary_matrices.append(np.array(matrix, dtype=float))
            else:
                print(f"警告: primaryMatrices 中 {key} 矩阵为空")
        #后端返回到前端的东西
        secondary_matrices = []
        for key, matrix in data.get('secondaryMatrices', {}).items():
            if matrix:
                secondary_matrices.append(np.array(matrix, dtype=float))
            else:
                print(f"警告: secondaryMatrices 中 {key} 矩阵为空")

        fuzzy_evaluation_matrices = []
        for key, matrix in data.get('fuzzyevaluationMatrices', {}).items():
            if matrix:
                fuzzy_evaluation_matrices.append(np.array(matrix, dtype=float))
            else:
                print(f"警告: fuzzy-evaluation-matrices 中 {key} 矩阵为空")

        print("一级指标矩阵:", primary_matrices)
        print("二级指标矩阵:", secondary_matrices)
        print("模糊评价矩阵:", fuzzy_evaluation_matrices)

        # 保存权重 (对一级和二级指标矩阵进行评估)
        Ahm = [EvaluateLibrary(primary_matrice) for primary_matrice in primary_matrices]  # Analytic_Hierarchy_Matrices
        Ahm.extend([EvaluateLibrary(secondary_matrice) for secondary_matrice in secondary_matrices])

        A = []
        for i in range(len(Ahm)):
            A.append(Ahm[i].ahp())
        print(A)
        # 创建模糊综合评价实例并计算综合评分
        fce = FuzzyComprehensiveEvaluation(A, fuzzy_evaluation_matrices, score_standard)
        S_final, final_score = fce.calculate_comprehensive_score()
        # 输出结果
        print("最终的综合评价结果（模糊向量）：", S_final)
        print("综合得分：", final_score)
        dict1=fce.calculate_every_secondary_score()
        dict2=fce.calculate_every_secondary_item_score()
        # 返回计算结果
        return jsonify({
            "final_score":final_score,
            "All_primary_score":dict1,
            "All_secondary_score":dict2

        })

    except Exception as e:
        print(f"发生错误: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)