slug: 07-three-ais-agree
en-title: Three AIs Agree. You Still Have a Problem.
zh-title: 三个AI都同意，你仍然还有问题
en-deck: Multiple models can catch errors and widen a search. Agreement among them is evidence—not an independent court of appeal.
zh-deck: 多模型能够互相纠错，也能拓宽搜索。但它们之间的一致只是证据，不是一座独立于人的终审法院。
---
@@ EN
You ask one model whether a contract clause is risky. It says yes. You ask a second. It identifies the same problem. A third reaches the same conclusion and offers nearly identical language. Three independent confirmations feel qualitatively different from one answer. The uncertainty seems to have been voted away.

Sometimes this procedure is excellent. Sometimes three voices are one blind spot wearing different clothes.

## Agreement is only as independent as its sources

Models may differ in architecture, training, tools, and style while drawing on overlapping public text and similar conventions. They may all inherit the same common error. They may interpret your wording in the same way because the prompt silently leads them. They may agree because the easy-to-express answer is not the answer the situation needs.

This does not make cross-model checking worthless. If one model invents a citation and two others cannot find it, you have learned something useful. If several systems using different retrieval tools converge on a factual claim and expose their sources, confidence should rise. But the rise must be proportional to the actual independence and quality of the evidence.

Three paraphrases are not three witnesses.

## Disagreement is often more informative

When models disagree, users tend to ask which one is best. A better first move is to map the disagreement. Are they using different facts, different definitions, different risk tolerances, or different ideas of what success means?

Suppose one model recommends launching a product, another delaying it. Their forecasts may be similar. The real divergence may be that one treats reputational harm as recoverable while the other treats harm to a vulnerable user group as a stopping condition. Once exposed, that is not a contest of intelligence. It is a dispute about what may be traded for what.

Ask each model to state the assumption that, if changed, would reverse its conclusion. Ask one to criticize the other’s frame rather than its details. Then verify the claims that matter outside the models, using primary sources, domain experts, or direct observation.

> A second model is most valuable when it helps you see a second frame, not merely when it repeats the first answer.

## Build checks and balances, not an oracle panel

A useful multi-model workflow gives different systems different jobs. One generates possibilities. Another looks for factual weakness. A third identifies missing stakeholders and failure modes. A human decides which objections require evidence, which require conversation, and which reveal that the task itself was badly framed.

The roles should not all end in a score. If every critic reports back to the same metric, apparent pluralism collapses into one objective. Genuine checks and balances preserve the ability to say, “This result performs well by the chosen measure and still should not be used.”

In high-stakes settings, the person affected also needs a place in the system. An applicant should not face three automated evaluations with no route to contest the record. A patient should not be told that multiple models agree without a clinician prepared to explain what was considered and what was not. More models do not substitute for appeal.

## Know when consensus is the wrong goal

Some questions have answers that consensus can strengthen: whether a quotation appears in a source, whether code passes a test, whether a calculation reproduces. Other questions remain open even after every model agrees: whether to forgive, which loss to accept, whether an institution has asked too much of a person.

AI can illuminate these questions, but agreement does not change their kind. Ten systems recommending that you sacrifice one relationship for a career do not accumulate a life capable of making the sacrifice. A unanimous forecast that a policy will be popular does not establish that the policy is just.

Before consulting multiple models, classify the decision. Are you looking for a fact, an interpretation, a prediction, a design, or permission? The last category is where users are most likely to disguise responsibility as verification.

## The final check is not another model

At some point the loop must end. Set the stopping rule in advance when stakes are high. For factual questions: require traceable primary evidence. For technical decisions: require tests under the conditions that matter. For decisions affecting people: include a route for challenge and human reconsideration. For personal commitments: write down what no amount of model agreement would be allowed to decide.

Then let the models work. Their speed and variety are real advantages. They can expose complacency in a human team and catch mistakes no individual noticed. The lesson is not to trust one human over many machines by default.

It is to remember what a system of checks is for. Checks are meant to keep power answerable, not to create a larger voice that no one can question. When three AIs agree, you may have stronger evidence. You do not yet have someone who can take responsibility for believing it.

