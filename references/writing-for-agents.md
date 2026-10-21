# 为 Agent 写作（writing-for-agents）——写作质量权威源

> 读取时机：生成/修改任何 agent 消费的文档时（SKILL.md、AGENTS.md/CLAUDE.md、被 pointer 引用的 doc）。本文是 `skill-creator` 与 `skill-creator-pipeline` 的共享写作参照（单一源，两 skill 引用不复制）。
> 核心洞见：打包方式不同（skill / AGENTS.md / 普通文档），写作手法相同——agent 每次运行走同一个**过程**而非产出同一个输出，同样的杠杆让每个文档都可预测。

## Context pointer（上下文指针）

**Context pointer** 是 agent 上下文里持有的一条引用，它命名某个上下文之外的材料，并编码触达它的条件。skill 的 description 是一个；AGENTS.md 里指向某文档的一行是同一个东西。**指针的措辞**（不是它的目标）决定 agent 何时触达材料、触达得多可靠。一个必达的目标配一条弱措辞的指针 = 方差 bug：先锐化措辞，锐化无效才内联材料。

一条 pointer 干两件事：陈述材料是什么；列出应触发触达的**分支**（branch = 文档处理的独立 case，不同运行走不同路径）。常驻 pointer 的每个词每轮都花钱，所以它比正文更配狠剪：

- **Leading word 前置**：指针就是它做触发工作的地方。
- **一分支一触发词。** 同义词重命名同一个分支 = 一个分支写两遍；合并它们，只保留真正不同的分支。
- **砍掉正文已承载的 identity。**

## 两负载（the two loads）

你添加的每份文档与每条 pointer 花的是两种预算之一：

- **Context load（上下文负载）**：常驻材料对 agent 窗口的成本——AGENTS.md 一行、skill description、任何每轮坐在上下文里的东西，无论是否触发都在花 token 与注意力。
- **Cognitive load（认知负载）**：对人的成本——哪些文档存在、何时用哪个。人就是索引。不是要最小化的成本：它是人类能动性的价格；在人类判断要紧的地方花，在不要紧的地方省。

只被 pointer 触达的材料以 pointer 自身那一行为代价躲开 context load；完全没有 pointer 的材料全骑在 cognitive load 上。

## 信息层级（information hierarchy）

文档由两种内容构成：**steps**（agent 按序执行的动作）与 **reference**（按需查阅的定义/规则/事实）。两者自由混合：全 steps（菜谱）、全 reference（一套审查规则、本文）、或两者都有。核心决策是每一块内容在**信息层级**的哪一档：

1. **In-file step** 是主档：agent 要做什么、按什么顺序。
2. **In-file reference** 按需查阅。常是合法的平级集合（一次审查的每条规则同一档），这是好安排，不是 smell。
3. **Disclosed reference** 推出到独立文件，由 context pointer 触达，指针触发才加载。从同目录的兄弟文件到任何文档都能指的完全外部 reference 都算。

下推太少顶层臃肿；下推太多藏住 agent 真需要的材料。这个张力就是整个决策。

**Progressive disclosure** 是沿梯子下移（出主文件、藏到 pointer 后）让顶层保持可读。首要的不是 token 优化：它是层级得以被保护的方式。分支是最干净的 disclosure 判据：**每个分支都需要的内联；只有部分分支触达的推到 pointer 后**。文档有 steps 时，本该 disclosed 的 in-file reference 会把 steps 埋掉、把注意它们变成抛硬币——那是方差杠杆，不只是可读性。

**Co-location** 是档内配套：梯子决定一块内容**坐多低**，co-location 决定它坐下后**旁边是什么**。把一个概念的定义、规则、警示放在同一标题下而不是散落各处，读一处就把邻居带上。判据：文档应该读起来像「为 agent 写的文档」。成组材料读起来像；散落材料不像。（区别于 duplication：那是把一个意思在两处重复；scattering 是把一个意思撕碎到多处。）

**Sprawl** 是这里的失败模式：文档单纯太长，哪怕每行都活着且唯一。注意力摊薄在过剩上，每多一行就多一行要维持相关性。解药是梯子：把 reference 藏到 pointer 后，按分支或序列拆分，让每条路径只带它需要的。

## Steps 与完成判据（completion criteria）

每个 step 结束在一个**完成判据**上——告诉 agent 工作做完了的条件。两个属性让它成为杠杆：

- **Clarity（清晰）**：agent 能分辨 done 与 not-done 吗？模糊边界（「达成了理解」）招来 **premature completion**：step 没真正做完就结束，注意力滑向「要做完了」。还排在后面的可见 steps（**post-completion steps**）提供拉力；判据的清晰度是阻力。防守顺序：**先锐化边界**（本地且便宜）；只有边界不可再锐化**且**你观察到赶工时，才通过拆分序列把后面的 steps 藏起来。藏只跨真实上下文边界起效（handoff 或 subagent 派发；内联调用把后面 steps 留在上下文里，什么也没清掉）。
- **Demand（要求度）**：它要求多少。「每个被修改的 model 都有交代」强迫彻底工作，「产出一份变更清单」不会。Demand 驱动 **legwork**（agent 在工作内部做的挖掘，潜伏在措辞里而不是写成独立 step），且不限于 step：「每条规则都已应用」约束一整块平级 reference，如同「每步都做完」约束一个序列——这就是全 reference 文档仍能携带穷尽性门槛的方式。

最强的判据既可核对又穷尽。

## 何时拆分

一份文档拆成两份要花两负载之一，所以拆分必须挣回它的代价：

