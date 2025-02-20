from collections import Counter
import math


class DiagnosticSystem:
    def __init__(self, disease_symptoms):
        """
        初始化诊断系统
        disease_symptoms: Dict[str, Set[str]] - 疾病名称到症状集合的映射
        """
        self.disease_symptoms = disease_symptoms
        self.all_symptoms = set().union(*disease_symptoms.values())

    def calculate_next_symptom(self, current_symptoms, denied_symptoms):
        """
        基于当前症状计算下一个最优询问症状
        current_symptoms: Set[str] - 当前已知的症状集合
        denied_symptoms: Set[str] - 患者已否认的症状集合
        returns: str - 下一个应该询问的症状
        """
        # 获取符合当前症状的候选疾病（部分匹配）
        candidate_diseases = self._get_candidate_diseases(current_symptoms)

        if not candidate_diseases:
            return None  # 无匹配疾病，返回 None

        # 计算剩余症状的信息增益，排除已否认的症状
        remaining_symptoms = self.all_symptoms - current_symptoms - denied_symptoms
        symptom_scores = {}

        for symptom in remaining_symptoms:
            score = self._calculate_information_gain(symptom, candidate_diseases)
            symptom_scores[symptom] = score

        # 选择信息增益最高的症状，如果信息增益都为 0，则选最小字母序
        if not symptom_scores or all(score == 0 for score in symptom_scores.values()):
            return min(remaining_symptoms) if remaining_symptoms else None

        return max(symptom_scores.items(), key=lambda x: (x[1], x[0]))[0]

    def _get_candidate_diseases(self, current_symptoms):
        """
        获取包含部分匹配当前症状的疾病，并按匹配度排序
        """
        candidates = {}

        for disease, symptoms in self.disease_symptoms.items():
            match_count = len(current_symptoms & symptoms)  # 交集症状数
            if match_count > 0:
                candidates[disease] = (symptoms, match_count)

        # 按匹配度排序（交集越多越优先）
        sorted_candidates = {
            k: v[0] for k, v in sorted(candidates.items(), key=lambda x: -x[1][1])
        }

        return sorted_candidates

    def _calculate_information_gain(self, symptom, candidate_diseases):
        """
        计算某个症状的信息增益
        使用二分类熵来评估症状的区分能力
        """
        total = len(candidate_diseases)
        if total == 0:
            return 0

        # 计算当前的熵
        current_entropy = math.log2(total) if total > 1 else 0

        # 统计有该症状和没有该症状的疾病数量
        with_symptom = sum(1 for symptoms in candidate_diseases.values() if symptom in symptoms)
        without_symptom = total - with_symptom

        # 避免 log2(0) 错误
        epsilon = 1e-9
        conditional_entropy = 0
        if with_symptom > 0:
            conditional_entropy += (with_symptom / total) * -math.log2(with_symptom / total + epsilon)
        if without_symptom > 0:
            conditional_entropy += (without_symptom / total) * -math.log2(without_symptom / total + epsilon)

        # 返回信息增益
        return current_entropy - conditional_entropy

    def get_disease_match_scores(self, symptoms):
        """
        计算症状与各个疾病的匹配度
        """
        scores = {}

        if len(symptoms) == 0:
            return {disease: 0.0 for disease in self.disease_symptoms}

        for disease, disease_symptoms in self.disease_symptoms.items():
            match_count = len(symptoms & disease_symptoms)  # 交集
            total_disease_symptoms = len(disease_symptoms)  # 该疾病所有症状数量
            match_rate = match_count / total_disease_symptoms  # 计算匹配率

            scores[disease] = match_rate

        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
