from multi import DiagnosticSystem

def multi_round_diagnosis(max_rounds=5, probability_threshold=0.8, method='exhaustive', num_questions=3):
    """
    进行多轮问诊，使用multi.py的诊断算法
    :param max_rounds: 最大问诊轮数
    :param probability_threshold: 诊断终止的概率阈值
    :param method: 症状选择方法（'greedy', 'exhaustive', 'genetic'）
    :param num_questions: 每轮询问的症状数量
    """
    disease_symptoms = {
        "感冒": {"发烧", "咳嗽", "流鼻涕", "头痛"},
        "流感": {"高烧", "咳嗽", "肌肉酸痛", "疲劳", "头痛"},
        "新冠": {"发烧", "干咳", "疲劳", "嗅觉丧失", "味觉丧失"},
        "肺炎": {"高烧", "咳痰", "胸痛", "呼吸困难", "疲劳"}
    }

    # 初始化诊断系统
    system = DiagnosticSystem(disease_symptoms)

    # 初始化患者症状
    current_symptoms = {"发烧", "咳嗽"}
    denied_symptoms = set()

    print("初始已知症候:", current_symptoms)

    for round_count in range(1, max_rounds + 1):
        print(f"\n第 {round_count} 轮问诊...")

        # 通过 multi 计算要询问的症状，让 multi 处理否认症候
        next_symptoms = system.calculate_next_n_symptoms(
            current_symptoms, num_questions, method=method, denied_symptoms=denied_symptoms
        )

        print(f"下一个询问的症状: {next_symptoms}")

        if not next_symptoms:
            print("没有更多症状可询问，诊断结束。")
            break

        symptom_list = ", ".join(next_symptoms)
        user_input = input(f"你还有{symptom_list}这些症状吗? (输入症状名称, 用逗号分隔): ")
        confirmed_symptoms = set(user_input.split(',')) if user_input.strip() else set()

        for symptom in next_symptoms:
            if symptom in confirmed_symptoms:
                current_symptoms.add(symptom)
            else:
                denied_symptoms.add(symptom)

        print( f"否认的症状: {denied_symptoms}")

        # 计算当前匹配的疾病概率
        scores = system.get_disease_match_scores(current_symptoms)

        print("\n当前疾病匹配概率:")
        for disease, score in scores.items():
            print(f"{disease}: {score:.2%}")

        # 检查是否有疾病的概率达到阈值
        for disease, score in scores.items():
            if score >= probability_threshold:
                print(f"\n诊断结束，可能的疾病为: {disease}，概率达到 {score:.2%}")
                return

    print("\n问诊达到最大轮数，最终可能的疾病匹配度:")
    scores = system.get_disease_match_scores(current_symptoms)
    for disease, score in scores.items():
        print(f"{disease}: {score:.2%}")


if __name__ == "__main__":
    multi_round_diagnosis(method='genetic', num_questions=2)