- **按序列拆**：当 post-completion steps 诱惑 agent 赶工前面那一步时，拆开这段 steps。让它们离开视野，驱动当前任务更多 legwork。小心反向：合并序列把每步的后续 steps 暴露给下文，招来 premature completion。
- **按调用方式拆**（skill 专属）：见下节。

## Leading words（引导词）

**Leading word** 是已活在模型预训练里的紧凑概念，agent 运行文档时用它思考（_lesson_、_fog of war_、_tracer bullets_、red、tight、seam、deep module）。作为 token 重复、永不作为句子重复，它积累出一个分布式定义，用最少 token 锚定一整片行为区域——靠招募模型已有的先验。自造词定义清楚也行，但造的词招募不到先验：预训练词白给的，你要用定义 token 付账；**先找已有的词**。

它锚定两处。正文中：**执行**——词每次出现 agent 都够到同一行为；在平级 reference 里它把注意力聚焦到一类要找的东西上。指针中：**调用**——同一个词活在你的 prompt、你的文档、你的代码库里时，agent 把共享语言连到材料上，更可靠地触达它。

找机会用 leading words 重构。三处拼写出来的三元组、花一整句话去比划一个想法的指针——每处都是求着收敛成单个 token 的段落：

- 「快、确定、低开销」→ *tight*（一条 *tight* 的回路）
- 「一条你信得过的回路」→ *red*，把模糊闸门变成二元可观察状态（回路在这个 bug 上变 *red*，或者没有）

双赢：更少 token，且 agent 挂思考的钩子更锐。假设每份文档都背着 leading words 能退休的复述。去找它们。

**Negation（否定句）** 是这个杠杆旁边的失败模式：用禁止来导航，把被禁行为拖进上下文，让它**更**可得而不是更不可得。别想大象，大象就占满一切；否定是弱修饰词，被强激活的概念碾过去，禁令半读成指令。**正面**提示：陈述目标行为（「写单行注释」），被禁的那个根本不被说出。禁令只在无法正面表述的硬护栏场景挣得席位；即便那时也配上正面目标，让注意力落在该做的事上。

## 修剪（pruning）

- 每个意思保住**单一事实源（SSOT）**：一个权威位置，改行为是一处编辑。**Duplication**（同一意思多处出现）花维护与 token，还把一个意思在层级上的显要度抬过它真实的级别。（leading word 的刻意反面：故意重复 token、永不重复意思。）
- **环境也是事实源**（`package.json` scripts、配置文件、目录布局、`--help` 输出），复述环境的文档是**缓存**：一份查询的副本，只有查询昂贵时才挣得它的负载。缓存 agent 看不到的东西：没写下来的约定、选择背后的理由、没有任何配置会坦白的坑。单文件单命令的查询留给环境，在那里不会过期。
- 逐行检查**相关性**：它还对文档做的事有贡献吗？一行失去相关性，要么从未贡献（纯解说、或本该 disclosed 的分支），要么随着它描述的行为或世界变化而过期。文档越短越容易保持相关。没有修剪纪律，默认命运是 **sediment（沉积层）**：因为添加感觉安全、删除感觉危险而过期层沉降下来，直到你必须钻透它们找还活着的东西。
- 逐句猎杀 **no-op**：模型默认已经遵守的指令，说了就是花负载说废话。判据（相对默认它改变行为吗？）是**模型相对**的、不是读者相对的：两个人对 no-op 有分歧，分歧其实在默认行为上，靠跑文档解决、不靠辩论。句子不及格时删整句，不是从里面删词。判据也分级 leading words：弱到打不过默认的词（agent 本来就 thorough-ish 时的 _be thorough_）是 no-op，修法是更强的词（_relentless_），不是换技巧。

## Skill 专属机制（frontmatter 与调用选择）

文档是 skill 时，额外多出三件事；其余写作手法上面的通用参照全覆盖。

### 调用方式（两种选择，交易两负载）

- **model-invoked**（模型可调用）skill 保留 `description`，agent 能自主触发它，其他 skill 也能够到它。你仍然可以键入它的名字：模型调用**总是包含**用户触达；description 只增加 agent 发现能力，从不剥夺人的触达。description 是 skill 的顶层 context pointer，被迫始终加载：用永久 context load 换可发现性。全 reference 的 model-invoked skill 还顺带是共享 reference 的一个家：别的 skill 能调用它，几个 skill 都需要的 reference 就可以住一处。机制：不设 `disable-model-invocation`，写面向模型的 description，携带触发分支（上面的 pointer 写法规则全额适用）。
- **user-invoked**（仅用户可调用）skill 把 description 从 agent 的可及范围剥掉：只有键入名字的人类能触发，其他 skill 也不能。零 context load，但花 cognitive load：你就是必须记得它存在的索引。机制：设 `disable-model-invocation: true`；description 变成面向人的一行摘要，剥离触发词列表。

只在 agent 必须自己够到该 skill、或另一个 skill 必须够到它时选 model-invocation。它只靠手动触发，就做成 user-invoked，不付 context load。

**两个 user-invoked skill 都需要的共享 reference 无家可归**：没有 description，谁也触发不了谁。把它推到 skill 系统外的普通文件：任何 skill 都能指的外部 reference。

### 按调用方式拆分

（序列拆分见上文「何时拆分」。）当你有一个该独立触发的**真 leading word**（你 prompt 里真会用的触发词）、或其他 skill 必须够到它时，拆出 model-invoked skill。你为新的常驻 description 付 context load，所以独立触达必须值回票价。

### Router skills（路由 skill）

user-invoked skill 多到你记不过来时，堆高的 cognitive load 用 **router skill** 治：一个 user-invoked skill，点名其余的以及各自何时用——人要记的从多个变成一个。它只能提示、永远不能触发它们：user-invoked skill 没有 description，除了人没有谁能触达。

