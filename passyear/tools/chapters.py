#!/usr/bin/env python
"""大题 → chapter 分工表（与 ../classification.md 同源，改一处两处都要改）。

每条 = (卷 key, 大题号, 分值, 一句话主题, 兼章列表)
"""

CHAPTERS = {
    1: ("Atomic structure", [
        ("9701_w24_21", 1, 16, "cobalt 电子构型、1s orbital 形状、Rh/Ir isotopes、Aᵣ 计算", [2]),
        ("9701_w24_22", 1, 9,  "vanadium ground state、electrons-in-boxes、p sub-shell 计数、isotopes", []),
        ("9701_s25_21", 2, 11, "iron mass spectrum 读图、Aᵣ 计算、protons/nucleons", [22]),
        ("9701_s25_22", 2, 10, "Aᵣ 定义、第三种 iron isotope 的 relative isotopic mass、3d sub-shell", []),
        ("9701_s25_23", 1, 10, "fluorine 全电子构型、n=2 电子对、calcium 最高能级 orbital、S 的 IE", []),
        ("9701_w25_21", 1, 20, "chromium isotopes、mass spectrometry、电子构型", [7]),
        ("9701_w25_22", 1, 10, "manganese-55 粒子数、isotopes 定义、求 Aᵣ 所需信息", []),
        ("9701_s26_22", 2, 6,  "质子/中子/电子在电场中的偏转、质荷比推理", []),
    ]),
    2: ("Atoms, molecules and stoichiometry", [
        ("9701_s25_21", 4, 9, "vitamin C empirical formula、I₂(aq) titration 定量计算", []),
        ("9701_s25_22", 5, 5, "vitamin C empirical formula、柠檬中 vitamin C 质量的滴定计算", []),
    ]),
    3: ("Chemical bonding", [
        ("9701_m24_22", 1, 16, "bismuth metallic bonding 图、Bi₂O₃ 结构与键型推断", [9]),
        ("9701_s24_21", 2, 12, "SCl₂ 水解、dot-and-cross、分子形状与键角", [9]),
        ("9701_s24_21", 5, 9,  "covalent bond 定义、σ/π 轨道重叠图、sp² hybridisation", [14]),
        ("9701_s24_23", 1, 13, "N₂ 惰性、σ/π 键数与重叠方式、Al 的 oxidation number", [12]),
        ("9701_s24_23", 4, 16, "NH₄Cl 的 ionic/covalent/dative 键、NH₃ 与 OH⁻ 作 nucleophile", [19]),
        ("9701_w24_21", 3, 20, "Group 14 C/Sn 结构与导电性、graphite 晶格", [4, 9]),
        ("9701_s25_21", 1, 11, "sodium / sodium oxide 键型与导电性、与水反应", [9]),
        ("9701_s25_22", 1, 16, "diamond / graphite 晶格与导电性、PCl₅ 与 SiCl₄ 水解", [9]),
        ("9701_s26_21", 1, 17, "SF₆ dot-and-cross 与形状、orbital 形状、IE 趋势、SCl₂ 极性", [1]),
        ("9701_s26_22", 1, 14, "oxygen 2p 电子、orbital 形状、Li₂O dot-and-cross 与水解", [1]),
    ]),
    4: ("States of matter", [
        ("9701_s26_23", 2, 9, "Group 18 原子半径趋势、ideal gas 行为判断、pV = nRT 求 Mᵣ", []),
    ]),
    5: ("Chemical energetics", [
        ("9701_s24_21", 4, 6,  "enthalpy change of formation 定义、Fe₂O₃ + CO 的 Hess 计算", []),
        ("9701_s24_22", 2, 10, "reaction pathway diagram、Na₂CO₃/NaHCO₃ + HCl 的量热与 Hess", []),
        ("9701_s24_23", 3, 7,  "H₂O 生成焓方程、B₂O₃ + NH₃ 的 ΔH 计算", []),
    ]),
    7: ("Equilibria", [
        ("9701_s24_21", 3, 9,  "Le Chatelier 定义、Fe³⁺/SCN⁻ 升温对平衡的影响", []),
        ("9701_s24_22", 3, 12, "dynamic equilibrium、加 KSCN 的移动、Kc", []),
        ("9701_s24_23", 2, 14, "Haber process 三组条件下的 NH₃ 产率比较", []),
        ("9701_m26_22", 4, 19, "weak acid 定义、pH 滴定曲线、中和离子方程", [18]),
        ("9701_s26_21", 2, 9,  "Contact process stage 2/3、Le Chatelier 预测产率", [12]),
        ("9701_s26_23", 3, 13, "Contact process 反应能量图、Le Chatelier、工业条件权衡", [5]),
    ]),
    8: ("Reaction kinetics", [
        ("9701_s25_21", 3, 10, "Boltzmann distribution 升温曲线、nickel catalyst、EA；后半为 Le Chatelier 与产率-压强图", [7]),
        ("9701_s25_23", 4, 11, "Na₂S₂O₃ + HCl 浓度-时间曲线读图求平均速率", []),
    ]),
    9: ("The Periodic Table: chemical periodicity", [
        ("9701_m24_22", 2, 18, "Period 3 chlorides 结构/键型/pH、Cl₂ + NaOH disproportionation", [11]),
        ("9701_s24_22", 1, 15, "Mg²⁺/Al³⁺ 离子半径、sodium 结构、Period 3 熔点变化", [1]),
        ("9701_w24_22", 2, 15, "Na/S 与 O₂ 的方程、Al₂O₃ dot-and-cross、Period 3 oxides 与水", []),
        ("9701_m25_22", 1, 17, "PCl₃/PCl₅ oxidation number、平衡条件、Period 3 性质", [7]),
        ("9701_s25_23", 2, 8,  "Period 3 oxides 的 pH、P₄O₁₀ + NaOH、氧化物熔点与键型", []),
        ("9701_w25_21", 2, 11, "Period 3 原子/离子半径趋势、Al 与 P 离子半径差异", []),
        ("9701_w25_22", 2, 20, "Period 3 导电性、Si–Cl 熔点差异、氧化物与氯化物性质", []),
        ("9701_s26_23", 1, 12, "Period 3 chlorides 键型与水解、Cl₂ 净水", [11]),
    ]),
    10: ("Group 2", [
        ("9701_m25_22", 2, 17, "metallic bonding 定义、Group 2 离子半径趋势、Be 逐级 IE", [1, 3]),
        ("9701_m26_22", 1, 14, "Mg–Ba 的 IE 趋势、电子构型、Group 2 物理性质、Cl₂ 歧化与净水", [1, 11]),
    ]),
    11: ("Group 17", [
        ("9701_s24_21", 1, 10, "卤素颜色与挥发性、Br₂ + NaI、浓 H₂SO₄ 与卤化物", []),
        ("9701_w24_21", 2, 13, "卤素颜色与氧化性、HX 热稳定性、C₂H₆ 的 free-radical substitution", [14]),
        ("9701_m25_22", 3, 15, "卤素 bond energy 与 electronegativity 趋势、NaX", []),
        ("9701_s26_21", 3, 10, "NaCl/NaBr/NaI + 浓 H₂SO₄ 的产物与还原性", [12]),
        ("9701_s26_22", 3, 8,  "NaCl/NaBr + 浓 H₂SO₄、Brønsted–Lowry acid–base", []),
    ]),
    12: ("Nitrogen and sulfur", [
        ("9701_m24_22", 3, 15, "N₂ 惰性、NO/NO₂ 生成、PAN 与 photochemical smog", []),
        ("9701_w24_22", 3, 19, "NOₓ 来源、acid rain、PAN、nitric acid 与碱反应", []),
        ("9701_m26_22", 2, 13, "NO dot-and-cross 与 σ/π 键、Cu + 稀 HNO₃", [3]),
    ]),
    13: ("An introduction to AS Level organic chemistry", [
        ("9701_s24_21", 6, 14, "化合物 V 的 stereoisomerism、functional groups、两步反应", []),
        ("9701_s26_22", 6, 13, "P 的 stereoisomer、P→Q 试剂条件、P/R/S 鉴别", [18]),
    ]),
    14: ("Hydrocarbons", [
        ("9701_s25_22", 3, 16, "C₃H₆ + HBr electrophilic addition 机理、Markovnikov、加氢速率", []),
        ("9701_s25_23", 3, 7,  "cracking、photochemical smog、C₄H₈ + H₂、EA 定义", [8]),
        ("9701_s25_23", 6, 10, "HOCl + CH₂=CH₂ electrophilic addition 机理、HOCl 用途", []),
        ("9701_w25_21", 3, 13, "cycloalkanes、C₅H₁₀ 环状异构、Cl₂/UV free-radical substitution", [13]),
        ("9701_w25_22", 3, 14, "homologous series 定义、alkane 惰性、cracking、hexane 异构", [13]),
        ("9701_s26_21", 5, 15, "ethene→PVC 序列、hybridisation、heterolytic fission、机理", [20]),
        ("9701_s26_22", 5, 9,  "hexane + Cl₂/UV 产物命名、free-radical substitution 三阶段", []),
        ("9701_s26_23", 5, 12, "propane + Cl₂/UV 产物命名、free-radical substitution 机理", []),
    ]),
    15: ("Halogen compounds", [
        ("9701_s24_22", 4, 15, "CH₃(CH₂)₅CHBrCH₃ 立体异构、SN1 机理、水解速率", []),
        ("9701_w24_22", 4, 17, "1,2-dibromoethane 反应网络、NaOH(aq) vs NaOH/乙醇、消除", [20]),
        ("9701_m26_22", 3, 14, "2-chlorobutane 分类、C₄H₈ + HCl electrophilic addition", [14]),
    ]),
    16: ("Hydroxy compounds", [
        ("9701_s25_23", 5, 14, "W 的 empirical formula、Na / Br₂ 检验、LiAlH₄ 还原", [17]),
        ("9701_s26_21", 4, 9,  "Z 经酸性 Cr₂O₇²⁻ 氧化为 W、配平氧化方程", [2]),
        ("9701_s26_22", 4, 10, "D→E→F（Cl→OH、Al₂O₃ 脱水）、X 的完全氧化计算", [15]),
        ("9701_s26_23", 4, 14, "V 中伯/仲/叔 hydroxyl 计数、Na / 2,4-DNPH / Fehling's 检验", [17]),
    ]),
    17: ("Carbonyl compounds", [
        ("9701_w24_21", 4, 11, "propanone 的 nucleophilic addition 机理、2,4-DNPH、还原", []),
        ("9701_m25_22", 4, 11, "J–M 的 K₂Cr₂O₇ / 碱性 I₂ / Na 检验、HCN 加成机理", [16]),
        ("9701_s25_21", 6, 7,  "ethanal / propanal / propanone 鉴别、Tollens'、碱性 I₂", []),
    ]),
    18: ("Carboxylic acids and derivatives", [
        ("9701_s25_21", 5, 12, "A 水解为丙二酸 + 乙醇、酯的结构推断、Na₂CO₃ 检验", []),
    ]),
    21: ("Organic synthesis", [
        ("9701_m24_22", 4, 11, "立体异构判定、HBr / KCN / 水解三步合成 S", [13]),
        ("9701_s24_23", 5, 10, "M→R 一步 vs 两步、机理命名、R 的 IR 谱", [22]),
        ("9701_s25_22", 4, 13, "丙酸还原、SOCl₂、腈路线三步合成 T", [18]),
        ("9701_w25_21", 4, 16, "C₂H₅COOH → 丙醇 → 氯代物 → propene，消除反应", []),
        ("9701_w25_22", 4, 16, "propane → 氯代 → 丙醇 → propanoic acid，free-radical 机理", [14]),
    ]),
    22: ("Analytical techniques", [
        ("9701_s24_22", 5, 8, "C₄H₁₀O 质谱 M/M+1 峰与碎片、氧化产物推断", [16]),
    ]),
}

