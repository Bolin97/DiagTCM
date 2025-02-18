# DiagTCM
中医多轮问诊

1.初始问句生成inital_sentence(list:systom)

从医案中随机取3个证候,调用4o生成初始问句inital_sen

@李贝

2.根据初始问句得到候选证型列表get_candidates(inital_sen)

返回字典candidates

@云梦

3.待询问的k个证候及问句, get_systoms(k, candidates)

返回systoms列表和系统问句question 

@伟豪

4.根据测试集医案回答系统问句question, get_answer(systoms, question)

首先根据医案找到systoms中患者真实患有的证型, 然后调用4o生成一个可以回答question的句子

@李贝
