slug: 02-prompting-is-not-judgment
en-title: Prompting Is Not Judgment
zh-title: 提示词不是判断力
en-deck: A better prompt can improve an answer. It cannot tell you which answer deserves to govern the situation.
zh-deck: 更好的提示词可以改善答案，却不能告诉你：在这个具体处境里，哪一个答案有资格成为行动的依据。
---
@@ EN
There is a particular pleasure in learning to prompt well. A vague request becomes a precise one. You assign a role, specify an audience, add examples, demand objections, and ask the model to compare alternatives. The output improves so visibly that it is tempting to treat prompting as the new name for thinking.

It is not. Prompting is a powerful way to arrange a search. Judgment begins where the search can no longer decide what matters.

## Better instructions solve the problem you named

Imagine you are choosing whether to leave a job. A weak prompt asks, “Should I quit?” A stronger prompt describes salary, savings, responsibilities, prospects, health, and tolerance for risk. It asks for scenarios rather than a verdict and requests the strongest case against each option.

The second prompt is clearly better. It exposes assumptions and gives the model more of the world. But it still inherits a prior decision: what belongs in the problem. Perhaps you provided salary and promotion odds but omitted the small humiliation you have been explaining away for two years. Perhaps you mentioned family expenses but not the promise you made to yourself after your last burnout. A model cannot weigh what never entered the frame.

Even when all the facts are present, weights do not appear by themselves. Is six months of financial uncertainty worse than three more years of work that is changing who you become? There is no neutral prompt that can settle the exchange rate. The answer depends on a life, not merely a dataset.

## The prompt can contain another person's law

Prompts often arrive disguised as our own requests while carrying someone else's definition of success. “Rewrite this so the client cannot object.” “Make my team more productive.” “Optimize my child’s college profile.” Each sounds practical. Each may also turn another person into a surface to be managed.

The model will usually cooperate with the objective it is given. That is one of its strengths. The pause has to come from elsewhere: Why must the client be unable to object? What is the team producing, and at what human cost? Does the child recognize their life in the profile being optimized?

These questions do not make prompting useless. They make it honest. Sometimes the right revision is not a cleverer instruction but a different task: “Show me what legitimate objections the client may have.” “Identify which productivity gains merely move cost onto the team.” “Help me begin a conversation in which my child can disagree with my plan.”

> Before improving the prompt, ask whether the objective deserves to survive the prompt.

## Ask for friction, not just performance

Many advanced prompting techniques aim to reduce error by adding structure. That is sensible. Yet a prompt can also be designed to preserve disagreement. Ask the model to identify what would remain unresolved even after its best answer. Ask which stakeholder is absent from the framing. Ask what new evidence would reverse the recommendation. Ask for two incompatible but defensible accounts of the same situation.

This kind of friction is valuable because an AI answer tends to arrive in a unified voice. The smoothness can make a contested decision look like a technical conclusion. By deliberately asking for the seam, you prevent coherence from masquerading as necessity.

Still, no meta-prompt escapes the problem entirely. You can ask the model to criticize its assumptions, then criticize the criticism, then simulate a panel of opponents. Eventually someone has to decide that the inquiry has gone far enough for action. That stopping point is itself a judgment.

## Good judgment may reject an excellent answer

A manager asks AI to design a fair schedule. The model balances preferences, seniority, workload, and legal constraints. Its proposal is measurably better than the old schedule. Then one employee explains that the new “fair” rotation places her on the only evening she can care for her father.

Nothing in this moment proves the model failed. The schedule optimized the conditions it received. Judgment means allowing a real person to reopen those conditions. It means treating the answer as a proposal whose legitimacy can be challenged, not as the inevitable result of enough information.

This distinction matters most when the output is strong. If the model is obviously wrong, we remain awake. When it is impressively right, we are tempted to believe that the work of judgment has ended. Often it has only become visible.

## A prompt is a door, not a destination

Use every advantage of good prompting. Give context. Separate facts from assumptions. Request uncertainty. Ask for counterarguments. Iterate. But keep one question outside the prompt: *What am I unwilling to let this procedure decide for me?*

The answer may be small. You may refuse to let a score determine whom to interview, let a predicted response decide whether to apologize, or let a polished strategy replace a conversation with the person who must live under it.

Prompting can widen the room in which thought happens. Judgment is the act of remaining present inside that room—especially when the machine has made leaving it feel effortless.