# 只作为「兼」章出现、没有自己主管题目的章（名字照 ../reference.md）
CHAPTERS.setdefault(6, ("Electrochemistry", []))
CHAPTERS.setdefault(19, ("Nitrogen compounds", []))
CHAPTERS.setdefault(20, ("Polymerisation", []))

SLUG = {
    1: "ch01-atomic-structure",
    2: "ch02-stoichiometry",
    3: "ch03-chemical-bonding",
    4: "ch04-states-of-matter",
    5: "ch05-chemical-energetics",
    7: "ch07-equilibria",
    8: "ch08-reaction-kinetics",
    9: "ch09-periodicity",
    10: "ch10-group-2",
    11: "ch11-group-17",
    12: "ch12-nitrogen-and-sulfur",
    13: "ch13-organic-intro",
    14: "ch14-hydrocarbons",
    15: "ch15-halogen-compounds",
    16: "ch16-hydroxy-compounds",
    17: "ch17-carbonyl-compounds",
    18: "ch18-carboxylic-acids",
    21: "ch21-organic-synthesis",
    22: "ch22-analytical-techniques",
    # 下面两章 3 年里没有单独成题，只作为跨章题的「兼」章出现，
    # 但 mirror.py 要给它们建文件夹放镜像，所以 slug 也要有
    6: "ch06-electrochemistry",
    19: "ch19-nitrogen-compounds",
    20: "ch20-polymerisation",
}

if __name__ == "__main__":
    n = sum(len(v[1]) for v in CHAPTERS.values())
    m = sum(q[2] for v in CHAPTERS.values() for q in v[1])
    print(f"{len(CHAPTERS)} 章, {n} 题, {m} 分")
    for c in sorted(CHAPTERS, key=lambda c: -sum(q[2] for q in CHAPTERS[c][1])):
        qs = CHAPTERS[c][1]
        print(f"  ch{c:<3}{SLUG[c]:<32}{len(qs)} 题 {sum(q[2] for q in qs):>4} 分")