@@ ZH
你问一个模型，合同里这条约定有没有风险。它说有。再问第二个，它指出同样的问题。第三个也得出相同结论，甚至给出几乎一致的修改措辞。三次确认带来的感觉与一次完全不同，仿佛不确定已经被投票消除了。

有时，这种做法非常好。有时，三个声音只是同一个盲点换了三件衣服。

## 一致有多独立，取决于来源有多独立

不同模型可能采用不同架构、工具与表达风格，却共享大量公开文本和相似惯例。它们可能一起继承同一个常见错误，也可能因为提示词悄悄引导了方向，而用同一种方式理解问题；有时它们一致，只是因为最容易说清的答案，并不是处境真正需要的答案。

这不意味着多模型核查毫无价值。一个模型虚构了引用，另外两个找不到，你得到了有用信号；几个使用不同检索工具的系统围绕一个事实收敛，并且都展示了来源，可信度确实应该上升。但上升多少，必须与证据真实的独立程度和质量相称。

三种改写，不等于三位证人。

## 分歧往往更有信息

模型互相矛盾时，人们容易追问“到底哪个更强”。更好的第一步，是先画出分歧发生在哪里：它们使用了不同事实、不同定义、不同风险偏好，还是不同的成功标准？

假设一个模型建议产品立即上线，另一个建议推迟。两边对市场结果的预测也许相近，真正的差别可能是：一边认为声誉损害以后可以修复，另一边把对脆弱使用者的伤害当成停止条件。区别一旦显露，就不再是智能高低的比赛，而是哪些东西可以拿来交换哪些东西。

可以让每个模型说出：哪个假设一旦变化，结论就会反转；也可以要求它批评对方的框架，而不只挑细节。然后把真正重要的主张带到模型之外，用第一手来源、专业人士和直接观察验证。

> 第二个模型最有价值的时候，不是它重复了第一个答案，而是它让你看见第二种框架。

## 建立制衡，不要组建神谕委员会

好的多模型流程，会让不同系统承担不同任务：一个生成可能，一个寻找事实弱点，一个寻找被遗漏的人与失败路径。然后由人决定，哪些异议需要补证据，哪些需要与当事人谈话，哪些说明整个任务从一开始就问错了。

这些角色不能最后都汇总成同一个分数。如果所有批评都向同一指标报告，表面的多元最终仍然塌成一个目标。真正的制衡必须保留这样一句话：“它在既定指标上表现很好，但仍然不应该使用。”

在高风险场景里，被影响的人也必须在系统里有位置。求职者不该面对三份自动评价，却没有途径质疑资料；病人也不该只听说多个模型意见一致，却找不到一个愿意解释系统看见了什么、又遗漏了什么的医生。增加模型数量，不能取代申诉。

## 有些问题不以共识为目标

有些问题确实会因共识变得更可靠：一句引文是否出现在来源里，一段代码是否通过测试，一个计算能否复现。另一些问题即使所有模型一致，仍然保持开放：要不要原谅，愿意接受哪一种损失，一个机构是否已经向人索取过多。

AI 能够照亮这些问题，但一致并不会改变问题的种类。十个系统都建议你为了事业牺牲一段关系，也不会因此积累出一段能够替你作出牺牲的人生；所有模型都预测一项政策会受欢迎，也不能证明政策正当。

在咨询多个模型以前，先分辨自己寻找的是事实、解释、预测、设计，还是许可。最后一种最危险，因为我们最容易在这里把逃避负责伪装成反复核验。

## 最后的核查，不是再问一个模型

循环总要结束。风险越高，越应该提前设定停止规则。事实问题要求可追溯的第一手证据；技术决策要在真正重要的条件下通过测试；影响人的决定必须保留质疑与人工复议路径；个人承诺则要写清楚，有什么不能因为模型数量增加就交出去。

然后尽管让模型工作。它们的速度与多样性都是真实优势，可以打破人类团队的自满，也能找到没有任何个人注意到的错误。这里的结论不是默认相信一个人而不信许多机器。

关键在于记得制衡系统为何存在。制衡是为了让权力仍然能够被追问，而不是制造一个更大的、无人可以质疑的声音。三个 AI 一致，你也许得到了更强证据；可你仍然没有得到一个能够为“相信这些证据”负责的人。
