import math
from itertools import combinations
import numpy as np

class DiagnosticSystem:
    def __init__(self, disease_symptoms):
        """
        初始化诊断系统
        disease_symptoms: Dict[str, Set[str]] - 疾病名称到症状集合的映射
        """
        self.disease_symptoms = disease_symptoms
        self.all_symptoms = set().union(*disease_symptoms.values())

    def _get_candidate_diseases(self, current_symptoms):
        """
        根据当前已知症状返回候选疾病列表
        当前症状与疾病症状的交集不为空的疾病作为候选疾病
        """
        candidate_diseases = {}
        for disease, symptoms in self.disease_symptoms.items():
            intersection = current_symptoms & symptoms
            if intersection:  # 如果交集非空，说明此疾病是候选疾病
                candidate_diseases[disease] = symptoms
        return candidate_diseases

    def calculate_next_n_symptoms(self, current_symptoms, n, method='greedy', denied_symptoms=None):
        """
        计算下一轮应该询问的n个症状
        Parameters:
            current_symptoms: Set[str] - 当前已知的症状集合
            n: int - 下一轮需要询问的症状数量
            method: str - 使用的算法方法 ('greedy', 'exhaustive', 'genetic')
            denied_symptoms: Set[str] - 已否认的症状集合（可选）
        Returns:
            Set[str] - 建议询问的n个症状（当候选不足时可能少于n个）
        """
        if denied_symptoms is None:
            denied_symptoms = set()
        candidate_diseases = self._get_candidate_diseases(current_symptoms)
        # 使用所有尚未确认的症状（不剔除否认症状），但在评分时对否认症状施加惩罚
        available_symptoms = self.all_symptoms - current_symptoms

        # 如果可选症状数量不足，则返回全部（可能不足n个）
        if len(available_symptoms) < n:
            return available_symptoms

        if method == 'greedy':
            return self._greedy_selection(current_symptoms, candidate_diseases, available_symptoms, n, denied_symptoms)
        elif method == 'exhaustive':
            return self._exhaustive_search(current_symptoms, candidate_diseases, available_symptoms, n, denied_symptoms)
        elif method == 'genetic':
            return self._genetic_algorithm(current_symptoms, candidate_diseases, available_symptoms, n, denied_symptoms)
        else:
            raise ValueError("Unknown method")

    def _greedy_selection(self, current_symptoms, candidate_diseases, available_symptoms, n, denied_symptoms):
        """
        贪心选择n个症状，考虑否认症状惩罚
        """
        selected_symptoms = set()
        symptoms_list = list(available_symptoms)

        # 启发式排序：根据症状对当前疾病的影响排序，否认症状得分打折
        def symptom_score(symptom):
            score = self._calculate_symptom_importance(symptom, current_symptoms, candidate_diseases)
            if symptom in denied_symptoms:
                score *= 0.5  # 对否认症状施加惩罚
            return score

        symptoms_list.sort(key=lambda x: symptom_score(x), reverse=True)

        for _ in range(n):
            if not symptoms_list:
                break

            best_score = float('-inf')
            best_symptom = None

            for symptom in symptoms_list:
                temp_symptoms = current_symptoms | selected_symptoms | {symptom}
                score = self._calculate_combined_score(temp_symptoms, candidate_diseases)
                # 如果症状曾被否认，则降低组合得分
                if symptom in denied_symptoms:
                    score *= 0.5

                if score > best_score:
                    best_score = score
                    best_symptom = symptom

            if best_symptom:
                selected_symptoms.add(best_symptom)
                symptoms_list.remove(best_symptom)

        # 如果选择的症状不足n个，补充剩余中得分最高的
        if len(selected_symptoms) < n:
            remaining = [s for s in symptoms_list if s not in selected_symptoms]
            remaining.sort(key=lambda x: symptom_score(x), reverse=True)
            for s in remaining:
                if len(selected_symptoms) >= n:
                    break
                selected_symptoms.add(s)

        return selected_symptoms

    def _exhaustive_search(self, current_symptoms, candidate_diseases, available_symptoms, n, denied_symptoms):
        """
        穷举搜索，考虑否认症状惩罚
        """
        best_score = float('-inf')
        best_combination = None

        # 启发式排序：根据症状的重要性排序，否认症状得分打折
        def symptom_score(symptom):
            score = self._calculate_symptom_importance(symptom, current_symptoms, candidate_diseases)
            if symptom in denied_symptoms:
                score *= 0.5
            return score

        sorted_symptoms = sorted(available_symptoms, key=lambda x: symptom_score(x), reverse=True)

        # 通过启发式选择前若干症状进行组合
        for combo in combinations(sorted_symptoms, n):
            temp_symptoms = current_symptoms | set(combo)
            score = self._calculate_combined_score(temp_symptoms, candidate_diseases)
            # 对组合中包含否认症状进行惩罚
            denied_count = sum(1 for symptom in combo if symptom in denied_symptoms)
            score -= denied_count * 0.2
            if score > best_score:
                best_score = score
                best_combination = combo

        return set(best_combination) if best_combination else set()

    def _genetic_algorithm(self, current_symptoms, candidate_diseases, available_symptoms, n, denied_symptoms):
        """
        遗传算法，考虑否认症状惩罚，加入精英策略、动态变异率、局部搜索
        """
        population_size = 50
        generations = 30
        mutation_rate = 0.1
        elite_size = 5  # 保留精英个体

        remaining_list = list(available_symptoms)
        # 初始化种群：每个个体为一个n个症状的集合
        population = [set(np.random.choice(remaining_list, n, replace=False)) for _ in range(population_size)]

        def fitness(individual):
            temp_symptoms = current_symptoms | individual
            base_score = self._calculate_combined_score(temp_symptoms, candidate_diseases)
            # 对个体中出现的否认症状施加惩罚，每个否认症状扣0.2分
            penalty = 0.2 * sum(1 for symptom in individual if symptom in denied_symptoms)
            return base_score - penalty

        for generation in range(generations):
            fitness_scores = [fitness(individual) for individual in population]

            # 保留精英个体
            elite_individuals = [population[i] for i in np.argsort(fitness_scores)[-elite_size:]]

            # 选择操作：锦标赛选择
            new_population = elite_individuals[:]
            for _ in range((population_size - elite_size) // 2):
                parent1 = self._tournament_select(population, fitness_scores)
                parent2 = self._tournament_select(population, fitness_scores)

                child1, child2 = self._crossover(parent1, parent2, n)
                child1 = self._mutate(child1, available_symptoms, mutation_rate, n)
                child2 = self._mutate(child2, available_symptoms, mutation_rate, n)

                new_population.extend([child1, child2])

            population = new_population

            mutation_rate = max(0.01, mutation_rate * 0.95)  # 动态调整变异率

            population = [self._local_search(individual, current_symptoms, candidate_diseases) for individual in population]

        best_individual = max(population, key=lambda x: fitness(x))
        return best_individual

    def _local_search(self, individual, current_symptoms, candidate_diseases):
        """
        局部搜索：模拟退火，随机替换一个症状，若能提高组合得分则接受
        """
        best_individual = individual.copy()
        best_score = self._calculate_combined_score(current_symptoms | individual, candidate_diseases)

        for symptom in list(individual):
            new_individual = individual.copy()
            new_individual.remove(symptom)
            remaining_symptoms = self.all_symptoms - current_symptoms - individual
            if remaining_symptoms:
                new_symptom = np.random.choice(list(remaining_symptoms))
                new_individual.add(new_symptom)
                score = self._calculate_combined_score(current_symptoms | new_individual, candidate_diseases)
                if score > best_score:
                    best_score = score
                    best_individual = new_individual
        return best_individual

    def _calculate_symptom_importance(self, symptom, current_symptoms, candidate_diseases):
        """根据症状对候选疾病的影响计算症状重要性"""
        temp_symptoms = current_symptoms | {symptom}
        return self._calculate_combined_score(temp_symptoms, candidate_diseases)

    def _calculate_combined_score(self, symptoms, candidate_diseases):
        """
        计算症状组合的综合得分
        考虑信息增益和症状间的互补性
        """
        info_gain = self._calculate_total_information_gain(symptoms, candidate_diseases)
        coverage_score = self._calculate_coverage_score(symptoms, candidate_diseases)
        independence_score = self._calculate_independence_score(symptoms)
        return 0.4 * info_gain + 0.4 * coverage_score + 0.2 * independence_score

    def _calculate_total_information_gain(self, symptoms, candidate_diseases):
        """计算症状组合的总信息增益"""
        if len(candidate_diseases) == 0:
            return 0
        initial_entropy = math.log2(len(candidate_diseases))
        subgroups = self._split_by_symptoms(symptoms, candidate_diseases)
        conditional_entropy = 0
        total = len(candidate_diseases)
        for subgroup in subgroups:
            prob = len(subgroup) / total
            if prob > 0:
                conditional_entropy -= prob * math.log2(prob)
        return initial_entropy - conditional_entropy

    def _calculate_coverage_score(self, symptoms, candidate_diseases):
        """计算症状组合对疾病的覆盖程度"""
        total_coverage = 0
        for disease, disease_symptoms in candidate_diseases.items():
            coverage = len(symptoms & disease_symptoms) / len(disease_symptoms)
            total_coverage += coverage
        return total_coverage / len(candidate_diseases) if candidate_diseases else 0

    def _calculate_independence_score(self, symptoms):
        """计算症状间的独立性分数"""
        if len(symptoms) <= 1:
            return 1.0
        mutual_info = 0
        for s1, s2 in combinations(symptoms, 2):
            mutual_info += self._calculate_mutual_information(s1, s2)
        return 1.0 / (1.0 + mutual_info)

    def _calculate_mutual_information(self, symptom1, symptom2):
        """计算两个症状之间的互信息"""
        count_both = 0
        count_s1 = 0
        count_s2 = 0
        total = len(self.disease_symptoms)
        for symptoms in self.disease_symptoms.values():
            has_s1 = symptom1 in symptoms
            has_s2 = symptom2 in symptoms
            if has_s1 and has_s2:
                count_both += 1
            if has_s1:
                count_s1 += 1
            if has_s2:
                count_s2 += 1
        if count_both == 0:
            return 0
        p_both = count_both / total
        p_s1 = count_s1 / total
        p_s2 = count_s2 / total
        if p_both == 0 or p_s1 == 0 or p_s2 == 0:
            return 0
        return p_both * math.log2(p_both / (p_s1 * p_s2))

    def _split_by_symptoms(self, symptoms, candidate_diseases):
        """根据症状组合将疾病分组"""
        groups = {}
        for disease, disease_symptoms in candidate_diseases.items():
            key = tuple(symptom in disease_symptoms for symptom in symptoms)
            if key not in groups:
                groups[key] = []
            groups[key].append(disease)
        return list(groups.values())

    def _tournament_select(self, population, fitness_scores, tournament_size=3):
        """
        锦标赛选择：从种群中随机选取几个个体进行比赛，返回适应度最高的个体
        """
        indices = np.random.choice(len(population), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in indices]
        winner_idx = indices[np.argmax(tournament_fitness)]
        return population[winner_idx]

    def _crossover(self, parent1, parent2, n):
        """
        遗传算法的交叉操作，从父代生成子代，确保子代大小为n
        """
        combined = list(parent1 | parent2)
        if len(combined) > n:
            np.random.shuffle(combined)
            combined = combined[:n]
        while len(combined) < n:
            remaining = (parent1 | parent2) - set(combined)
            if not remaining:
                break
            combined.append(np.random.choice(list(remaining)))
        return set(combined), set(combined)

    def _mutate(self, individual, available_symptoms, mutation_rate, n):
        """
        遗传算法的变异操作，随机替换个体中的一个症状
        """
        if np.random.random() < mutation_rate:
            available = list(available_symptoms - individual)
            if available:
                symptom_to_replace = np.random.choice(list(individual))
                new_symptom = np.random.choice(available)
                individual.remove(symptom_to_replace)
                individual.add(new_symptom)
        return individual

    def get_disease_match_scores(self, current_symptoms):
        """
        计算当前已知症状与每种疾病的匹配度
        匹配度 = (匹配症状数) / (该疾病总症状数)
        """
        scores = {}
        for disease, symptoms in self.disease_symptoms.items():
            match_count = len(current_symptoms & symptoms)
            total_count = len(symptoms)
            scores[disease] = match_count / total_count if total_count > 0 else 0.0
        return scores

'''# 示例使用
def example_usage():
    disease_symptoms = {
        "感冒": {"发烧", "咳嗽", "流鼻涕", "头痛", "喉咙痛"},
        "流感": {"高烧", "咳嗽", "肌肉酸痛", "疲劳", "头痛", "恶心"},
        "新冠": {"发烧", "干咳", "疲劳", "嗅觉丧失", "味觉丧失", "呼吸困难"},
        "肺炎": {"高烧", "咳痰", "胸痛", "呼吸困难", "疲劳", "食欲不振"},
        "支气管炎": {"咳嗽", "咳痰", "胸闷", "呼吸困难", "低烧", "疲劳"}
    }
    system = DiagnosticSystem(disease_symptoms)
    current_symptoms = {"发烧", "咳嗽"}
    next_symptoms = system.calculate_next_n_symptoms(current_symptoms, 3, method='greedy', denied_symptoms={"流鼻涕"})
    print("下一轮询问的症状:", next_symptoms)

# example_usage()
'''

