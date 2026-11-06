<!-- md #top -->
# Chapter 13 An introduction to AS Level organic chemistry

Cambridge International AS & A Level Chemistry 9701（2025 / 2026 / 2027）· **Organic chemistry**

{{org-nav}}

- 内容边界与 learning outcome 逐字取自 syllabus；判分句式取自 2024–2026 Paper 2 的 mark scheme，引用写卷号（冲突时以 9701/22 May/June 2026 为准）。
- 🔬 / 🧊 / 📝 开头的 cell 是交互图（已经预先渲染好，打开就能用）。如果显示空白：**Runtime → Run all**。🧊 3D 图需要联网加载 three.js。
- 蓝色链接会跳到别章 notebook 的对应小节：新标签页打开后，**左边目录里高亮的那一项就是目标**，点一下即到（Colab 打开时不一定自动滚过去）。

chapter 13 是整个 organic 部分的「语言课」：后面 14–21 章每一章都在用这里的四样东西。

| 本章小节 | 学什么 | 后面在哪里用 |
|---|---|---|
| 13.1 | formula 的五种写法、functional group、IUPAC 命名 | 每一章的「画出 / 命名 product」 |
| 13.2 | reaction 和 mechanism 的术语（addition、nucleophile、homolytic fission …） | 14–19 章的每个 reaction |
| 13.3 | sp / sp² / sp³ 的 shape、bond angle、σ 与 π | 14.2 alkene、17.1 C=O |
| 13.4 | structural isomerism 与 stereoisomerism | 14.2 Markovnikov、15.1 S<sub>N</sub>1、17.1 racemic mixture |

syllabus 的约定：**X** 表示 halogen atom；**R、R′** 表示 alkyl group（有时也可以是 H），R 和 R′ 可以相同也可以不同。

<!-- md #s13-1 -->
## 13.1 Formulas, functional groups and the naming of organic compounds

### A. hydrocarbon 与 alkane

**hydrocarbon**：只由 C 和 H 两种 atom 组成的 compound。

{{lo 13.1.1}}

alkane（C<sub>n</sub>H<sub>2n+2</sub>）是最简单的 hydrocarbon：只有 C–C 和 C–H single bond，**没有 functional group**，所以几乎什么都不反应（14.1 E 解释原因）。其他 homologous series 都可以看成「alkane 的一个 H 被 functional group 换掉」。

{{lo 13.1.2}}

### B. 五种 formula

以 propene 和 butan-2-ol 为例（讲义）：

| formula | 含义 | propene | butan-2-ol |
|---|---|---|---|
| **empirical formula** | 各种 atom 的最简整数比 | CH₂ | C₄H₁₀O |
| **molecular formula** | 一个 molecule 里各种 atom 的实际数目 | C₃H₆ | C₄H₁₀O |
| **structural formula** | 写出每个 C 上连着什么，不画 bond（C=C、C≡C 要写出来） | CH₂=CHCH₃ | CH₃CH(OH)CH₂CH₃ |
| **displayed formula** | 每一根 bond 都画出来（包括 C–H、O–H） | 见下面 🔬 图鉴 | 见下面 🔬 图鉴 |
| **skeletal formula** | 去掉 C、H 的符号和 C–H bond；每个折点 / 端点是一个 C；其他 atom（O、N、X）和连在它们上面的 H 要写出来 | 见 🔬 | 见 🔬 |

- **general formula**：一个 homologous series 共用的式子，如 alkane C<sub>n</sub>H<sub>2n+2</sub>、alkene C<sub>n</sub>H<sub>2n</sub>、alcohol C<sub>n</sub>H<sub>2n+1</sub>OH。
- skeletal formula 的「zig-zag」是真实的形状：sp³ 的 C 键角 109.5°，链本来就是折线。3D displayed formula 里 **wedge**（实心楔形）表示朝向读者、伸出纸面，**dashed line**（虚楔形）表示伸到纸面后面。
- 考卷写 structural formula 时，**C=C 必须写出来**（CH₂=CHCH₃，不能写 CH₂CHCH₃）；–OH、–CHO、–COOH 照常缩写。
- 「draw the structure」：任何无歧义的写法都给分，但只写 molecular formula（如 C₄H₈）不给分（9701/22 May/June 2026 Q4(a)(iii)）。

{{lo 13.1.4}}

### C. functional group 与 homologous series

- **functional group**：molecule 里决定其特征 chemical reaction 的 atom 或 atom 组。
- **homologous series**：一组 organic compounds，**同一个 functional group、同一个 general formula、相似的 chemical properties**；相邻两员差一个 CH₂，physical properties（如 boiling point）随链长逐渐变化。

{{lo 13.1.3}}

syllabus 表里的 9 个 homologous series，以及每个在哪一章详讲（链接跳到那一章）：