@@ ZH
学会写提示词，有一种很直接的快感。一个含糊的问题逐渐变得精确：设定角色、说明读者、补充例子、要求反驳、比较不同方案。输出肉眼可见地变好，于是很容易产生一种错觉：提示词工程，就是这个时代新的思考方式。

它不是。提示词是一种很强的搜索与组织方法；判断力开始于搜索再也不能替你决定“什么重要”的地方。

## 好指令解决的是你已经命名的问题

假设你在考虑要不要辞职。差的提示词只问：“我该辞职吗？”好的提示词会交代收入、存款、家庭责任、行业机会、健康状况和风险承受力；它不要求一句结论，而是让 AI 展开情景，并为每个选择提出最强反对意见。

第二种当然更好。它暴露假设，也把更多现实放进来。可它仍然继承了一个更早的决定：哪些东西算作这个问题的一部分。也许你写了工资和晋升概率，却没有写那种已经忍了两年的细小羞辱；也许你写了家庭开支，却没有写上一次耗尽之后对自己许下的承诺。没有进入画面的东西，模型无从衡量。

即使事实全部到场，权重也不会自动出现。六个月的财务不确定，是否一定比三年继续做一份正在改变你的工作更糟？这里没有一条中立提示词能给两者规定汇率。答案来自一段人生，而不只是来自一组资料。

## 提示词里可能藏着别人的法

很多提示词看上去是我们自己的要求，其实带进了别人的成功定义：“把这封信改到客户无法反驳。”“让团队效率更高。”“优化孩子的大学申请形象。”每一句都很实用，也都可能把另一个人变成需要管理的表面。

模型通常会忠实配合你给出的目标，这是它的能力。暂停却必须从别处发生：为什么客户不可以反驳？团队究竟在生产什么，代价由谁承担？那个被优化申请形象的孩子，是否还认得出里面是自己的人生？

这些问题不会让提示词失去意义，反而会让它诚实。有时真正需要改的不是措辞，而是任务本身：“请列出客户可能提出的合理异议。”“哪些效率提升只是把成本转嫁给团队？”“帮我开启一场孩子可以不同意我的谈话。”

> 在优化提示词以前，先问一问：这个目标本身是否值得被保留下来。

## 不只要求表现，也要主动制造摩擦

很多高级提示技巧都在通过增加结构来减少错误，这当然有价值。但提示词也可以被设计成保存分歧。你可以让 AI 指出：即使给出最佳答案，还有什么没有被解决；这个问题的框架漏掉了谁；出现什么新证据时，建议必须反转；同一件事能否存在两个互不相容、却都站得住的解释。

这种摩擦很重要，因为 AI 的答案往往以统一而流畅的声音出现。它会让一个本来有争议的决定，看起来像纯粹的技术结论。主动要求它指出接缝，是为了不让“说得通”伪装成“只能如此”。

不过，没有任何元提示词能无限逃离这个问题。你可以让模型批评自己的假设，再批评这份批评，再模拟一桌反对者。到了最后，仍然必须有人决定：调查已经足够，现在需要行动。这个停止点本身就是判断。

## 好的判断，有时会拒绝一个优秀答案

一位管理者让 AI 设计公平排班。模型综合偏好、资历、工作量与法律限制，给出的方案也确实比旧排班合理。可一名员工说，新的“公平轮班”把她排到了唯一能够照顾父亲的那个晚上。

这并不证明模型失败了。它只是很好地优化了自己收到的条件。判断力意味着允许一个真实的人重新打开这些条件；意味着把答案当成可以被质疑其正当性的建议，而不是信息足够以后必然出现的结果。

输出越强，这一区别越重要。模型明显出错时，我们反而保持清醒；当它正确得令人佩服，我们最容易以为判断已经结束。很多时候，判断其实只是刚刚显出形状。

## 提示词是一扇门，不是终点

好的提示方法都可以用：补充语境，区分事实与假设，要求说明不确定，索要反方意见，反复修改。但请把一个问题留在提示词之外：*有什么东西，是我不愿交给这一套程序替我决定的？*

答案可能很小。你可能不愿让一个分数决定谁有资格面试，不愿让对方反应的预测决定自己是否道歉，也不愿让一份漂亮策略取代与那个必须生活在策略之下的人谈一次话。

提示词可以把思考的房间扩得更大。判断力则是你仍然留在房间里——尤其是在机器已经让离开这间房变得毫不费力的时候。
