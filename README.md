# DiagTCM
中医多轮问诊

1.初始问句生成inital_sentence(list:systom)

从医案中随机取3个证候,调用4o生成初始问句inital_sen

@李贝

2.根据初始问句得到候选证型列表get_candidates(inital_sen)

返回字典candidates

@云梦

3.待询问下k个证候, get_systoms(k, candidates)

返回list, systoms

@伟豪

4.
