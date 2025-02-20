import json


def load_or_map(filepath):
    """加载或关系的 JSON 文件"""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


# 加载 or_map
or_map = load_or_map("or_dict.json")

# 样例数据：每种疾病对应一组症状
disease_symptoms = {
    "感冒": {"发烧", "咳嗽", "流鼻涕", "头痛"},
    "流感": {"高烧", "咳嗽", "肌肉酸痛", "疲劳", "头痛"},
    "新冠": {"发烧", "干咳", "疲劳", "嗅觉丧失", "味觉丧失"},
    "肺炎": {"高烧", "咳痰", "胸痛", "呼吸困难", "疲劳"}
}

# 当前症状集合（示例）
current_symptoms = {"发烧", "咳嗽"}


def process_or(disease, current_symptoms, symptoms):
    """
    对于指定疾病，根据 or_map 中的规则处理症状。

    参数：
        disease: 疾病名称，用于获取 or_map 中该疾病的关系规则
        current_symptoms: 当前症状集合，复制一份用于迭代修改
        symptoms: 疾病对应的症状集合，需要根据 or 关系进行过滤

    逻辑：
        遍历 current_symptoms 中的每个症状，若该症状在 or_map 中有替代症状，
        则将替代症状从症状集合中移除（同时也从当前症状中删除）。
    """
    relations = or_map.get(disease, {})
    # 使用 current_symptoms 的拷贝用于遍历和修改
    use_current_symptoms = current_symptoms.copy()

    for symptom in list(use_current_symptoms):
        # 如果当前症状已被删除，则跳过
        if symptom not in use_current_symptoms:
            continue
        alternatives = relations.get(symptom, [])
        print(f"症状 {symptom} 的替代症状: {alternatives}")
        for alt in alternatives:
            print(f"移除替代症状: {alt}")
            if alt != symptom:
                symptoms.discard(alt)
                use_current_symptoms.discard(alt)

    return symptoms


def update_disease_symptoms(disease_symptoms, current_symptoms):
    """
    更新每种疾病对应的症状集合，根据 or 关系过滤替代症状，并返回一个新的字典。

    为避免不同疾病之间互相干扰，处理时均使用 current_symptoms 的拷贝。
    """
    updated_dict = {}
    for disease, symptoms in disease_symptoms.items():
        # 对每个疾病，均使用当前症状的拷贝和该疾病的症状集合进行处理
        updated_symptoms = process_or(disease, current_symptoms.copy(), set(symptoms))
        updated_dict[disease] = updated_symptoms
    return updated_dict


if __name__ == '__main__':
    updated_disease_symptoms = update_disease_symptoms(disease_symptoms, current_symptoms)
    print("修改后的完整 disease_symptoms:")
    for disease, symptoms in updated_disease_symptoms.items():
        print(f"{disease}: {symptoms}")