| homologous series | functional group | general / structural formula | 例子 | 详讲 |
|---|---|---|---|---|
| alkene | C=C bond | C<sub>n</sub>H<sub>2n</sub> | propene CH₂=CHCH₃ | {{xref ch14#alkenes ch14 →}} |
| halogenoalkane（primary, secondary and tertiary） | halogen | R–X | 1-chloropropane CH₃CH₂CH₂Cl | {{xref ch15#halogenoalkanes ch15 →}} |
| alcohol（primary, secondary and tertiary） | hydroxyl | R–OH | propan-1-ol CH₃CH₂CH₂OH | {{xref ch16#alcohols ch16 →}} |
| aldehyde | carbonyl | R–CHO | propanal CH₃CH₂CHO | {{xref ch17#carbonyls ch17 →}} |
| ketone | carbonyl | R–CO–R′ | propanone CH₃COCH₃ | {{xref ch17#carbonyls ch17 →}} |
| carboxylic acid | carboxyl | R–COOH | propanoic acid CH₃CH₂COOH | {{xref ch18#acids ch18 →}} |
| ester | ester | R–COO–R′ | methyl propanoate CH₃CH₂COOCH₃ | {{xref ch18#esters ch18 →}} |
| amine（primary only） | amine | R–NH₂ | propylamine CH₃CH₂CH₂NH₂ | {{xref ch19#amines ch19 →}} |
| nitrile | nitrile | R–C≡N | propanenitrile CH₃CH₂CN | {{xref ch19#nitriles ch19 →}} |

注意 aldehyde 和 ketone 是**同一个** functional group（carbonyl，C=O）：C=O 在链端（连一个 H）是 aldehyde，在链中间（两边都是 C）是 ketone。

<!-- html: functional group 图鉴：四种 formula #fg-gallery -->
{{cell fg-gallery}}

<!-- md #naming-rules -->
### D. IUPAC 命名

{{lo 13.1.5}}

**stem（碳数）**：meth- 1、eth- 2、prop- 3、but- 4、pent- 5、hex- 6。alkyl side-chain 把 -ane 换成 **-yl**（methyl、ethyl）；同一种 side-chain 有几个就加 **di- / tri- / tetra-**。

**suffix / prefix（functional group）**：

| series | 写法 | 例 |
|---|---|---|
| alkane / alkene | -ane / -ene（C=C 的位置写在 -ene 前） | but-2-ene CH₃CH=CHCH₃ |
| halogenoalkane | prefix：fluoro- chloro- bromo- iodo- | 2-chloropropane CH₃CHClCH₃ |
| alcohol | -ol（位置写在 -ol 前；两个 OH 写 -diol） | butan-2-ol、ethane-1,2-diol |
| aldehyde | -al（一定在 C1，不写数字） | butanal CH₃CH₂CH₂CHO |
| ketone | -one（位置写在 -one 前） | butan-2-one CH₃COCH₂CH₃ |
| carboxylic acid | -oic acid（一定在 C1，不写数字） | butanoic acid CH₃CH₂CH₂COOH |
| ester | 「alcohol 那一半的 alkyl」+「acid 那一半的 -oate」 | ethyl propanoate CH₃CH₂COOCH₂CH₃ |
| amine | -amine | butylamine CH₃CH₂CH₂CH₂NH₂ |
| nitrile | -nitrile（**C≡N 的 C 算进主链**） | butanenitrile CH₃CH₂CH₂CN（4 个 C） |

**四步法**（讲义）：

1. 找出最重要的 functional group；
2. 找出含这个 functional group 的**最长碳链**，其余是 side-chain（substituent）；
3. 给主链编号：让 **principal functional group 的 locant 最小**；没有 functional group 时，让 side-chain 的 locant（第一个不同点）最小；
4. 写名字：substituent 按**字母顺序**（不看 di- / tri-），数字与字母之间用 hyphen「-」，数字与数字之间用 comma「,」。

例：3-ethyl-2-methylpentane（ethyl 的 e 排在 methyl 的 m 前面）；2,2,3-trimethylpentane；2-bromo-3,3-dichlorohexane。

**说「第几个碳」时一律用 IUPAC 编号**：propene（prop-1-ene）里 C1 是端点的 =CH₂，C2 是 =CH–，C3 是 CH₃——不按画图时从左到右数。后面所有章节（Markovnikov 的「H 加到 C1」、ester 的「alcohol 那一半」）都按这个口径。

syllabus 的范围：最多 6 个 C（ester 是 6 + 6）；**ester 和 nitrile 只考直链**。

<!-- html: IUPAC 命名练习 #naming -->
{{cell naming}}

<!-- md #formula-deduce -->
### E. 从结构式推 molecular / empirical formula

数 skeletal formula 最容易错的是 H：**每个 C 一共 4 根 bond**，图上没画满的都是 C–H。

1. 数 C：每个折点、端点各一个（C≡N 的 C、C=O 的 C 也要算）；
2. 数 H：每个 C 上 H = 4 − 已画出的 bond 数（double bond 算 2）；再加上 OH、NH₂、CHO 里写出来的 H；
3. 数 O、N、X；
4. 求 empirical formula：各数除以最大公约数（C₄H₈ → CH₂；C₂H₄O₂ → CH₂O）。

检查方法：链状、没有 ring、没有 π bond 的 compound 符合 C<sub>n</sub>H<sub>2n+2</sub>（halogen 当 H 数，O 不影响）；每多一个 ring 或一根 π bond，H 少 2 个。

{{lo 13.1.6}}

<!-- html: skeletal → molecular formula 计数器 #formula-count -->
{{cell formula-count}}

<!-- md #s13-2 -->
## 13.2 Characteristic organic reactions

### A. 描述 compound 和 reaction 的术语

{{lo 13.2.1}}

| 术语 | 意思 | 第一次真正用到 |
|---|---|---|
| (a) **homologous series** | 见 13.1 C | — |
| (b) **saturated** / **unsaturated** | 只有 single bond / 含 C=C 或 C≡C（π bond） | alkane vs alkene，{{xref ch14#alkenes 14.2}} |
| (c) **homolytic fission** | covalent bond 断开时两个 atom **各拿一个** electron → 两个 free radical | {{xref ch14#rx-frs free-radical substitution}} |
| (c) **heterolytic fission** | 较 electronegative 的 atom **拿走两个** electron → 一对 ions（例如 carbocation + X⁻） | {{xref ch15#rx-nucsub S<sub>N</sub>1}} |
| (d) **free radical** | 带 unpaired electron 的 species（Cl•、CH₃•），很活泼 | {{xref ch14#rx-frs 14.1 C}} |
| (d) **initiation / propagation / termination** | 产生 radical / radical 进攻 molecule 又生出新 radical（chain reaction）/ 两个 radical 结合，radical 消失 | {{xref ch14#rx-frs 14.1 C}} |
| (e) **nucleophile** | electron pair donor（有 lone pair 或负电荷）：OH⁻、CN⁻、NH₃、H₂O | {{xref ch15#rx-nucsub 15.1}}、{{xref ch17#rx-hcn 17.1}} |
| (e) **electrophile** | electron pair acceptor（缺 electron）：H⁺、Br₂ 里 δ+ 的那端、carbocation | {{xref ch14#rx-alkene-add 14.2}} |
| (f) **addition** | 两个（或多个）molecule 合成**一个** product | alkene 的所有 addition |
| (f) **substitution** | 一个 atom / group 被另一个替换 | halogenoalkane |
| (f) **elimination** | 从一个大 molecule 上**去掉一个小 molecule**（HX、H₂O） | {{xref ch15#rx-elimination 15.1 D}}、{{xref ch16#rx-dehydration 16.1 F}} |
| (f) **hydrolysis** | 与 water 反应使 molecule 断开（常用 acid 或 alkali 催化） | ester、nitrile、halogenoalkane |
| (f) **condensation** | 两个 molecule 结合、同时**放出一个小 molecule**（通常 H₂O） | {{xref ch18#rx-esterification esterification}} |
| (g) **oxidation / reduction** | 加 O 或去 H / 去 O 或加 H | {{xref ch16#rx-oxidation 16.1 E}}、{{xref ch17#rx-reduction 17.1 B}} |

**[O] 与 [H]**：organic redox equation 里用 [O] 表示氧化剂提供的一个 O atom，[H] 表示还原剂提供的一个 H atom，例如

- CH₃CH₂OH + [O] → CH₃CHO + H₂O（partial oxidation，distillation）
- CH₃CH₂OH + 2[O] → CH₃COOH + H₂O（reflux）
- CH₃COCH₃ + 2[H] → CH₃CH(OH)CH₃

配平时数 O 和 H：等号两边的 H、O 要相等，[O] / [H] 的系数就是这样定出来的。

### B. 四种 mechanism 与 curly arrow

{{lo 13.2.2}}

| mechanism | 进攻的 species | 被进攻的 | 例子（syllabus 指定） | 详讲 |
|---|---|---|---|---|
| (a) free-radical substitution | Cl• / Br• | alkane 的 C–H | ethane + Cl₂, UV | {{xref ch14#rx-frs ch14 →}} |
| (b) electrophilic addition | electrophile（Br₂ 的 δ+ 端、HBr 的 H） | C=C 的 π electrons | Br₂ / ethene、HBr / propene | {{xref ch14#rx-alkene-add ch14 →}} |
| (c) nucleophilic substitution | nucleophile（OH⁻、CN⁻、NH₃） | C–X 里 δ+ 的 C | S<sub>N</sub>1 / S<sub>N</sub>2 | {{xref ch15#rx-nucsub ch15 →}} |
| (d) nucleophilic addition | nucleophile（CN⁻） | C=O 里 δ+ 的 C | HCN + ethanal / propanone | {{xref ch17#rx-hcn ch17 →}} |

curly arrow 的规矩（mark scheme 每次都查）：

- 一支 curly arrow = **一对 electrons** 的移动；
- 箭尾必须从 **bond**（从 bond 的中间出发）或 **lone pair**（从那两个点出发）开始；
- 箭头指向 electrons 要去的 **atom**（形成新 bond）或 **atom 之间**（新 bond 的位置）；
- free radical 的单个 electron 移动**不要求**画箭头（syllabus 原注）。

<!-- html: homolytic vs heterolytic fission、reagent 分类 #fission -->
{{cell fission}}

<!-- md #s13-3 -->
## 13.3 Shapes of organic molecules; σ and π bonds

### A. straight-chained、branched、cyclic

{{lo 13.3.1}}

- **straight-chained**：所有 C 连成一条不分叉的链（skeletal formula 是一条折线），例如 pentane；
- **branched**：主链上有 side-chain，例如 2-methylbutane；
- **cyclic**：C 首尾相连成 ring，例如 cyclohexane C₆H₁₂（与 hex-1-ene 是 structural isomer）。

三者可以是同一个 molecular formula 的不同 isomer（13.4 A 的 chain isomerism）。

### B. sp³ / sp² / sp 的 shape 与 bond angle

hybridisation 的来历在 {{xref ch03#hybrid chapter 3 的 sp / sp² / sp³ 3D 图}}；σ 与 π overlap 在 {{xref ch03#sigma-pi chapter 3 的 σ / π 3D 图}}。这里只用结论：

| C 周围 | hybridisation | shape | bond angle | σ / π | 例子 |
|---|---|---|---|---|---|
| 4 个 σ bond（全是 single bond） | sp³ | tetrahedral | 109.5° | 4 σ | ethane 的两个 C、propene 的 C3 |
| 3 个 σ + 1 个 π（一根 double bond） | sp² | trigonal planar | 120° | 3 σ + 1 π | ethene 的两个 C、C=O 的 C |
| 2 个 σ + 2 个 π（一根 triple bond，或两根 double bond） | sp | linear | 180° | 2 σ + 2 π | ethyne HC≡CH、C≡N 的 C |

- 讲理由时用 VSEPR 口径：「C 周围有 n 对 bonding electrons（π 不另算一个方向），彼此 repel、尽量远离」。
- 一个 molecule 里不同的 C 可以是不同的 hybridisation：propene 的 C1、C2 是 sp²（120°），C3 是 sp³（109.5°）。

{{lo 13.3.2}}

### C. σ 与 π 的排列

- **σ bond**：orbital **end-on**（head-on）overlap，electron density 在两个 nuclei 的连线上；每一根 bond（single、double、triple）里都**有且只有一根** σ。
- **π bond**：相邻 C 上**未参与 hybridisation 的 p orbitals** **sideways** overlap，electron density 在两个 nuclei 连线的**上方和下方**两瓣。
- double bond = 1 σ + 1 π；triple bond = 1 σ + 2 π（两根 π 互相垂直，合起来像包着 C≡C 的圆筒）。
- π overlap 要求两个 p orbital 平行 → 绕 C=C 转动会拉断 π bond → **restricted rotation**（13.4 B 的 cis/trans 就从这里来）。

数 σ / π：数每一根 bond，single 记 1σ，double 记 1σ+1π，triple 记 1σ+2π。例如 propene CH₂=CHCH₃：8 σ + 1 π。

{{lo 13.3.3}}

### D. planar

**planar**：molecule 里（某一部分的）所有 atom 在同一个平面上。

- ethene：两个 sp² C 和四个 H **全部共面**，π 的两瓣在这个平面的上下方；
- 判断方法：C=C 的两个 C 以及**直接连在它们上面的四个 atom** 一定共面（六原子共面）；但 sp³ 的 CH₃ 上的 H 伸出平面，所以 propene 整体**不是** planar；
- ethyne 是 linear（四个 atom 一条直线）。

{{lo 13.3.4}}

<!-- html3d: organic molecule 的 shape、hybridisation 与 σ / π #shapes3d -->
{{cell shapes3d}}

<!-- md #s13-4 -->
## 13.4 Isomerism: structural isomerism and stereoisomerism

**isomers**：molecular formula 相同、但 atom 的排列不同的 compounds。

### A. structural isomerism

**structural isomers**：molecular formula 相同，**structural formula 不同**（atom 连接的次序不同）。

{{lo 13.4.1}}

| 类型 | 哪里不同 | 例子 |
|---|---|---|
| **chain** isomerism | 碳骨架（直链 / 支链） | butane 与 2-methylpropane（C₄H₁₀） |
| **positional** isomerism | functional group 在同一骨架上的**位置** | propan-1-ol 与 propan-2-ol；1-chloropropane 与 2-chloropropane |
| **functional group** isomerism | functional group 本身不同 | propanal 与 propanone（C₃H₆O）；propanoic acid 与 methyl ethanoate（C₃H₆O₂）；propene 与 cyclopropane（C₃H₆） |

常见的 functional group isomer 配对（molecular formula 相同）：aldehyde ↔ ketone、carboxylic acid ↔ ester、alkene ↔ cycloalkane、alcohol ↔ ether（ether 不在 syllabus 表里，但出现在 isomer 题里）。

画 isomer 时最常见的错：**把同一个结构画两次**。C–C single bond 可以自由转动，链怎么弯都是同一个 compound；从链的另一端编号得到的也是同一个（1-chloropropane 不存在「3-chloropropane」）。

### B. stereoisomerism

**stereoisomers**：atom 的连接方式完全相同，只是 atom 在**空间里的排列**不同。分两类：geometrical（cis/trans）isomerism 和 optical isomerism。

{{lo 13.4.2}}

**geometrical（cis/trans）isomerism** 的来源：C=C 里的 π bond 要求两个 p orbital 平行，绕 C=C 转动会破坏 π overlap，所以**不能自由转动（restricted rotation）**。两边的 group 于是被固定在同侧（**cis**）或异侧（**trans**）。

- 条件：C=C 的**每一个** C 上都连着**两个不同的** group。(CH₃)₂C=CHCH₃ 没有 cis/trans（左边的 C 连着两个相同的 CH₃）；but-1-ene 也没有（C1 上是两个 H）；but-2-ene 有。
- ring 也会限制转动：1,2-dimethylcyclohexane、cyclobutane-1,3-dicarboxylic acid 都有 cis / trans。
- cis / trans isomers 是不同的 compounds，physical properties 不同（mp、bp），chemical reaction 的速率也可能不同。
- E/Z 命名可以用但不要求。

mark scheme 的说法（解释 cis/trans 的来源）：**restricted rotation about the C=C / π bond** AND **each C of the C=C has two different groups attached**。

{{lo 13.4.3}}

<!-- html3d: 为什么 C=C 不能转：cis / trans but-2-ene #cis-trans3d -->
{{cell cis-trans3d}}

<!-- md #optical -->
### C. optical isomerism 与 chiral centre

- **chiral centre**：连着**四个不同 atom 或 group** 的 C atom（skeletal formula 里常用 * 标出）。
- 有一个 chiral centre 的 molecule 有两个 **optical isomers（enantiomers）**：互为**镜像**，而且**不能重合（non-superimposable）**。
- 一对 enantiomers 的 physical / chemical properties 几乎完全一样；区别是对 **plane-polarised light** 的作用：转动的角度相等、**方向相反**（一个顺时针，一个逆时针）。
- 一个 molecule 可以有不止一个 chiral centre（syllabus 原注：不考 meso compound、diastereoisomer 这类名称）。两个不同的 chiral centre → 最多 4 个 optical isomers。

画 enantiomers 的得分点：两个 3D 结构（用 wedge / dashed line，四个 group 呈 tetrahedral）**互为镜像**，中间画一条镜面线；四个 group 都要写对。

{{lo 13.4.4}}

<!-- html3d: 镜像能重合吗：一对 enantiomers #chiral3d -->
{{cell chiral3d}}

<!-- md #find-isomerism -->
### D. 在给定结构里找 chiral centre 与 cis/trans

找 chiral centre：逐个看 **sp³ 的 C**（sp² / sp 的 C 只连三个或两个 group，不可能是 chiral centre）：

1. 连着两个以上 H 的 C（CH₃、CH₂）直接排除；
2. 剩下的 C，把四个方向上的 group **整条看到底**：–CH₂CH₃ 和 –CH₃ 不同；ring 上的 C 要沿 ring **顺时针和逆时针各走一圈**比较，两边一样就不是 chiral centre（对称取代的 ring 没有 chiral centre）；
3. 标 * 号。

找 cis/trans：逐根 C=C（包括 ring 上的取代位置）检查「每个 C 上两个 group 不同」。

数 stereoisomer：n 个 chiral centre（彼此不同）+ m 根能 cis/trans 的 C=C → 最多 2<sup>n+m</sup> 个 stereoisomers。

{{lo 13.4.5}}

<!-- html: 找出 chiral centre 与 cis/trans 的 C=C #find-centres -->
{{cell find-centres}}

<!-- md #deduce-isomers -->
### E. 由 molecular formula 推出所有 isomer

系统地写，才不会漏也不会重：

1. 由 molecular formula 判断可能的 functional group：算「缺几对 H」——C<sub>n</sub>H<sub>2n+2</sub> 是饱和；少 2 个 H = 一根 C=C 或 C=O 或一个 ring；有 O 时想 alcohol / ether（1 个 O、饱和）、aldehyde / ketone（1 个 O、少 2 H）、acid / ester（2 个 O、少 2 H）；
2. 每个 functional group 下，先写最长的直链，再逐步缩短主链、挪 side-chain（chain isomers）；
3. 每个骨架上挪 functional group 的位置（positional isomers），利用对称性去重；
4. 最后逐个检查 stereoisomerism：有没有 chiral centre、有没有能 cis/trans 的 C=C——**题目要「all isomers」时，cis / trans 和 enantiomers 都要算进去**。

例：C₄H₈ 有 alkene 三种骨架（but-1-ene、but-2-ene、2-methylpropene），but-2-ene 再分 cis / trans；加上 cyclobutane、methylcyclopropane 两个 cyclic isomer，共 6 个。

{{lo 13.4.6}}

<!-- html: isomer 枚举器 #isomer-explorer -->
{{cell isomer-explorer}}

<!-- md #practice -->
## Practice

2024–2026 Paper 2 里所有考 chapter 13 的小问，按考试时间排列（含正本在其他章、但这一小问考本章的）。题干只保留到看得懂为止；展开 **答案** 对照 mark scheme。

<!-- practice: 9701/22 Feb/Mar 2024 -->
### 9701/22 Feb/Mar 2024

#### Q4(a) [2]

P, Q, R and S show stereoisomerism. Complete Table 4.1 by identifying with a tick (✓) the type
of stereoisomerism that each molecule shows. The type of stereoisomerism shown by Q is given.

**Table 4.1**

| | P | Q | R | S |
|---|---|---|---|---|
| geometrical isomerism | ✓ | | | |
| optical isomerism | | ✓（已给） | ✓ | ✓ |

::: answer
**答案** — P 只显示 geometrical isomerism；Q（已给）、R、S 都只显示 optical isomerism
**判分** — geometrical 一行（P✓其余×）与 optical 一行（Q✓给定、R✓、S✓）分别各占 1 分

:::

#### Q4(b)(ii) [1]

Name the mechanism in reaction 2.

::: answer
**答案** — nucleophilic substitution

:::

<!-- practice: 9701/22 May/June 2024 -->
### 9701/22 May/June 2024

Y is a structural isomer of W. Both W and Y produce colourless bubbles when sodium is added to them. Y does not react when heated with acidified K₂Cr₂O₇. Y does not react when warmed with alkaline I₂(aq).

#### Q5(c)(iii) [1]

Draw the structure of Y.

::: answer
**答案** — Y = (CH₃)₃COH（2-methylpropan-2-ol，tert-butanol）

:::

<!-- practice: 9701/23 May/June 2024 -->
### 9701/23 May/June 2024

#### Q5(b)(ii) [1]

Name the mechanism for step 1 in Figure 5.2.

::: answer
**答案** — electrophilic addition

:::

<!-- practice: 9701/21 Oct/Nov 2024 -->
### 9701/21 Oct/Nov 2024

Hydrated rhodium(III) chloride, RhCl₃·xH₂O, catalyses the conversion of ethene to but-2-ene. Both stereoisomers of but-2-ene are formed in the reaction.

#### Q1(d)(ii) [1]

Define stereoisomers.

::: answer
**答案** — molecules with the same structural formula and same molecular formula with different
3D / different spatial arrangement of atoms / groups

:::

#### Q1(d)(iii) [1]

Explain how the conversion of ethene to but-2-ene can be described as an addition reaction.

::: answer
**答案** — a single product is made

:::

#### Q1(d)(iv) [2]

Draw the two stereoisomers of but-2-ene.

::: answer
**答案** — 两个骨架式：**E-but-2-ene**（trans，锯齿形骨架，双键两端的 CH₃ 分居 C=C 异侧）与
**Z-but-2-ene**（cis，双键处骨架拐折，两个 CH₃ 同侧）。

:::

The halogenoalkane CH₃CH₂Cl forms when chlorine reacts with C₂H₆ via a free-radical substitution mechanism.

#### Q2(b)(i) [1]

Define free radical.

::: answer
**答案** — a species with one or more unpaired electrons

:::

<!-- practice: 9701/22 Oct/Nov 2024 -->
### 9701/22 Oct/Nov 2024

Compound E is the only isomer of 1,2-dibromoethane. Alkaline hydrolysis of E gives compound F.
- **E** = CH₃CHBr₂（1,1-dibromoethane）
- **F** = CH₃CHO（ethanal）——E 的两个 Br 同时被 OH 取代生成 gem-diol CH₃CH(OH)₂，不稳定，
  自发脱水成 aldehyde F

#### Q4(d)(i) [1]

Identify the type of isomerism shown by E and 1,2-dibromoethane.

::: answer
**答案** — structural / positional

:::

#### Q4(d)(ii) [1]

Name the homologous series that F belongs to.

::: answer
**答案** — aldehyde

:::

<!-- practice: 9701/22 Feb/Mar 2025 -->
### 9701/22 Feb/Mar 2025

Fig. 1.1 shows a reaction scheme involving P₄ and Cl₂.
![Fig. 1.1](passyear/extracted/ch09-periodicity/img/9701_m25_22_fig1-1.png)

#### Q1(b)(v) [1]

Draw the structure of **C**, used in reaction 6.

::: answer
**答案**（答案是图，见 MS 渲染页 `_img/9701_m25_22_msp05.png`）

**C** 是 ethane-1,2-diol，结构为 HO-CH₂-CH₂-OH（骨架式：左端 HO 接一个之字形双碳链，
右端接 OH）。反应 6 是 PCl₅ 把二醇的两个 –OH 都取代成 –Cl，生成 Fig. 1.1 中标出的
ClCH₂CH₂Cl。

:::

1,2-dichloroethane, ClCH₂CH₂Cl, reacts with NaOH to produce an unsaturated compound, C₂H₃Cl, as shown in reaction 7.
reaction 7　ClCH₂CH₂Cl + NaOH → C₂H₃Cl + H₂O + NaCl

#### Q1(c)(i) [1]

State what is meant by unsaturated.

::: answer
**答案** — contains a (one or more) C=C / double / multiple bond(s)

:::

K reacts with HCN in the presence of a KCN catalyst, forming N.

#### Q4(b)(iii) [1]

N has a chiral centre. Explain what is meant by a chiral centre.

::: answer
**答案** — atom / carbon with four different atoms / (functional) groups attached / bonded

:::

<!-- practice: 9701/22 May/June 2025 -->
### 9701/22 May/June 2025

#### Q4(b)(i) [1]

Propan-1-ol is converted to compound T in a three-step synthesis. In step 1, SOCl₂ is added to
propan-1-ol to produce compound E. Name the type of reaction that occurs in step 1.

::: answer
**答案** — substitution

:::

#### Q4(b)(iv) [1]

Name the type of reaction that occurs in step 3.

::: answer
**答案** — (alkaline) hydrolysis

:::

#### Q4(c)(i) [1]

Compounds A, B and C belong to the alcohol homologous series. Each molecule of A, B and C
contains four saturated carbon atoms. Identify the type of hybridisation shown in the saturated
carbon atoms of all alcohols.

::: answer
**答案** — sp³

:::

<!-- practice: 9701/21 Oct/Nov 2025 -->
### 9701/21 Oct/Nov 2025

#### Q3(b) [2]

Cyclopentane, C₅H₁₀, has four cyclic structural isomers. One of these isomers is C, shown in
Fig. 3.1. Complete Fig. 3.1 to show two other cyclic structural isomers of C₅H₁₀.

![Fig. 3.1](passyear/extracted/ch05-chemical-energetics/img/9701_w25_21_fig3-1.png)

::: answer
**答案** — Fig. 3.1 中已给出的 C 是 1,2-dimethylcyclopropane（cyclopropane 相邻两个碳各接一个 methyl）。C₅H₁₀ 除 cyclopentane 本身外共有四种环状异构体，本题只需再画出以下三种中的
任意两种：
- methylcyclobutane（cyclobutane 上一个碳接一个 methyl）
- 1,1-dimethylcyclopropane（cyclopropane 同一个碳上接两个 methyl）
- ethylcyclopropane（cyclopropane 上一个碳接一个 ethyl）

**判分** — two of the above structures

:::

<!-- practice: 9701/22 Oct/Nov 2025 -->
### 9701/22 Oct/Nov 2025

#### Q3(a) [2]

Define homologous series.

::: answer
**答案**
- M1 (family of molecules / compounds / series with) same general formula
  OR (family of molecules where) molecular formula differs (only) by (units of) CH₂(n)
- M2 similar chemical properties / reactions

:::

Hexane, C₆H₁₄, has four structural isomers. Fig. 3.1 shows hexane and two of its structural
isomers.
![Fig. 3.1](passyear/extracted/ch03-chemical-bonding/img/9701_w25_22_fig3-1.png)

#### Q3(d)(i) [2]

Complete Fig. 3.1 by drawing structures for C and D, the other two structural isomers of hexane.

::: answer
**答案** — Fig. 3.1 中已给出 hexane（直链）、A（2-methylpentane，支链在离端点第 2 个碳）、
B（2,3-dimethylbutane，两个 methyl 分别在相邻的第 2、3 个碳上）。还需再画出：
- C = 3-methylpentane：CH₃CH₂CH(CH₃)CH₂CH₃（methyl 支链在链正中间的第 3 个碳）
- D = 2,2-dimethylbutane：CH₃CH₂C(CH₃)₂CH₃（两个 methyl 都接在同一个碳，即第 2 个碳，
  上，形成 quaternary carbon）

:::

#### Q4(a)(i) [1]

Reaction 1 in Figure 4.1 takes place in the presence of sunlight.

C₃H₈ + Cl₂ → CH₃CH₂CH₂Cl + HCl

The reaction takes place via initiation, propagation and termination steps. Name the mechanism
shown by reaction 1.

::: answer
**答案** — free-radical substitution

:::

#### Q4(a)(iii) [1]

Reaction 1 is initiated by the bond fission of Cl₂. State the type of bond fission shown in the
initiation step.

::: answer
**答案** — homolytic

:::

#### Q4(a)(iv) [1]

Compound Q is a by-product of reaction 1：CH₃–CHCl–CH₂Cl。Name Q.

::: answer
**答案** — 1,2-dichloropropane

:::

#### Q4(a)(v) [2]

The molecular formula of Q is C₃H₆Cl₂. Identify the types of structural isomerism and
stereoisomerism that a molecule with molecular formula C₃H₆Cl₂ can show.

::: answer
**答案**
- type of structural isomerism — positional
- type of stereoisomerism — optical

:::

#### Q4(d)(i) [1]

CH₃CH₂COOH reacts with an unsaturated alcohol R to form unsaturated ester S. State the type of
reaction that forms S.

::: answer
**答案** — condensation

:::

<!-- practice: 9701/22 Feb/Mar 2026 -->
### 9701/22 Feb/Mar 2026

2-chlorobutane can be formed by the electrophilic addition of HCl to different isomers of C₄H₈. Compound A is one of these isomers.
![Figure 3.2](passyear/extracted/ch13-organic-intro/img/9701_m26_22_fig3-2.png)
（A 是 *cis*-but-2-ene / (Z)-but-2-ene——从 QP 图上双键两侧的顺式画法可确认）

#### Q3(b)(ii) [2]

Draw and give the systematic name of the geometrical isomer of A.

::: answer
**答案**

- M1 画出 *trans* 构型的 but-2-ene 结构（两个 CH₃ 在 C=C 两侧呈反式排列）
- M2 systematic name：*trans*-but-2-ene

:::

#### Q3(b)(iii) [2]

State and explain the origin of geometrical isomerism in alkenes.

::: answer
**答案**

- M1 (two) different groups attached to **each** carbon of C=C
- M2 restricted / lack of / no rotation about double / C=C / pi / π bond

:::

#### Q4(d)(ii) [1]

Name HCHO, the reactant used in step 2.

::: answer
**答案** — methanal

:::

#### Q4(d)(iii) [1]

Deduce the molecular formula of E.

::: answer
**答案** — C₆H₇NO₂

:::

<!-- practice: 9701/21 May/June 2026 -->
### 9701/21 May/June 2026

#### Q5(a) [2]

Complete Table 5.1.

Table 5.1

| compound | type of hybridisation of carbon atoms |
|---|---|
| 1,2-dichloroethane | sp³ |
| chloroethene | sp² |

::: answer
**判分** — M1 sp³ 的各种写法（sp3、SP³ 等）都给分；M2 sp² 同理

:::

#### Q5(c) [2]

Describe what is meant by heterolytic fission of a covalent bond.

::: answer
**答案**
- M1 when a (covalent) bond / it is broken
- M2 one atom takes both of the electrons from the shared pair

**判分** — M2 必须明确是在描述"某个共价键断裂"这一过程中，才能因"一个原子拿走两个电子"
得分；**R** 用 element / molecule / compound 代替 species；**I** radical、uneven number of
electrons、formation of (positive and negative) ions、formation of nucleophile and electrophile
这类表述

:::

#### Q5(e) [1]

When 1,2-dichloroethane is heated in reaction 2, thermal decomposition occurs. The reaction is
endothermic. State the type of reaction that occurs.

::: answer
**答案** — elimination

:::

<!-- practice: 9701/22 May/June 2026 -->
### 9701/22 May/June 2026

Figure 6.1 shows the structure of compound P.
![Figure 6.1](passyear/extracted/ch13-organic-intro/img/9701_s26_22_fig6-1.png)

#### Q6(a)(i) [1]

Draw the structure of the stereoisomer of P.

::: answer
**答案** — P（Fig. 6.1）为 trans (E) but-2-enedioic acid；答案画出其 cis (Z) 立体异构体，即两个
COOH 在 C=C 同侧。

**判分** — A 任何明确无歧义的 cis / Z 结构；I connectivity 画错；I 画成 trans 结构

:::

#### Q6(a)(ii) [2]

Explain why P shows stereoisomerism.

::: answer
**答案**
- M1 limited / restricted / lack of / no rotation about the pi bond / π bond of C=C
- M2 (two) different groups attached to each C of the C=C / each end of the C=C

**判分**
- M1：A limited / restricted / lack of / no rotation about the C=C；C=C 全篇只需点名一次；
  BOD C−C double bond；**I** double bond（分子里另有一个 C=O，笼统说 double bond 不给）；
  **I** movement；rotate = twist = spin；**R** "(compound) P has a chiral carbon"
- M2：each = both；A different atoms / functional groups / H and COOH / species；
  **I** each side (of the C=C)；**R** different compounds / molecules

:::

P reacts to produce compound Q.
![Figure 6.2](passyear/extracted/ch13-organic-intro/img/9701_s26_22_fig6-2.png)

#### Q6(b)(ii) [2]

Complete Figure 6.3 to show the pair of stereoisomers of Q.

![Figure 6.3](passyear/extracted/ch13-organic-intro/img/9701_s26_22_fig6-3.png)

::: answer
**答案** — Q 是 P 加水后的产物（malic acid，2-hydroxybutanedioic acid），手性碳上接
COOH（竖直向上）、H（竖直向下）、OH 与 CH₂COOH（一前一后，用楔形/虚楔表示）：
- isomer 1：COOH 竖直向上，H 竖直向下；OH 用粗楔形键（指向读者）画在左下方，
  CH₂COOH 用虚楔形键（指向纸面后方）画在右下方
- isomer 2（isomer 1 的 enantiomer）：COOH 竖直向上，H 竖直向下；CH₂COOH 用虚楔形键
  画在左下方，OH 用粗楔形键画在右下方——即把 OH 和 CH₂COOH 的前后位置互换

**判分**
- COOH = CO₂H；A C₂H₃O₂
- M1 中心碳周围 4 个基团（COOH / H / OH / CH₂COOH）全部正确，方向不拘（写在 isomer 2 上也算）
- M2 是 M1 结构的 enantiomer（不要求画成严格镜像）；**R** 平面内的键画成互相相对方向；
  **I** 与手性碳无关的键形状；**I** 键角；**I** connectivity

:::

<!-- practice: 9701/23 May/June 2026 -->
### 9701/23 May/June 2026

Compounds W, X and Y are structural isomers of V.
![Figure 4.2](passyear/extracted/ch13-organic-intro/img/9701_s26_23_fig4-2.png)
> 读图提示：骨架式的每个拐点都是一个碳。Figure 4.2 的四个结构**全是 C₅H₁₂O₄**——V = CH₃–C(OH)(CH₂OH)–CH(OH)–CH₂OH；W = HOCH₂–CH(OH)–CH(OH)–CH₂–CH₂OH（左侧竖线下端到 CH₂OH 之间那个折点是 CH₂）；X = HOCH₂CH₂–C(OH)(CH₂OH)₂；Y = C(CH₂OH)₄（pentaerythritol）。W 的 C2、C3 各连 4 个不同基团，所以 (c)(ii) 说「both have 2 chiral centres」成立。

#### Q4(c)(i) [2]

Describe structural isomerism.

::: answer
**答案**

- M1 — (molecules / isomers with) the same molecular formula / same number of atoms of each element
- M2 — different arrangement of atoms

**判分** — M1 A same molecular formula；I same chemical formulas；I same/similar molecular number。M2 A different structures／different structural formulas／different displayed formulas／different skeletal formulas；I arrangement of bonds／不同空间排布；I 只提 carbon skeleton／functional groups／chain 不同

:::

#### Q4(c)(ii) [2]

Identify which of structures V, W, X and Y show stereoisomerism. Explain your answer by referring to the relevant parts of the molecule that cause stereoisomerism.

::: answer
**答案**

- M1 — compound W **AND** compound V
- M2 — both have (2) chiral centres / (2) asymmetric carbon atoms

**判分** — chiral = 4 个不同的 group/atom 连在同一个碳上；R 说成"molecules/compounds"而非 atoms/groups 连接；R "C 连 4 个不同的 alkyl group"（应是 4 个不同基团，不限烷基）；M2 也可以用在 Figure 4.2 上标注星号表示手性碳来给分

:::

<!-- md -->
{{lo-checklist}}
