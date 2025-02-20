from single import DiagnosticSystem


def multi_round_diagnosis(max_rounds=5, probability_threshold=0.8):
    # 初始化候选症型
    disease_symptoms = {
        "感冒": {"发烧", "咳嗽", "流鼻涕", "头痛"},
        "流感": {"高烧", "咳嗽", "肌肉酸痛", "疲劳", "头痛"},
        "新冠": {"发烧", "干咳", "疲劳", "嗅觉丧失", "味觉丧失"},
        "肺炎": {"高烧", "咳痰", "胸痛", "呼吸困难", "疲劳"}
    }

    # 初始化患者已有症候
    current_symptoms = {"发烧", "咳嗽"}
    denied_symptoms = set()

    system = DiagnosticSystem(disease_symptoms)

    print("初始已知症候:", current_symptoms)

    round_count = 0

    while round_count < max_rounds:
        round_count += 1
        print(f"\n第 {round_count} 轮问诊...")

        # 选择下一个要询问的症状
        next_symptom = system.calculate_next_symptom(current_symptoms, denied_symptoms)

        if next_symptom is None:
            print("没有更多症状可询问，诊断结束。")
            break

        # 生成问题询问患者
        user_input = input(f"您是否有'{next_symptom}'? (输入症候名称/none): ")

        if user_input.lower() == "none":
            denied_symptoms.add(next_symptom)  # 记录该症状被否认
        else:
            current_symptoms.add(user_input)  # 记录该症状

        # 计算当前匹配的疾病概率
        scores = system.get_disease_match_scores(current_symptoms)

        print("\n当前疾病匹配概率:")
        for disease, score in scores.items():
            print(f"{disease}: {score:.2%}")

        # 检查是否有疾病的概率达到 80%
        for disease, score in scores.items():
            if score >= probability_threshold:
                print(f"\n诊断结束，可能的疾病为: {disease}，概率达到 {score:.2%}")
                return

    print("\n问诊达到最大轮数，最终可能的疾病匹配度:")
    scores = system.get_disease_match_scores(current_symptoms)
    for disease, score in scores.items():
        print(f"{disease}: {score:.2%}")


if __name__ == "__main__":
    multi_round_diagnosis()
