#!/usr/bin/env python3
"""Build the English, Simplified Chinese, and Traditional Chinese Analects edition.

The five additional reading editions are built from edited copy by
``build_analects_languages.py``.  This builder keeps the shared source pages
aware of every edition so the language menu and hreflang graph remain stable.
"""

from __future__ import annotations

import argparse
import ctypes
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/hanqin/Documents/大知解论语")
TARGET = ROOT / "essays" / "analects"
UTF8 = 0x08000100


ITEMS = [
    ("01", "opposite-answers", "The Teacher Gave Opposite Answers", "‘On hearing it, should I act?’"),
    ("02", "waits-for-the-question", "He Waits Until the Question Is Yours", "‘I do not open the way for the unready.’"),
    ("03", "empty-empty", "He Says He Has No Knowledge in Store", "‘Empty, empty.’"),
    ("04", "prefer-not-to-speak", "If the Teacher Stops Speaking, What Do We Record?", "‘I would prefer not to speak.’"),
    ("05", "hui-does-not-help", "He Thought Yan Hui Agreed Too Easily", "‘Hui does not help me.’"),
    ("06", "no-private-lesson", "Even His Son Received No Private Lesson", "Chen Kang questions Boyu."),
    ("07", "said-in-jest", "A Teacher Admits He Was Wrong in Front of the Class", "‘What I said before was a joke.’"),
    ("08", "if-you-are-at-peace", "If You Are at Peace with It, Do It", "Zai Wo and the three-year mourning period."),
    ("09", "no-way-forward", "Yan Hui Was Not a Fan", "‘I have no way to go on.’"),
    ("10", "was-anyone-hurt", "The Stable Burns. What Does He Ask First?", "‘Was anyone hurt?’"),
    ("11", "refusing-sagehood", "He Kept Refusing to Be a Sage", "‘How would I dare claim sagehood or ren?’"),
    ("12", "four-answers-on-filial-care", "Four People Ask about Filial Conduct", "Four questions, four different answers."),
    ("13", "three-answers-on-ren", "Ren Has No Standard Answer", "Three students, three prescriptions."),
    ("14", "defending-guan-zhong", "He Defends the ‘Traitor’ Twice", "The case of Guan Zhong."),
    ("15", "why-he-laughed-at-zilu", "Why Did He Laugh at Zilu?", "Four students describe their aspirations."),
    ("16", "knowing-it-cannot-be-done", "A Gatekeeper Defines Him", "‘Knowing it cannot be done, yet doing it.’"),
    ("17", "four-refusals", "Confucius’s Four Refusals", "No guessing, no certainty, no rigidity, no self-centering."),
    ("18", "transmit-not-compose", "Why Did He Not Write a Book?", "‘I transmit; I do not compose.’"),
    ("19", "people-may-follow", "The ‘Keep the People Ignorant’ Line", "Who was it addressed to?"),
    ("20", "virtue-and-shame", "The Sign of ‘Rule by Virtue’ May Be Hanging Backwards", "Shame and self-government."),
    ("21", "boundaries-not-checklists", "Four ‘Do Nots’ and Nine ‘Considerations’", "A boundary is not a checklist."),
    ("22", "let-the-ruler-be-a-ruler", "‘Let the Ruler Be a Ruler’", "The first demand is on the ruler."),
    ("23", "correcting-names", "Correcting Names Is Not Pedantry", "Who is doing what, and by what right?"),
    ("24", "study-then-office", "The Famous Line Cut in Half", "‘Study, then take office.’"),
    ("25", "thinking-without-office", "If You Hold No Office, May You Still Think?", "‘Do not plan another’s government.’"),
    ("26", "detesting-the-fixed", "The Supposed Conservative Who Condemned Rigidity", "‘I detest the fixed.’"),
    ("27", "danger-of-must", "The Man Who Always Keeps His Word Is Called Petty", "The danger of ‘must.’"),
    ("28", "negative-golden-rule", "Why Not ‘Give Others What You Want’?", "The negative Golden Rule."),
    ("29", "scolding-yuan-rang", "He Was Not Condemning Old People", "He was scolding Yuan Rang."),
    ("30", "empty-ritual", "‘Man-Eating Ritual’? Confucius Condemned Empty Ritual First", "When form survives its reason."),
    ("31", "three-opening-questions", "The Analects Begins with Three Questions, Not Three Commands", "Learning, friendship, and recognition."),
    ("32", "neither-curse-nor-kneel", "Neither Curse Confucius nor Kneel to Him", "What this reading opposes."),
    ("33", "the-chapter-next-door", "The Chapter Next Door", "‘Only the highest wise and lowest foolish do not change.’"),
    ("34", "difference-without-rank", "People Differ; Therefore They Must Not Be Ranked", "Four ways of knowing."),
    ("35", "defy-the-teacher", "He Told You to Defy the Teacher", "Who told you to fear the sage?"),
    ("36", "later-lineage", "Later Readers Built Him a Lineage", "The ‘Yao Said’ chapter."),
    ("37", "women-and-petty-men", "We Will Neither Excuse This Line nor Accept Its Use", "‘Women and petty men.’"),
    ("38", "five-beauties-four-evils", "Eight Words and a Checklist", "The five beauties and four evils."),
    ("39", "ji-shi-handout", "The Analects Chapter That Reads Like a Handout", "The Ji Shi chapter."),
    ("40", "two-ways-of-praising", "Two Ways of Praising Someone", "What does ‘lofty’ explain?"),
    ("41", "he-did-not-curse-the-age", "He Did Not Curse the Age", "Criticism needs a person and a case."),
    ("42", "burial-against-his-wishes", "A Funeral against the Teacher’s Wishes", "The burial of Yan Hui."),
    ("43", "zigong-defends-his-teacher", "How Zigong Defended His Teacher without Making Him a Saint", "Learning how to protect a teacher’s humanity."),
    ("44", "zengzi-and-the-list", "The Excellent Student Who Turned Living Speech into Items", "Zengzi and the attraction of a transmissible formula."),
    ("45", "chapter-without-confucius", "A Chapter in Which Confucius Never Speaks", "The Zizhang chapter."),
    ("46", "not-yet-ren", "‘Not Yet Ren’ May Be Praise", "Classmates judge Zizhang."),
    ("47", "they-could-have-left-it-out", "They Could Have Left These Things Out", "The honesty of the recorders."),
    ("48", "three-encounters-with-recluses", "Three Encounters with Recluses", "Must commitment take one form?"),
    ("49", "the-step-only-you-can-take", "The Step the Teacher Cannot Take for You", "Zilu and Zigong."),
    ("50", "he-left-no-doctrine", "He Left No Doctrine", "After the reconstruction."),
]

MOVEMENTS = [
    (1, 18, "The Person in the Room", "他是这样一个人", "先看他说话、听人、改口与停下来的方式。"),
    (19, 31, "True Words, Misread", "真话，被读歪", "把被截断、倒挂或抽空语境的名句放回原处。"),
    (32, 41, "What This Reading Opposes", "我们反对什么", "不做真假裁判，只说明哪些材料不能替代现场。"),
    (42, 50, "The Students—and the Limits of a Record", "弟子们，与记录的限度", "看弟子如何继承、误读、争辩，也如何诚实地留下毛边。"),
]

RESEARCH = [
    ("General Introduction", "One Who Cultivates", "涵育者", "https://self-as-an-end.net/papers/sae-analects-intro.html"),
    ("Part I", "The Instrument", "器", "https://self-as-an-end.net/papers/sae-analects-1.html"),
    ("Part II", "The Man Who Would Not Be a Sage", "不肯成为圣人的人", "https://self-as-an-end.net/papers/sae-analects-2.html"),
    ("Part III", "In the Room", "在场", "https://self-as-an-end.net/papers/sae-analects-3.html"),
    ("Part IV", "What Was Built in His Name", "以他之名建成的东西", "https://self-as-an-end.net/papers/sae-analects-4.html"),
]


# Reader-facing English reconstructions. Each entry is written as an essay rather
# than translated sentence by sentence from the Chinese source.
ENGLISH: dict[str, list[str]] = {
    "opposite-answers": [
        "Two students ask Confucius the same practical question: once you hear what is right, should you act on it at once? Zilu receives a brake—your father and elder brother are still alive; how could you act without consulting them? Ran You receives the opposite instruction: act when you hear it. If either sentence is lifted out of the scene, it becomes a plausible maxim. Put them side by side and Confucius appears inconsistent.",
        "A third student, Gongxi Hua, is puzzled enough to ask. Confucius answers by naming the difference the two maxims conceal. Ran You tends to hang back, so he pushes him forward. Zilu has energy enough for two people, so he holds him back. The answer is not stored inside the question. It emerges from the question and the person asking it.",
        "Notice the timing. Confucius does not begin with a lecture on individualized teaching. He lets the contradiction become visible, then explains it only when someone can no longer connect the two replies. Even the principle of teaching according to the person is not handed out as a universal principle. It is taught according to the person.",
        "This is why the names in the Analects are not decorative background. They are part of the prescription. Remove Ran You and Zilu, and two carefully aimed interventions become rival commandments: always consult your elders; always act decisively. Both can be printed on posters. Neither tells us what happened in the room.",
        "The Analects became an almanac of sayings largely by losing those names one at a time. To reopen it, we have to reverse that operation. Before asking what ‘The Master said’ means for everyone, ask the simpler question: whom was he trying to move, and in which direction?",
    ],
    "waits-for-the-question": [
        "The classroom many readers associate with Confucius is easy to picture: rows of children reciting, a teacher supplying the right answer, discipline measured by accurate repetition. Yet one of his best-known statements describes almost the reverse. He will not open the way for someone who is not straining to understand; he will not supply the missing words for someone who is not struggling to speak. Show one corner, and if the learner cannot return with the other three, he does not repeat the lesson.",
        "The heaviest word in that passage is ‘not,’ and it is addressed first to the teacher. Do not rush to explain. Do not mistake the learner’s silence for a vacancy that your knowledge must fill. Wait until the difficulty has become theirs—until the question is not merely assigned but felt.",
        "The famous one-corner image sharpens the point. A teacher may reveal something real and still leave most of the work undone. The other three corners are not a test imposed after the lesson; finding them is part of learning. If the teacher draws the whole square, the learner may possess a diagram while never having formed the relation for themselves.",
        "This demanding method did not mean a narrow door. Confucius says he refused instruction to no one who brought even the modest customary gift; elsewhere, ‘in teaching there should be no classes.’ Access is broad, but the path varies with readiness. He does not rank human worth. He distinguishes the next step that can actually become someone’s own.",
        "There is an irony in the afterlife of this passage. A statement against intellectual force-feeding became one more sentence generations of students were forced to memorize. Its fate is also its proof: the words of a teacher who withheld the remaining three corners can themselves be used to prevent anyone from looking for them.",
    ],
    "empty-empty": [
        "Confucius is often imagined as a man carrying a warehouse of moral answers. Ask about conduct, government, ritual, or humaneness, and he opens the correct drawer. In the Analects, however, he gives a stranger a stranger self-description: ‘Do I possess knowledge? I possess none. But if a common person asks me something, empty as I am, I knock at the question from both ends until I exhaust it.’",
        "This is not the modesty of someone who owns a full storehouse and politely denies it. It is a working rule: do not prepare the answer before the other person arrives. The question must be sounded, tested, and opened from within. The teacher’s knowledge matters, but it is not allowed to replace the shape of the problem brought into the room.",
        "The same pattern explains an apparent oddity. Confucius speaks rarely of profit, fate, and ren—humaneness—even though ren is conventionally called the center of his thought. When it does appear, it usually appears in response to a named person. Yan Hui, Zhonggong, Sima Niu, Fan Chi, and Zigong ask, and each receives a different reply. There is no public master class defining ren once for everyone.",
        "Emptiness here is not intellectual poverty. A full vessel cannot receive the person opposite it. Remaining empty means remaining able to learn, and able to teach without pouring one finished doctrine into every mind. Confucius can know texts, precedents, music, and ritual while refusing to let that knowledge settle the question in advance.",
        "The recorders deserve credit for preserving this uncomfortable portrait. Hagiography would have given us a teacher who knew everything and answered every question. They left ‘I possess no knowledge,’ ‘empty, empty,’ and the things he would not discuss. The omniscient sage is a later statue. The man in the text keeps an empty chair for the next questioner.",
    ],
    "prefer-not-to-speak": [
        "Every textbook wants to summarize Confucius: ren, ritual, reciprocity, the mean. The examination question asks for one core, and the successful student supplies it. The Analects repeatedly stages a less convenient moment. Zigong asks whether there is one saying that could guide an entire life. Confucius offers a boundary—reciprocity, perhaps; do not impose on others what you would not want yourself—yet even here the tentative ‘perhaps’ matters.",
        "Elsewhere he tells Zigong that his way is threaded through by one thing. Zigong cannot name it. After Confucius leaves, Zengzi supplies the answer for the other students: loyalty and reciprocity, and nothing more. Zengzi signs the explanation with his own name. It may point in the right direction. But ‘nothing more’ closes the opening the teacher left.",
        "Then Confucius says something stranger: he would prefer not to speak. Zigong protests that without speech the students would have nothing to transmit. Confucius points to heaven. The seasons move; the hundred things grow. What does heaven say? He is not announcing a vow of silence—the book is full of his precise and practical talk. He is marking a limit to what speech can hand over.",
        "A teacher can give examples, corrections, questions, and boundaries. What connects them into a living orientation must finally be connected by the learner. The instant the teacher names that thread as a complete formula, it becomes the teacher’s possession again: something to quote rather than something another person has learned to see.",
        "Later readers have proposed many candidates for the missing ‘one.’ Each may be a serious interpretation. None can erase the silence from which interpretation begins. The question is not merely what single principle unifies Confucius. It is whether a unifying principle is still yours when someone else has already sealed it, labeled it, and told you there is nothing more.",
    ],
    "hui-does-not-help": [
        "Yan Hui is remembered as Confucius’s finest student: poor, serene, devoted, and seemingly incapable of disagreement. Confucius’s own complaint is therefore startling. ‘Hui does not help me. There is nothing I say that fails to please him.’ A teacher who wanted obedience would call this perfection. Confucius calls it useless to him.",
        "The remark belongs beside a harder instruction: in matters of ren, do not yield even to your teacher. The teacher is not the highest authority in the room. What is right outranks him, and a student who has learned to judge must be able to use that judgment against the person who taught it. Respect that cannot answer back leaves both people exposed to error.",
        "The political version is even sharper. Duke Ding asks whether one saying could ruin a state. Confucius answers that if a ruler’s one delight is that no one contradicts him, ruin may lie close by. The sentence a person in power most wants to hear—no one dares oppose you—is not evidence of successful rule. It is the mechanism by which a bad decision travels uncorrected through an entire country.",
        "This does not make contradiction sacred. A student can object badly, and an adviser can oppose for vanity. The point is structural: a room in which disagreement is impossible cannot discover its mistakes. Confucius wants students who develop judgments robust enough to resist him, because only then has teaching produced more than an echo.",
        "‘Reverence for the teacher’ is often invoked as though it were the heart of the Analects. What the book actually gives us is a teacher irritated by perfect assent, withdrawing his own immunity, and warning rulers against the pleasure of an unopposed voice. If nobody can tell you no, the problem may not be that everyone finally understands. It may be that you have made understanding unsafe.",
    ],
    "no-private-lesson": [
        "Traditions built around masters often produce rumors of an inner teaching: the public receives lessons, the chosen disciple receives the key, and the teacher’s child hears what is never written down. The Analects includes a small investigation into precisely this suspicion. Chen Kang asks Confucius’s son, Boyu, whether he has received any special instruction.",
        "Boyu recalls two encounters. On one occasion his father asked whether he had studied the Odes; when he said no, Confucius told him that without them he would not know how to speak. On another, he was asked about ritual and told that without it he would not know how to take his stand. That was all. Both conversations happened as Boyu crossed the courtyard. No closed door, no family doctrine.",
        "Chen Kang leaves delighted. He asked one question and learned three things: the importance of poetry, the importance of ritual, and that a cultivated person keeps distance from his own son. The last claim does not mean emotional neglect. It means that kinship does not open a privileged channel into knowledge unavailable to everyone else.",
        "The wider record supports him. Confucius did not give his son an exceptional funeral; when Yan Hui’s father later asked him to sell his carriage for a more elaborate outer coffin, he pointed to the same restraint in his own family. A beloved student did not receive a ceremonial exemption, and a son did not receive an intellectual one.",
        "This is unusually strong evidence because Confucius does not certify his own fairness. A suspicious outsider checks with the supposed beneficiary. The son’s report reveals ordinary lessons already present throughout the school. ‘Teaching without class distinction’ begins at home: not by withholding from the son, but by refusing to make sonship a title to something others cannot receive.",
    ],
    "said-in-jest": [
        "‘The Master said’ later became a seal: once stamped onto an argument, discussion ended. Yet the Analects preserves a scene in which a student uses the teacher’s own principle to correct him. Confucius visits Wucheng and hears stringed instruments. He jokes that one does not need the full apparatus for governing such a small place—why use an ox-cleaver to kill a chicken?",
        "Ziyou answers with a lesson he learned from Confucius: a cultivated person who studies the Way learns to care for others; ordinary people who study it become easier to guide. If education is good for ruler and people alike, why should Wucheng be too small for it? The student does not reject his teacher’s standard. He applies it where the teacher, for a moment, did not.",
        "Confucius turns to the others: ‘Students, Ziyou is right. What I said before was only a joke.’ The public nature of the correction matters. He does not privately preserve authority while quietly changing course. He tells the class that the student’s answer is better than his remark. There is pride in the admission: this is what it looks like when a student can use a teaching rather than merely repeat it.",
        "Other scenes confirm the habit. When someone exposes his mistaken defense of Duke Zhao’s ritual knowledge, Confucius calls himself fortunate that his errors are always discovered. After Zai Wo’s conduct shows the limits of trusting speech alone, he revises his method: now he will listen to words and observe action. Error becomes an occasion for learning, not a threat to the teacher’s identity.",
        "The line ‘To make a mistake and not correct it—that is the mistake’ is credible because its speaker lets the record show him doing so. The first person in the Analects who refuses to treat ‘The Master said’ as infallible is the Master himself.",
    ],
    "if-you-are-at-peace": [
        "The three-year mourning period became one of the heaviest institutions associated with Confucian ritual. In the Analects it appears not as a regulation smoothly transmitted from master to disciple, but as an unresolved argument. Zai Wo asks whether one year would be enough. If cultivated people withdraw for three, he says, ritual and music will decay; a full cycle of crops and fire-making already marks a year.",
        "Confucius does not dismiss the argument. He asks a different question: after one year, would Zai Wo be at ease eating fine rice and wearing brocade? Zai Wo answers with one uncompromising word: yes. ‘If you are at ease, then do it,’ Confucius says. He repeats the permission after explaining his own experience: for a child’s first three years the parents carry it in their arms; during mourning, food, music, and comfortable housing simply do not feel right to him.",
        "That explanation is a reason, not a command. Confucius cannot make Zai Wo feel the unease on which his own observance rests. He can disclose the source of his judgment, ask the student to examine his own, and leave the action with him. After Zai Wo departs, Confucius calls him lacking in ren. The disappointment is real. So is the permission.",
        "This is not a modern celebration of every preference. Zai Wo’s answer may be shallow; Confucius plainly thinks it is. What the scene refuses is the final step from ‘I think you are wrong’ to ‘therefore your judgment no longer belongs to you.’ The teacher argues, fails to persuade, and does not pretend the failure has disappeared.",
        "Later states wrote three-year mourning into law and punished violations. Coercion completed what Confucius did not complete in conversation. The book preserves the harder possibility: a tradition may hold something sacred, give its deepest reason, and still face another person who says, ‘I am at ease.’ What happens then reveals whether ritual remains an answer or has become a weapon.",
    ],
    "no-way-forward": [
        "Yan Hui’s devotion is often flattened into fandom: the perfect disciple who agrees, endures poverty, and follows. His most revealing tribute to Confucius says something quite different. The more he looks up, the higher the teaching seems; the more he bores into it, the harder it becomes. It appears before him and suddenly behind. Confucius broadens him with culture, disciplines him with ritual, and makes stopping impossible. Yan Hui exhausts his ability—and then says, ‘Though I wish to follow it, there is no way forward.’",
        "That last sentence is not a complaint that the teacher failed to provide a route. It identifies the place at which routes run out. Materials can be given. Practices can be trained. A direction can be indicated. But the step from seeing a way of life before you to standing there as its source cannot be walked on another person’s behalf.",
        "A fan always has a road: keep following the admired person. A student eventually needs a destination the teacher cannot occupy for him. Yan Hui’s ‘no way’ therefore describes successful teaching more accurately than effortless agreement. Confucius has brought him to the threshold where imitation must end.",
        "The record does not pretend he finished. After Yan Hui’s death, Confucius does not seal him with the title ‘ren’ or ‘sage.’ He grieves: ‘I saw him advance; I never saw him stop.’ The final assessment remains in the progressive tense. Later tradition made Yan Hui the ‘Renewing Sage,’ a completed honorific. His teacher remembers movement interrupted.",
        "To cultivate another person is to provide what can be provided and stop before the one step that would make their life yours. Yan Hui knew exactly where that stop occurred. ‘There is no way forward’ may be the most honest sentence a learner can offer—and one of the highest forms of praise a teacher can receive.",
    ],
    "was-anyone-hurt": [
        "One chapter of the Analects records how Confucius dressed, ate, sat, walked, entered court, and responded to ritual occasions. Read as a rulebook, it makes him look like a ceremonial machine: precise cuts of meat, straight mats, correct posture, silence at meals. But a camera can capture what a person does more easily than why this situation called for that action.",
        "Then the stable burns. Confucius returns from court and asks, ‘Was anyone hurt?’ The record adds: he did not ask about the horses. In a moment with no time for a prepared performance, the ordering behind the details becomes visible. Human life comes before valuable property.",
        "This does not make every external form irrelevant. Confucius distinguishes forms that can change from the relation a form protects. The old ceremonial cap was made of linen; people now use cheaper silk, and he follows the majority. The old practice placed a bow below the hall; people now bow above it, which he considers presumptuous, so here he refuses the majority. Antiquity is not the rule, and popularity is not the rule. He judges what the change does.",
        "That is what a list of habits cannot preserve. The same living judgment may produce conformity in one case and dissent in the next. Once only the actions remain, readers can turn them into a timeless code and miss the act of discrimination that made them meaningful.",
        "The chapter of daily conduct is therefore not uniformly dead. Most of it gives us the outside. A few moments allow a glimpse inward. When the stable burns, action and reason nearly coincide: danger, a question, and no inquiry about the lost asset. If someone filmed every meal and gesture of your life, would they finally possess you—or would the most important ordering still appear only in moments they could not schedule?",
    ],
    "refusing-sagehood": [
        "The temple title says ‘Most Sage and Foremost Teacher.’ Confucius’s own descriptions stay stubbornly unfinished. When a court official wonders whether his many abilities prove heavenly sagehood, Zigong agrees. Confucius dismantles the compliment with biography: the official does not know him; he was poor when young, and poverty made him learn many practical tasks. The miraculous gift becomes a history of necessity and work.",
        "Asked how Zilu should describe him, Confucius offers no doctrine and no achievement: this is a person who works so intently he forgets to eat, becomes so absorbed in joy he forgets his troubles, and does not notice old age approaching. Every verb is still in motion. Elsewhere he says he was not born knowing; he loved the old and sought it diligently.",
        "He is just as direct about the titles others want to give him: ‘As for being a sage or a man of ren, how would I dare? Perhaps it may be said that I work at it without tiring and teach others without weariness.’ He will acknowledge the continuing practices, not the completed identity. Gongxi Hua replies that this is precisely what the disciples cannot learn.",
        "Refusing sagehood is more than conventional modesty. A sage is easily turned into a finished object—venerated, quoted, and used to close a dispute. A learner can be corrected. A teacher can be answered. The man who continues to work can change his mind. By declining the title, Confucius leaves his own words exposed to the contact through which they might remain alive.",
        "Later centuries promoted him title by title and enlarged the temples. Each honor may express real gratitude. Together they risk hiding the person who answered praise with childhood poverty and ‘How would I dare?’ The irony is not that Confucius failed to become a sage. It is that a man who kept refusing the completed position became most famous as the completion itself.",
    ],
    "four-answers-on-filial-care": [
        "‘Do not disobey’ is often cited as the Confucian definition of filial conduct. In the Analects, those words are the beginning of a conversation, not its end. Meng Yizi asks about filiality and receives the compressed answer. Later Confucius raises the exchange while Fan Chi is driving. Fan Chi asks what it meant. Confucius explains: while parents live, serve them according to ritual; after death, bury and sacrifice according to ritual. What must not be violated is ritual, not every parental wish.",
        "The listener matters. Meng Yizi headed one of Lu’s powerful hereditary houses, families notorious for using ceremonies reserved for higher ranks. ‘Do not overstep’ is a well-aimed warning to that man. His own father had entrusted him to Confucius to learn ritual. Fan Chi lacks this background, so the short answer needs opening. Without Fan Chi’s follow-up, later readers would possess two dangerous floating words.",
        "Three adjacent questions make the method visible. Meng Wubo, the next generation of the same family, is told to let his parents worry only about illness—everything reckless within his control should cease to trouble them. Ziyou is told that providing food is not enough; animals are also fed, and human care requires respect. Zixia, diligent and service-minded, is told that performing tasks and serving food is the easy part; the difficult part is the expression on one’s face.",
        "These are not four fragments of a definition waiting to be assembled. They are four interventions aimed at excess, recklessness, reduction to maintenance, and reduction to chores. None simply says ‘obey.’ Elsewhere Confucius explicitly tells children to remonstrate gently when parents are wrong. Remonstration is not obedience; it is a form of relationship that refuses both abandonment and surrender of judgment.",
        "The editors place the four replies beside one another without explaining away their difference. That arrangement is itself a lesson: filial care is not a rule applied identically to everyone. It begins by seeing who is asking, what relation is already present, and where that relation is in danger of becoming empty.",
    ],
    "three-answers-on-ren": [
        "If ren is the center of Confucius’s thought, we might expect its clearest definition. Instead, three students ask about it at the beginning of one chapter and receive answers of strikingly different scale. Yan Hui is told to master himself and return to ritual; when he asks for particulars, he receives four boundaries: do not look, listen, speak, or act contrary to ritual. The positive contents remain his to judge.",
        "Zhonggong, whom Confucius considered capable of governing, receives a public ethic: meet others as honored guests, employ people as though conducting a great sacrifice, and do not impose what you would reject yourself. The answer addresses the danger carried by someone who will exercise power. Ren appears here not as inward serenity but as the manner in which another person enters one’s decisions.",
        "Sima Niu, quick and profuse in speech, receives only this: the person of ren is hesitant in speaking. He objects—is hesitation all ren means? Confucius points to the difficulty of doing what words promise. The brevity is the prescription. A fuller definition would let a man whose trouble is speech acquire still more words.",
        "The three replies are not a survey of ren’s components. They are medicines for three people. The book even records whether each answer lands: Yan Hui and Zhonggong undertake the teaching; Sima Niu asks in disbelief. A fitting intervention need not produce immediate satisfaction, and the teacher does not change it merely to make the learner feel served.",
        "‘To love people,’ the phrase later treated as the definition, is also an answer to a named person—Fan Chi—and not even his only answer. At other times he is told to put difficulty before reward or to practice respect and fidelity in ordinary conduct. If ren concerns treating people as people, a single formula delivered without regard for difference would already betray it. The absence of a standard answer is not a hole in the teaching. It is evidence of what the teaching sees.",
    ],
    "defending-guan-zhong": [
        "Guan Zhong served Prince Jiu in a succession struggle. When Jiu lost and was killed, his colleague Shao Hu died with him. Guan Zhong did not. He entered the service of the victor, Duke Huan, and became the architect of Huan’s power. By a morality that makes loyalty to one lord absolute, the verdict is easy: traitor.",
        "Zilu brings that verdict to Confucius. Guan Zhong failed to die—was he not deficient in ren? Confucius changes the scale. Duke Huan repeatedly assembled the lords without resorting to war, and that was Guan Zhong’s achievement. ‘Such was his ren! Such was his ren!’ Zilu asks about fidelity to one man; Confucius answers with the people spared by an alternative to war.",
        "Zigong later presses the same case. Confucius points again to consequences: Guan Zhong ordered the realm, and people still benefited from his work. Without him, their culture might have been overwhelmed. Must he imitate an ordinary man or woman who keeps a small pledge by strangling himself unnoticed in a ditch? The harsh comparison rejects the idea that dying is automatically the purest proof of principle.",
        "This is not hero worship. Confucius criticizes Guan Zhong elsewhere for smallness of capacity and ritual extravagance. He neither lets public achievement cleanse every fault nor lets one fault erase a work that protected many lives. Judgment remains plural and specific.",
        "The painful coda lies with the questioners. Zilu later dies amid Wei’s political violence, preserving his ceremonial cap at the end; Zigong’s diplomacy helps save Lu. One carries fidelity to death. The other achieves something closer to the outcome Confucius praised in Guan Zhong. The lesson did not mechanically determine either life. It placed another measure in the room: do not ask only whom a death honors. Ask whom an action allows to live.",
    ],
    "why-he-laughed-at-zilu": [
        "The longest scene in the Analects begins casually. Four students are sitting with Confucius. He asks them to forget that he is older and say what they would do if someone truly recognized their abilities. Zilu immediately promises that within three years he could give courage and order to a war-pressed state. Confucius smiles.",
        "Ran You offers to make a smaller territory prosperous and leaves ritual and music to a better person. Gongxi Hua says he would like to learn the modest role of an assistant at ceremonies. Zeng Dian sets down his zither and imagines a spring day: bathing in the Yi, taking the air at the rain altar, returning home in song with adults and children. Confucius sighs, ‘I am with Dian.’ That line has often been read as his final preference for contemplative freedom over political service.",
        "But the conversation continues. After the others leave, Zeng Dian asks why the teacher laughed at Zilu. Confucius answers exactly: governing requires ritual, and Zilu’s manner lacked deference. The problem was not the wish to govern; it was the way he rushed forward and promised command. Confucius then affirms that Ran You’s and Gongxi Hua’s ambitions also concern government, and treats their modest formulations as larger than they sound.",
        "‘I am with Dian’ therefore need not cancel the first three aspirations. Confucius has invited each person to speak without forcing the answers into a ranking. Zeng Dian’s scene may move him personally; it may also exemplify the ease and shared life good government hopes to make possible. Either way, the teacher does not announce a winner and convert the conversation into four models of worth.",
        "The clue is his opening: do not take my age and position as a reason to hold back. A teacher who begins by lowering the hierarchy, listens to four different lives, and later explains one precise smile has done something more interesting than select the most poetic answer. He has made a room where ambition can become speakable—and therefore answerable.",
    ],
    "knowing-it-cannot-be-done": [
        "By conventional measures Confucius’s political career failed. He held office briefly, left under pressure, travelled for years, and found no ruler prepared to use him as he hoped. He knew the pattern. He lamented the absence of auspicious signs and said that no one understood him. A gatekeeper, probably sympathetic to reclusion, condensed the life into a taunt: ‘Is that the man who knows it cannot be done and yet does it?’",
        "The sentence survived because the students heard more than ridicule in it. ‘Knowing it cannot be done’ is not ignorance of probability. Confucius can count. The difference lies in what the count is allowed to decide. One way of acting first asks whether success is likely and proceeds only if the answer is favorable. Another first asks whether the act is called for and lets success remain a separate question.",
        "This is not permission to use any means for a righteous end. When an ally offers to kill a slanderer who has influenced the Ji family, Confucius refuses. Whether the Way advances is larger than that man; murder will not preserve it. The end does not purify the instrument. ‘And yet he does it’ remains bounded by what one may rightly do.",
        "Confucius describes the inner discipline differently: do not resent heaven, do not blame people; learn from below and reach upward. Resentment shuts the door through which another person might still teach you. Blaming fate turns failure into a reason to stop. He does not require this posture of everyone. He tells Zigong how he himself continues.",
        "The gatekeeper measures a life by arrival and finds absurdity. The disciples preserve his line and effectively answer: yes, that is our teacher. A political project can fail without making every act within it wasted, just as an achieved project can be wrong. The durable question is not whether Confucius secretly expected to win. It is which actions remain necessary after hope of winning has gone.",
    ],
    "four-refusals": [
        "Schoolbook contrasts make Confucius the active moralist and Laozi the apostle of withdrawal. One compact observation by the disciples complicates the picture. Confucius, they say, put an end to four things: conjecture, insistence, rigidity, and self-centeredness. The highest cultivation they record is composed entirely of refusals.",
        "The four terms describe stages of one movement. A person forms an idea before the matter is clear; converts it into what must be so; clings once the world resists; and finally makes the self the measure by which everything else is judged. Confucius refuses to place a finished frame in front of a living person or event and then confuse the result with knowledge.",
        "The observation matches his practice. He does not volunteer a universal account of ren. He calls himself empty and works from the question brought to him. He refuses to name the single thread running through his way. To Yan Hui he gives negative boundaries rather than a positive inventory. What he withholds from students, he first withholds from himself: the right to decide the contents before the encounter.",
        "‘No self’ here does not mean erasing one’s personality or abandoning conviction. It means refusing to use one’s own standpoint as a mold into which other people must fit. Without that refusal, individualized answers would be impossible. Everyone would become a better or worse instance of the teacher’s prior categories.",
        "Confucius acts throughout his life; the four refusals do not make him passive. They distinguish action from premature closure. Laozi’s warning that a way fully spoken is not the constant way comes from another project and need not be made identical. But both traditions know a danger that the easy contrast between action and nonaction misses: the most forceful interference may begin long before our hands move, when a frame hardens and the person before us disappears inside it.",
    ],
    "transmit-not-compose": [
        "A founder who wrote no book is an odd figure in intellectual history. The Analects was assembled by students and later hands. Confucius says, ‘I transmit; I do not compose. I trust and love the old.’ The familiar reading turns this into a charter of conservatism: his virtue was preserving antiquity rather than creating anything new.",
        "The old he loved was not exempt from evidence or change. He admits that the records for reconstructing Xia and Shang ritual are insufficient. He traces how one dynasty modified the rites of another and expects later ages to modify Zhou. Elsewhere he rejects rigidity and warns that the young may surpass the old. ‘Loving the old’ cannot by itself mean freezing it.",
        "This series reads his refusal to write through the structure of his teaching. In a room, Confucius can ask who has brought the question, wait for readiness, offer one corner, stop, or give opposite advice to people who need opposite movement. A book cannot see its reader. It says the same sentence to Zilu and Ran You. A prescription aimed at a person becomes a general drug once detached from the encounter.",
        "On this reading, ‘transmitting’ means keeping available the materials—poetry, history, music, ritual—from which a present response can be composed. ‘Not composing’ means declining to seal those responses into one formula for everyone. This is an interpretation, not a claim that writing is intrinsically corrupt. Plato wrote dialogues partly to preserve questioning inside text. Every writer may invent other defenses against closure.",
        "Confucius’s defense failed in an instructive way. His students wrote; later readers removed names and occasions; the living prescriptions became smooth sayings. ‘I transmit; I do not compose’ itself became a maxim against innovation. Yet the recorders also preserved enough roughness to reverse the process. Because they wrote ‘Zilu asked,’ ‘Zai Wo replied,’ and ‘the Master smiled,’ the room can still be reopened.",
    ],
    "people-may-follow": [
        "Few lines have done more damage to Confucius’s reputation than the usual rendering of Analects 8.9: ‘The people may be made to follow; they may not be made to understand.’ Defenders and critics often accept the same syntax. One uses it to justify secrecy; the other cites it as proof that Confucian government begins in keeping subjects ignorant.",
        "The difficulty is that this Confucius would contradict nearly everything the book shows him doing. He teaches across social distinctions, treats ordinary questioners as capable of pursuing an issue from both ends, says human natures are close, and makes public trust a condition of political standing. The man who opens learning broadly would suddenly declare knowledge unavailable to most people.",
        "Another reading turns on the causative verb. The line need not mean ‘do not let them know.’ It can mean that people may be guided along a way, but cannot be made to possess someone else’s understanding. Knowledge cannot be installed by command. Cheng Yi already distinguished inability from prohibition here. The Guodian text *Zun deyi* offers an important parallel: people may be guided, but not coerced.",
        "This fits the classroom. Even Yan Hui cannot be made to know before his own question reaches the proper heat. A ruler has still less claim to pour a state-approved mind into an entire population. The limit belongs not to the people’s intelligence but to political power: guide conduct where necessary; do not confuse rule with authorship of another person’s understanding.",
        "The textual and grammatical history is genuinely contested, and this essay does not pretend to close it. Its claim is methodological: a translation that makes Confucius the founder of obscurantism must be tested against the people to whom he speaks and the practices the book attributes to him. Before using the sentence either as accusation or permission, restore its implied subject. Who is doing the ‘making,’ and what power do they imagine they possess?",
    ],
    "virtue-and-shame": [
        "Analects 2.3 is commonly taught as the charter of Confucian rule by virtue: guide people with regulations and punishments and they will avoid penalties without shame; guide them with virtue and order them through ritual and they will develop shame and become upright. Law manages behavior, on this reading; moral education transforms character.",
        "This series proposes a deliberately revisionary reading, and the caution belongs at the front. The chapter is addressed to rulers. Throughout *Wei zheng*, the recurring demand is that the person governing first govern himself. The verbs here also run from ruler to people. The question, then, is not simply whether shame is good. It is what happens when a ruler sets out to produce shame inside other people.",
        "Elsewhere Confucius praises *xing ji you chi*: in one’s own conduct, having a sense of shame. That shame belongs to the agent’s judgment. State-manufactured shame is different. It can become an internal policeman speaking in an official voice. On the proposed reading, clear law and punishment establish a boundary while leaving life within it open; moralizing rule fills that open field with prescribed feelings and blocks movement.",
        "This reverses the traditional valuations of several words, especially *chi* and *ge*. It has no manuscript variant that compels acceptance. Its support is structural: Confucius tells rulers to correct themselves, warns against imposing knowledge on people, and expects influence to follow example without constant command. ‘Govern by virtue’ praises the ruler’s own stance; ‘guide them with virtue’ may name the danger of using that stance as content to be installed in others.",
        "The reader should keep both interpretations in view. A new reading does not become true because it is morally attractive, and two thousand years do not settle a sentence by seniority alone. What the revision makes visible, even if one rejects it, is a question modern institutions still face: which parts of our shame grow from judgments we can own, and which were placed inside us so early that obedience feels like conscience?",
    ],
    "boundaries-not-checklists": [
        "‘Do not look, listen, speak, or act contrary to ritual.’ The four prohibitions given to Yan Hui can sound like the purest expression of a culture that regulates every movement. Their grammar suggests another possibility. They tell him where not to go. They do not tell him what he must see, hear, say, and do within the boundary.",
        "The difference between a fence and a floor plan matters. Yan Hui asks for particulars after hearing that ren requires mastering himself and returning to ritual. Confucius gives the strongest student negative limits, not a positive script. Within them, perception and action still require judgment. A detailed inventory would decide his life for him; a boundary leaves him responsible for it.",
        "Later interpreters understandably wanted more. Cheng Yi’s four admonitions turn the prohibitions into positive guidance about correct looking, listening, speaking, and acting; Zhu Xi places them beside the passage. Such lists may be wise. But once treated as the exhaustive answer, scaffolding becomes architecture and the learner’s remaining judgment becomes compliance.",
        "The Analects itself contains a useful contrast: the ‘nine considerations’ tell the cultivated person what to think about when seeing, hearing, speaking, becoming angry, or encountering gain. The list may remind a novice of dimensions otherwise missed. Its problem is not that it is positive or organized. A checklist becomes dangerous only when it claims completeness, immunity from revision, or the power to replace attention to this case.",
        "Negative rules are not automatically liberating; ‘do not’ can also become an iron cage. Positive advice is not automatically colonial; it can be questioned, adapted, and discarded. The deeper test is whether guidance returns judgment to the person using it. Confucius’s four refusals leave an open field. Later readers should be careful not to praise the fence while quietly paving everything inside it.",
    ],
    "let-the-ruler-be-a-ruler": [
        "‘Let the ruler be a ruler, the minister a minister, the father a father, the son a son.’ These eight Chinese characters are often placed near the foundations of hierarchical Confucian order. Yet the sentence is not delivered by a sovereign to his subjects. Duke Jing of Qi asks Confucius about government, and Confucius begins with the ruler.",
        "Each repeated word moves from position to responsibility: a ruler must do what makes the title real; the same applies to minister, father, and son. The line does not rank their human worth. It asks whether the person occupying a role performs its obligations. Duke Jing hears it that way. His first worry is ‘if the ruler is not a ruler’—if he himself fails—before he considers everyone below him.",
        "The answer is fitted to Qi. Duke Jing’s household and succession were unstable, while the Chen clan steadily absorbed political power. Titles and realities were separating. The prescription ‘be a ruler’ does not grant the duke more arbitrary control. It tells him that the name on his place cannot do the work for him.",
        "Later doctrine can reverse the direction. A demand spoken to the ruler becomes an order spoken to ministers: know your place and obey. But Confucius elsewhere gives obligations to both sides—rulers employ ministers through ritual, ministers serve with integrity—and defines a great minister as one who serves by the Way and leaves when that cannot be done. Zilu is told not to deceive a ruler, but to oppose him to his face.",
        "The first word therefore remains decisive. A role that carries power carries the first burden of becoming truthful. If the ruler is not a ruler, ‘the minister must be a minister’ cannot repair the relation by demanding more submission. Before quoting the line downward, return it to the person sitting opposite Confucius. He asked how to govern and was told, first, to deserve his own name.",
    ],
    "correcting-names": [
        "Asked what he would do first if entrusted with government in Wei, Confucius answers: rectify names. Zilu immediately calls him pedantic. Why begin with language when the state has urgent work to do? The student’s impatience has remained persuasive because ‘correcting names’ sounds like policing titles while reality burns.",
        "Wei’s crisis makes the answer less abstract. The former heir Kuai Kui had fled; his son Zhe occupied the throne; the father returned to claim it, and the two sides struggled over a state. Who was ruler, by what title and right, was not a nicety. People were being asked to act inside a conflict whose fundamental positions could not be truthfully stated.",
        "Confucius’s famous chain runs from incorrect names to disordered speech, failed affairs, damaged ritual and music, unjust punishment, and finally people who do not know where to put hand or foot. The destination is not efficient control of the population. It is the bewilderment suffered by people when official language and actual power no longer meet.",
        "The extended chain may show editorial elaboration; Confucius’s speech elsewhere is usually less schematic. But three points fit the person already visible: put the root position right, leave what you do not know open, and do not speak carelessly. Rectifying names asks who is doing what and by what authority before action disguises itself as necessity.",
        "Zilu later dies in the very disorder of Wei. That fact should not be used to claim that one linguistic reform would have saved him. It does show why the argument was not wordplay. When a public institution cannot say truthfully who occupies its offices, whose command is valid, or what act is being demanded, bodies eventually carry the contradiction that language tried to postpone.",
    ],
    "study-then-office": [
        "‘Study well and you will become an official’ is one of the most durable summaries of the Confucian career. The phrase is attributed to the Analects and placed behind centuries of examination culture. Two small repairs change it. Zixia, not Confucius, says it; and he says two balanced clauses, not one.",
        "The whole line reads: when public service leaves surplus capacity, study; when study leaves surplus capacity, enter public service. Here *you* means room or capacity, not superior grades. Work should not end learning, and learning should not become a refuge from doing. The movement runs in both directions.",
        "Later citation cuts away the first half and changes the sense of one word. The result is a one-way escalator from education to office. The missing clause is inconvenient to those already in power: it sends officials back to study rather than promising students advancement. Nothing must be forged. Selection alone remakes the sentence.",
        "Zixia gives learning a different destination elsewhere. Craftspeople remain in their workshops to complete their work; the cultivated person studies in order to reach the Way. Confucius similarly contrasts older learning ‘for oneself’ with learning performed for the eyes of others. On that account, office may become one field in which learning acts, but it cannot be learning’s final certificate.",
        "The complete pair remains good advice. People immersed in work need study that can interrupt habit; people immersed in study need encounters with consequence. The warning concerns what happens when a relation is edited into a pipeline. Whenever a famous sentence fits an institution too perfectly, look beside it. The other half may have been making a demand the institution preferred not to hear.",
    ],
    "thinking-without-office": [
        "‘When you do not occupy a position, do not plan its government’ now functions as an elegant way to say: this is none of your business. Lacking the office becomes lacking the right to think or speak. The sentence appears twice in the Analects, once followed by Zengzi’s gloss that a cultivated person’s thoughts do not go beyond his position.",
        "This series reads Confucius’s *mou qi zheng* more narrowly: do not take over the planning and decision that belong to another office. It is a limit on acting in someone else’s place, not on forming a judgment. That reading fits other instructions to let responsible officers act first and to make roles answer for their own work.",
        "It also fits Confucius’s life. He spent long periods outside office while thinking and speaking about government. He challenged Ran You over the Ji family’s sacrifice, formally petitioned against a political murder after retirement, criticized rulers, and answered questions about statecraft. If the saying prohibited thought and criticism, its first conspicuous violator would be its speaker.",
        "Zengzi’s adjacent sentence moves from planning to thought. The shift may be sincere, and he signs it with his own name. But it creates a route by which a boundary against usurping another’s agency becomes a boundary around the mind itself. Later authority can merge the two and call exclusion from power a reason for silence.",
        "Hands can cross a line that thought does not. I may not make your decision for you, yet I can question it, advise, protest, and refuse participation. Indeed, preventing such judgment makes accountable office less likely. When someone quotes ‘not in the position’ to end discussion, ask what they are protecting: the other person’s authority to decide, or the officeholder’s wish never to be answered?",
    ],
    "detesting-the-fixed": [
        "Confucius is often treated as conservatism personified: lover of antiquity, transmitter rather than author, restorer of Zhou. An older man named Weisheng Mu confronts him from another angle. Why is he forever bustling from place to place—perhaps showing off his eloquence? Confucius gives a two-word answer: ‘I detest rigidity.’",
        "The reply does not establish a modern progressive Confucius. It does expose a problem with the easy portrait. The disciples say he refused rigidity among four fundamental errors. He warns that later generations may surpass the present. Comparing different recluses, he distinguishes himself by having no predetermined ‘must’ and no predetermined ‘must not.’ A conservative icon keeps announcing that fixedness is the danger.",
        "His attraction to Zhou is reasoned. Zhou observed the two preceding dynasties and produced a rich culture through inheritance and revision. He follows what he judges the strongest available achievement, not whatever happens to be oldest. He also says that rites change through additions and subtractions and refuses to reconstruct ancient practices where evidence is insufficient.",
        "A similar edit turns his contrast between ancient and current learners into nostalgia. The full sentence gives the criterion: earlier learners studied for themselves; current learners study for the recognition of others. ‘Ancient’ is praised because of the direction of learning, not because age sanctifies it. Remove the reason and only a preference for the past remains.",
        "The restless traveler whom Weisheng mocks refuses one more fixed form: withdrawal. Confucius does not believe that seeing a damaged age obliges everyone to hide. He moves because the judgment must be made again in each place. The deepest irony may be that later ages made a guardian of immobility from someone who explained his motion with ‘I detest the fixed.’",
    ],
    "danger-of-must": [
        "‘Always keep your word and carry every action through’ sounds like unimpeachable Confucian advice. When Zigong asks how to recognize a *shi*, however, Confucius places precisely this character at the bottom of his ranking: the person who insists on keeping every word and completing every act is hard and clattering like a stone—a petty person, though perhaps still of the lowest rank.",
        "The trouble is not trustworthiness but the word ‘always.’ Circumstances change; promises conflict; new knowledge reveals that the act itself is wrong. A rule of automatic completion turns off the faculty by which fidelity should be judged. The result may be dependable in a narrow sense and destructive in a larger one.",
        "Confucius makes the same distinction when defending Guan Zhong. Dying for one defeated claimant would have displayed small fidelity. Living to build an order that spared many from war could count as ren. Elsewhere the disciples describe him as having no fixed must and no fixed must-not, aligning action instead with what is right in the case.",
        "Later lists of cardinal virtues can detach *xin*, trustworthiness, from the relations in which it operates and make it an absolute item. But Confucius’s teaching joins texts, conduct, wholeheartedness, and trust; it does not place promise-keeping beyond judgment. Intelligence is not a competing virtue ranked somewhere else. It is the eyesight without which ren and fidelity can be commandeered.",
        "A person who never breaks a promise is easy to praise because the rule is visible. The harder person must sometimes explain why keeping this promise would betray what made promises valuable at all. That explanation can become an excuse, so it needs scrutiny. But eliminating scrutiny in favor of ‘I said it, therefore I must’ is not integrity perfected. It is a stone striking stone.",
    ],
    "negative-golden-rule": [
        "Zigong asks for one word he might practice throughout life. Confucius answers tentatively: perhaps *shu*, reciprocity—‘What you do not desire, do not impose on others.’ The sentence is often called a negative Golden Rule and compared unfavorably with the positive instruction to give others what you would want yourself.",
        "Its negative form protects a crucial asymmetry. Because the other person is human like me, I can begin from the knowledge that coercion, humiliation, and injury I reject are likely to matter to them. But because they are another human rather than a copy, I cannot conclude that what I enjoy, admire, or seek must also be their good.",
        "The positive rule can therefore overreach in the name of generosity. I offer the career I wanted, the food I love, the faith that consoles me, or the intervention I would welcome, and treat good intention as consent. The gift’s contents come from my life; the recipient’s answer disappears. A negative boundary makes less dramatic promises, but it leaves the interior open.",
        "Confucius also says that one who wishes to stand should help others stand, and one who wishes to reach should help others reach. That is not the same as deciding where they must stand or what destination counts as arrival. It concerns the capacity to become an agent, not the program that agency must pursue.",
        "A universal rule capable of travelling through very different lives may have to be thin in this way. Any rich positive content will eventually meet someone for whom it is wrong. ‘Do not impose’ does not complete ethics; it makes ethical relation possible by ensuring that the other person is still there to answer. Before doing someone a good turn, the neglected part of the Golden Rule is a question: did they ask for this good?",
    ],
    "scolding-yuan-rang": [
        "‘Old and not dead—a pest.’ Detached from its scene, the phrase can be used as Confucius’s warrant for contempt toward the elderly. The full passage is almost comically specific. Yuan Rang sits sprawled with his legs apart, waiting. Confucius recounts this one man’s life—disrespectful when young, leaving nothing worth recounting when grown, and now old without changing—then taps him on the shin with his staff.",
        "Yuan Rang was not an anonymous old man. Other records portray him as a lifelong friend eccentric enough to sing while Confucius helped prepare his mother’s coffin. Asked why he remained associated with such a person, Confucius replied that family remains family and old friends remain old friends. The insult belongs to decades of intimacy and exasperation.",
        "Its three clauses form a miniature biography. Childhood, adulthood, and the present posture are joined into one rebuke. The tap matters too. This is not a judicial sentence pronounced over a social class. It is one elderly friend prodding another’s leg and saying, in effect, you have really remained yourself to the bitter end.",
        "To manufacture the proverb, no word needs to be altered. Remove Yuan Rang’s name, his posture, the first two clauses, the staff, and the relationship. What remains sounds universal. A remark that only these two people could fully hear becomes a judgment delivered by a sage against everyone who shares one trait with its target.",
        "The recorders preserved all the details required to resist that transformation. Readers performed the deletion. This small passage offers a clean model of how living speech becomes cruelty: first erase whom it was for. Whenever a severe quotation arrives with ancient authority, restore the missing ordinary questions. Who was present? What had happened between them? And would these words have been spoken to a stranger?",
    ],
    "empty-ritual": [
        "The phrase ‘man-eating ritual’ belongs to a modern indictment of Confucian social order, and the historical indictment has ample material. The temptation is to treat every concern with *li*—ritual, form, propriety—as one more brick in the same machine. Yet the chapter of the Analects most devoted to ritual opens by attacking ritual emptied of humaneness.",
        "The Ji family uses a royal dance formation; great houses close ceremonies with music reserved for the sovereign. Confucius asks: if a person lacks ren, what can he have to do with ritual? What can he have to do with music? Correct performance cannot generate its own moral core. Without regard for persons, form becomes an impressive shell.",
        "When Lin Fang asks for the root of ritual, Confucius praises the question but points rather than defines. In ceremony, prefer frugality to extravagance; in mourning, prefer genuine grief to flawless management. Jade and silk do not constitute ritual, any more than bells and drums constitute music. Delegating a sacrifice does not delegate the presence by which it means anything.",
        "His own practice distinguishes change in form from loss of relation. He accepts a cheaper material for the ceremonial cap because respect survives the economy. He refuses a fashionable change in where one bows because it removes the humility the gesture expresses. Tradition and majority each yield to judgment about the human meaning carried by the form.",
        "A ritual order becomes predatory when it preserves the outside, strips away ren, and then uses the shell to discipline people. That order can quote Confucius, but it also stands under his opening question: without humaneness, what has it to do with ritual? The useful test for any rule, ceremony, or inherited custom is not merely whether it has been performed correctly. It is whether a person remains visible inside it.",
    ],
    "three-opening-questions": [
        "The opening of the Analects is so familiar that its punctuation disappears: learn and practice in due time—is that not a pleasure? Have friends arrive from afar—is that not a joy? Remain unresentful when others do not recognize you—is that not the cultivated person? These are not three declarations. They are three questions.",
        "The repeated construction, ‘is it not … ?’, invites assent but does not manufacture it. Someone opposite the sentence still has to answer. Once the question marks are mentally removed, an invitation becomes an instruction: review your lessons, welcome friends, control resentment. The first loss in reading the Analects may therefore be formal rather than doctrinal—the place reserved for a listener vanishes.",
        "The verb conventionally rendered ‘review’ is richer than returning to notes on a timetable. Its early image is associated with a bird repeatedly trying its wings. Learning is followed by practice, rehearsal, and enactment. Pleasure arrives when knowledge begins to fly, not merely when information is revisited.",
        "The final question runs deepest. Confucius returns throughout the book to anxiety about being known: do not worry that others fail to know you; become worthy of being known. The cultivated person does not require an audience in order to stand. Recognition can bring genuine joy, as the arriving friends do, but its absence need not become the author of one’s value.",
        "The three questions can be read as a small ascent: the pleasure of practice within oneself, the joy of resonance with another, and the steadiness that survives when no one arrives. The text never labels the steps. It lets the reader discover—or refuse—the pattern. Before the Analects presents a teaching, it has already shown how teaching might speak: as something awaiting an answer.",
    ],
    "neither-curse-nor-kneel": [
        "After thirty-one essays, a recognizable person has emerged: a teacher who waits for questions, gives different answers to different people, leaves corners unfinished, welcomes correction, permits Zai Wo to act against his judgment, refuses sagehood, and tells students not to yield even to a teacher where ren is concerned. Then the Analects contains statements that seem to build the opposite world.",
        "One passage appears to divide unchangeable superior wisdom from unchangeable inferior stupidity. Another ranks ways of knowing. One tells the cultivated person to fear great men and the words of sages. The final chapter can support a lineage running from ancient kings toward an authorized succession. The most notorious sentence generalizes about women and petty people.",
        "Two familiar responses share an assumption. Devotion says that because Confucius said these words, they must be right and our discomfort must yield. Rejection says that because the words are in his book, they expose the real Confucius and discredit everything else. Both make attribution settle judgment.",
        "This reading takes a narrower path. It does not claim manuscript evidence capable of assigning or deleting these sayings. It asks what each sentence establishes and whether that structure fits the person reconstructed from repeated scenes. Hierarchy, immunity from questioning, exclusive lineage, and categorical exclusion conflict with practices that keep teaching open and judgment alive. That conflict can be named without pretending to solve the textual history.",
        "Not every passage that fails as an anchor deserves opposition. A checklist may contain excellent advice while revealing no occasion or listener. A record of clothing may be accurate while failing to disclose judgment. The two questions must remain separate: can this passage help us know this person, and should the structure it supports be accepted? The next essays neither wash the text clean nor kneel before it. They keep the seam visible.",
    ],
    "the-chapter-next-door": [
        "‘Human natures are close; practice makes them diverge.’ Beside that open sentence stands another: ‘Only the highest wise and the lowest foolish do not change.’ The first makes difference a history. The second can be used to install exceptions at both ends, including a class of people for whom education is futile.",
        "Nothing in the first sentence must be edited for the second to narrow it. Add one neighboring qualification and ‘natures are close’ becomes ‘except at the top and bottom.’ ‘In teaching there should be no classes’ becomes ‘except for those already judged unteachable.’ An open door acquires an invisible admissions policy.",
        "That use conflicts with the scenes. Confucius receives a young person from Huxiang, a place considered difficult to speak with, and rebukes students who distrust the visitor. Approve the person’s coming forward, he says; do not endorse everything behind him, but do not refuse the attempt to enter. When Ran You says he lacks strength, Confucius accuses him not of incapacity but of drawing the line in advance.",
        "The contested sentence need not have only one sense. ‘Not changing’ might describe extreme stability rather than an innate caste, and the historical speaker cannot be settled here. What this essay opposes is the application that uses it to license abandonment: some kind of person cannot learn, so no teacher need try.",
        "People are genuinely different; otherwise teaching according to the person would be meaningless. But difference calls for different approaches, not different eligibility for being treated as a learner. Difference does not authorize rank. When the neighboring line is used to close the door opened by ‘no classes,’ the closure is the reader’s action and should be judged as such.",
    ],
    "difference-without-rank": [
        "One passage sorts knowing into four levels: those born knowing are highest; those who learn come next; those driven by difficulty to learn come after; those who meet difficulty and still do not learn are lowest. The observation begins with a real difference. People acquire understanding at different speeds and under different conditions.",
        "An earlier version of this argument objected that Confucius calls himself someone who learned rather than someone born knowing, and therefore could not rank innate knowledge highest. That objection was invalid and has been withdrawn. He could deny belonging to a category while believing the category superior. A desired conclusion does not rescue a bad inference.",
        "The stronger question concerns the movement from descriptions of learning to grades of people. ‘Born knowing,’ ‘learning to know,’ and ‘learning under pressure’ name routes. ‘Highest,’ ‘next,’ and ‘lowest’ can convert those routes into human standing. Once that conversion is accepted, withholding effort and opportunity begins to look rational.",
        "Confucius’s practice runs the other way. Students differ, so he gives Zilu and Ran You opposite pushes. Learners ask about ren from different positions, so each receives a different answer. Difference is the reason to teach responsively. It is not a warrant to reduce anyone’s status as a person or cancel the offer of teaching.",
        "The passage’s list-like form and lack of occasion also make it a poor anchor for reconstructing the teacher in the room. That does not prove it false or worthless. It establishes the limit of the claim made here: do not use differences in how knowledge is acquired to rank whose life counts, and do not call a pedagogical surrender an insight into natural hierarchy.",
    ],
    "defy-the-teacher": [
        "The ‘three fears’ are neatly arranged: the cultivated person fears Heaven’s command, great men, and the words of sages; the petty person understands none of these, treats the powerful casually, and insults sage speech. The passage has offered later readers a compact architecture of deference.",
        "The three objects should not be collapsed. Awe before Heaven can name a limit between what one can and cannot control. Confucius works without guaranteeing success and refuses to blame fate for failure. Respect for a person of genuine responsibility or for words tested by generations can also be intelligent. Serious attention is not servility.",
        "But when fear of great men means that office exempts its holder from challenge, the line conflicts with Confucius’s practice. He tells a minister to serve by the Way and leave when that becomes impossible. He tells Zilu to avoid deceiving a ruler yet oppose him directly. He calls a sovereign’s delight in being uncontradicted a route toward political ruin.",
        "Fear of sage speech becomes still harder to reconcile when it means immunity from reasons. Confucius asks students not to yield to their teacher in matters of ren, complains that Yan Hui agrees with everything, announces Ziyou’s correction to the class, and refuses the title of sage for himself. The teacher repeatedly removes the very shield later reverence places around him.",
        "This essay does not determine who composed the list or deny that ‘fear’ can mean weighted respect. It opposes a particular use: authority may not turn ‘take this seriously’ into ‘you may not ask why.’ A sentence worthy of reverence should survive questions. If questioning it is already defined as disrespect, reverence has become a device for protecting the sentence from judgment.",
    ],
    "later-lineage": [
        "The final book of the Analects opens without ‘The Master said.’ Instead, Yao addresses Shun, Shun passes a charge to Yu, Tang accepts blame for the realm, Zhou honors worthy people, and a concise program names people, food, mourning, and sacrifice as priorities. Its language resembles proclamations more than remembered classroom conversation.",
        "Much of the content is admirable. Rulers take fault upon themselves rather than pushing it downward. Ordinary people come first. Extinct states and broken lines are restored; overlooked talent is raised. These are close to the demands Confucius repeatedly places on those who govern.",
        "The risk lies in what the sequence can be made to establish. Yao, Shun, Yu, Tang, Zhou—and then, by the book’s placement, Confucius—become a chain of authorized transmission. Later accounts extend the line into a ‘succession of the Way,’ sometimes with a secret formula passed intact from holder to holder.",
        "Once lineage becomes the criterion, the question ‘is this right?’ slides toward ‘who transmitted it?’ Insiders inherit authority; outsiders become heterodox. Yet Confucius says people enlarge the Way, not the Way people. He refuses sagehood, declines to seal his teaching in a doctrine, and leaves the unifying thread unnamed. A man who will not found an esoteric transmission becomes the indispensable link in one.",
        "Remembering ancient rulers is not the same as asserting an exclusive orthodoxy, and the passage need not itself complete that move. This essay does not reject its political counsel or claim to know its compiler. It marks a later use: when a genealogy substitutes for judgment, the names of good predecessors have stopped inviting emulation and begun granting jurisdiction.",
    ],
    "women-and-petty-men": [
        "‘Women and petty people are difficult to deal with: draw them near and they become disrespectful; keep them distant and they resent it.’ No line in the Analects is more likely to repel a modern reader. Defensive interpretation offers several exits—perhaps ‘women’ means particular household dependents, perhaps the sentence observes unequal relationships, perhaps the graph should be read differently.",
        "This essay takes neither exoneration nor condemnation by attribution. There is no manuscript basis here for confidently removing the line from Confucius, and its possible meanings cannot be forced into a single charitable one. The sentence remains. So does responsibility for what readers build with it.",
        "What must be opposed is the use that infers women are naturally lesser, generally incapable of cultivation, or properly excluded. That conclusion collides with four clear commitments: human natures are close; teaching admits no class barrier; reciprocity begins from another person’s standing as a person; and Confucius ordinarily judges conduct rather than membership in a category.",
        "An observation about language may register caution without settling history. Elsewhere in the Analects, the same graph commonly transcribes ‘you’; the compound meaning women is isolated here. An isolated usage is not evidence sufficient to rewrite or delete the sentence. It is a reason to resist easy certainty.",
        "The decisive question belongs to readers. When two broad principles—closeness of human nature and teaching without exclusion—stand beside one ambiguous and damaging line, why choose the isolated line to govern the principles? That choice is not dictated by the book. We need not wash the sentence clean, and we need not accept its harshest use. We can leave it visible and write beside it: this categorical judgment does not fit the Confucius reconstructed here.",
    ],
    "five-beauties-four-evils": [
        "Zizhang asks how to enter government. The answer unfolds as a polished inventory: honor five beauties and remove four evils. Benefit people without waste; make demands without provoking resentment; desire without greed; remain composed without arrogance; inspire awe without ferocity. Do not execute without instruction, demand results without warning, issue delayed orders with abrupt deadlines, or become miserly when giving what is due.",
        "The list is excellent administrative counsel. The question is whether it resembles an answer fitted to Zizhang. Elsewhere he appears ambitious, ceremonious, proud, and difficult to join in ren. Greed, coercive command, and bureaucratic stinginess are not the particular weaknesses by which his classmates know him. Of nine items, perhaps composure without arrogance lands directly.",
        "Compare another answer to Zizhang’s question about government: occupy the role without weariness; carry out affairs with wholeheartedness. Eight Chinese characters meet his unstable persistence and attraction to the outward display of office. The short answer contains the questioner. The long checklist contains the topic.",
        "This creates a useful test within the Analects. When a passage says a named person asked, inspect whether the response touches that person. If a generic handout wears the shell of dialogue, the name may be serving only to stage an inherited program as personal instruction.",
        "That judgment does not make the checklist false, late, or harmful. It limits the work it can do. The five beauties and four evils can help an administrator examine practice. They cannot by themselves show us how the teacher listened and answered in a room. Good content and good evidence for a portrait are different questions.",
    ],
    "ji-shi-handout": [
        "The sixteenth book of the Analects sounds different. Its first chapter offers an extended political argument; nearby come sets of three beneficial friendships and three harmful ones, three beneficial pleasures and three harmful ones, three cautions by stage of life, three faults in attending a cultivated person, and nine considerations. The material is orderly, teachable, and curiously ready for slides.",
        "Form is evidence, though not a verdict. Confucius’s strongest scenes are tied to occasions: one student rushes, another hesitates; a ruler asks from a compromised position; a reply stops after a few words. In *Ji Shi*, repeated molds generate successive lists. The same syntax accepts a new subject and produces another complete set.",
        "Its content often fits the broad tradition very well. Choose honest friends, avoid flattering pleasures, distribute resources fairly, govern by culture rather than force—none of this needs opposition. The difference is between a well-arranged handout and a living exchange. A handout can preserve the results of many judgments while hiding how any one was reached.",
        "That loss matters for this reconstruction. Without a person asking, we cannot see whether an answer was medicine, provocation, concession, or boundary. The organized form leaves less room for the hearer to discover the next step and more opportunity to treat the inventory as complete.",
        "Calling the chapter ‘more like notes’ does not assign authorship or falsity. Students and later editors may faithfully systematize a teacher’s orientation. Their work deserves its own reading. It simply cannot replace the encounters through which we recognize this particular teacher. A table may summarize what someone believes; it rarely lets us meet the person deciding.",
    ],
    "two-ways-of-praising": [
        "Two neighboring passages praise ancient rulers. One calls Shun and Yu lofty because they possessed the realm yet did not make it serve private advantage. The reason is compact and visible: power did not become personal appropriation. A reader can inspect why the praise was given.",
        "The next passage praises Yao at greater length: great, lofty, vast, brilliant. He follows Heaven; the people cannot name his achievement; his works and institutions are magnificent. The language rises repeatedly, but no single action anchors the height. Five praises do not necessarily provide one reason.",
        "This contrast is useful because length can disguise thinness. The shorter statement makes a judgment available for judgment. We may ask whether nonappropriation deserves admiration and whether Shun or Yu actually met the description. The longer encomium asks the reader to share awe before knowing what produced it.",
        "Confucius elsewhere praises with a case attached: Guan Zhong spared people from war; Yan Hui kept advancing; a student’s reply corrected his own. The reason may be disputed, but it is present. Praise that supplies a reason treats the listener as someone capable of evaluating the praise. Pure exaltation asks for participation in a mood.",
        "The second passage need not be rejected, declared inauthentic, or denied literary force. It may be ceremonial song rather than analytic speech. It simply offers little evidence for recognizing the teacher whose judgments normally expose their ground. The next time you call someone great, try completing the sentence after ‘because.’ The missing clause is where admiration becomes answerable.",
    ],
    "he-did-not-curse-the-age": [
        "Two sayings in the Analects sound like posts from a disillusioned observer: how difficult it is to escape this age; a ritual vessel is no longer a ritual vessel—what a vessel! They may preserve real grief. What they lack is the feature Confucius’s criticism usually carries: a named person, act, or consequence.",
        "Under hunger in Chen, with followers collapsing, Confucius does not denounce the age. Zilu asks whether a cultivated person can be reduced to such straits; Confucius answers that the cultivated remain steady while petty people become reckless. Surrounded at Kuang, mocked by Weisheng Mu, or blocked by rulers, he speaks to the situation rather than cursing an atmosphere.",
        "His sharpest rebukes are exact. The Ji family uses a royal dance; Zang Wenzhong houses a sacred tortoise with forbidden ornament; Yuan Rang sits improperly after a life Confucius knows. Name, act, and reason let criticism be challenged. ‘The times are rotten’ makes everyone guilty and leaves no one responsible.",
        "The vessel lament may be developed into a doctrine that rulers and ministers no longer match their names. The possibility of misuse is not a reason to condemn the sentence in advance. Preemptive guilt would reproduce the very habit this reading resists. We can mark the opening without pretending it has already been filled.",
        "These sayings are not rejected or assigned to another author. They are simply poor anchors for a portrait of someone whose disapproval usually has an address. General despair can be emotionally true, but criticism becomes accountable when it can answer: who did what, to whom, and what should have happened instead?",
    ],
    "burial-against-his-wishes": [
        "When Yan Hui dies, Confucius loses the student whose progress he had watched most closely. Yan Hui’s father asks him to sell his carriage in order to provide an elaborate outer coffin. Confucius refuses: his own son received only the ordinary coffin. Talent does not change the fact that each father has lost a son, and ritual should not become competitive display.",
        "The disciples nevertheless give Yan Hui a lavish burial. Confucius says it should not have been done, but they do it. His grief then takes an unsettling form: ‘Hui treated me as a father, yet I have not been able to treat him as a son. It was not I; it was those students.’ At the largest moment, the school does not obey its teacher.",
        "Both sides act from something real. Confucius wants Yan Hui treated through ordinary ritual, the same human measure he applied within his own family. The disciples need a visible form large enough to carry admiration and sorrow. Their reverence is sincere. It also overrides the judgment of the person they revere and the ordinary standing of the person being buried.",
        "The funeral becomes a model for a later afterlife. Confucius leaves an opening; a disciple fills it with a formula. He gives prescriptions to persons; followers organize them into lists. He rejects sagehood; admirers build the title higher. Respect repeatedly takes the form of deciding on behalf of its object what honor ought to mean.",
        "Yet the recorders write down the refusal, their disobedience, and the teacher’s reproach. They overrule him and preserve the evidence that they did. This double movement—reverence that covers over, honesty that exposes the covering—will shape the entire book. The first question is not whether love and respect are genuine. It is whether they can still hear ‘do not.’",
    ],
    "zigong-defends-his-teacher": [
        "It is easy to say that the disciples created the saint. Zigong himself once moved in that direction. When an official wondered whether Confucius’s many abilities proved him a sage endowed by Heaven, Zigong agreed. Confucius answered that poverty, not celestial status, had made him learn many practical skills. A compliment became a lesson in how not to praise him.",
        "Later, Zigong repeatedly defends his teacher without making the same mistake. When someone calls him inferior to Confucius, he compares their walls: his own is shoulder-high and lets anyone see the house; the teacher’s is high enough that one must find the gate before discovering the richness within. Difference in access is not difference in species.",
        "When another critic ranks Zigong above the Master, he says a word may reveal intelligence or folly and should not be spoken carelessly; one cannot reach Confucius, just as one cannot climb to the sky by stairs. The image is extravagant, but the defense focuses on the critic’s hasty judgment rather than an official title of sanctity.",
        "His finest account concerns government. A teacher establishes people and they stand; guides them and they move; settles them and they come; sets them in motion and they become harmonious. The verbs remain divided. The teacher supplies conditions and direction. The people perform the actions. No maker claims the finished human beings as his products.",
        "Zigong has learned to defend a teacher’s greatness by describing what happens around him, not by removing him from humanity. The student once corrected by ‘I was poor’ stops using sagehood as the answer. Good defense does not make its object impossible to question. It protects the very openness by which that person became worth defending.",
    ],
    "zengzi-and-the-list": [
        "Later genealogies of Confucian transmission place Zengzi close to the center: Confucius, Zengzi, Zisi, Mencius. The Analects presents an earnest and morally serious student whose way of understanding also reveals how living speech becomes transmissible doctrine.",
        "Zengzi examines himself on three counts each day. He describes the cultivated person’s task as heavy and the road long. He says that when trying a case, one should pity rather than delight in extracting the truth. These are memorable and often humane statements. They also arrive as compact items, balances, and formulas.",
        "The same habit appears when Confucius says his way is threaded by one thing and then leaves. Zengzi tells the puzzled disciples: loyalty and reciprocity, nothing more. He does not counterfeit the attribution; ‘Zengzi said’ remains visible. But ‘nothing more’ converts an opening another learner might have traversed into a content that can be memorized.",
        "This may explain why later tradition found him so suitable as a transmitter. Lists travel. An unfinished silence does not. ‘Loyalty and reciprocity’ can be handed from teacher to pupil, examined, and certified. The teacher’s refusal to name the thread cannot found a curriculum without being changed.",
        "The point is not to dismiss Zengzi as someone who failed to understand. The same person can preserve ‘pity, do not rejoice’ and overfill an open sentence. His strength is inseparable from the risk: he knows how to make insight teachable. Every tradition needs that work. Every tradition must also remember what organization removes—the live occasion, the other person, and the room in which another answer could still arise.",
    ],
    "chapter-without-confucius": [
        "The nineteenth book of the Analects contains no direct speech from Confucius. Zizhang, Zixia, Ziyou, Zengzi, and Zigong speak; the teacher appears only inside recollection—‘I heard this from the Master.’ If the book were merely a container for authoritative sayings, this would be an odd chapter to preserve.",
        "Instead, we hear a school after and around its teacher. The students discuss learning, office, friendship, mourning, errors, and one another. They disagree. Ziyou criticizes Zixia’s pupils for attending to surface details; Zixia replies that no part of the Way can simply be thrown away. The inheritance exists as argument, not a single voice played back.",
        "Some of their sentences bear the structure already encountered. Zigong describes the teacher as learning from many people rather than possessing a fixed master. Zixia compares craftspeople completing work in their shops with cultivated people learning toward the Way. Zengzi tells officers judging cases to meet confessions with compassion, not triumph.",
        "These are not the teacher’s words and should not be silently reassigned. They show what different students learned and what each turned it into. To know a teacher is partly to observe the plurality of lives that continue after the lesson. Perfect uniformity might prove not faithful transmission but the extinction of judgment.",
        "A chapter without Confucius can therefore reveal the Confucian school more clearly than another collection of maxims. The teacher is present as difference among students: what they emphasize, systematize, resist, and correct. Ask of any education not only what the teacher said, but what becomes possible in the students’ own speech when the teacher is no longer in the room.",
    ],
    "not-yet-ren": [
        "Two classmates assess Zizhang in language that first sounds dismissive. Ziyou says he can accomplish what is difficult, yet is not yet ren. Zengzi calls him impressive in bearing but difficult to practice ren alongside. Later readers can hear an elite circle withholding its highest badge.",
        "But ‘not yet ren’ has a peculiar force in this school. Confucius refuses to call himself a man of ren. He seldom grants the designation to others; even Yan Hui is remembered through continuing advance rather than a completed title. The standard is not a credential possessed by teacher and rationed downward.",
        "The classmates also specify what they see. Zizhang is capable and imposing, perhaps too invested in the outer grandeur of the cultivated role. The criticism does not cancel his achievement. It asks whether a person difficult to stand beside has reached a virtue that must exist between people.",
        "To say ‘not yet’ therefore places Zizhang in company with everyone, including the teacher. It keeps the judgment open in time and refuses both condemnation and canonization. The school’s most honest shared name may be unfinished.",
        "Praise often tries to complete the person it loves; criticism often tries to close the file in the other direction. ‘Not yet ren’ does neither. It recognizes real ability, names a relational limit, and leaves movement possible. Heard inside this particular community, what resembles exclusion may be a form of equality.",
    ],
    "they-could-have-left-it-out": [
        "If the Analects were simply a publicity document for a dead master, its editors made strange choices. They record Confucius misjudging Duke Zhao’s ritual conduct, mocking Ziyou and being corrected, losing patience with Yuan Rang, despairing that no one knows him, and revising his method after Zai Wo disappoints him.",
        "They also preserve less flattering material about themselves. Zai Wo answers that he is comfortable abandoning three-year mourning. Students bury Yan Hui lavishly after Confucius says not to. Zilu creates a false household staff during the teacher’s illness and is rebuked. The group’s reverence, confusion, overreach, and disagreement remain in the record.",
        "Any one of these details could have disappeared without creating a visible gap. Together they are difficult to explain as image management. People constructing a flawless sage rarely include the moments in which his judgment fails and their own devotion becomes disobedience.",
        "This honesty did not prevent later smoothing. Names and gestures could still be stripped away until prescriptions became maxims. The students could not control the life of the book. Yet because they retained who asked, where someone stood, a smile, a tap of the staff, and the word with which a student refused, later readers can put the rough edges back.",
        "The Analects has at least two layers of discipleship: hands that arrange, fill, honor, and sometimes monumentalize; and eyes honest enough to record what resists the monument. The book remains readable because the second layer never entirely submits to the first. They did not leave us a seamless statue. They left a set of scenes with tool marks still showing.",
    ],
    "three-encounters-with-recluses": [
        "Textbooks often divide early Chinese thought into Confucian engagement and Daoist withdrawal. The Analects gives us several messier encounters. Recluses mock Confucius’s travellers for serving a world beyond repair. They know who the famous reformer is; the travellers often do not know the recluses’ names.",
        "A farmer tells Zilu that someone who does not labor with his limbs or distinguish the grains has no standing. Zilu receives hospitality but finds the man gone next morning. Confucius calls him a recluse and sends Zilu back, too late. In another scene, field workers warn that chaos floods the world and invite the travellers to follow those who avoid rulers altogether.",
        "Confucius’s answer is not that withdrawal is cowardice. He says he cannot herd with birds and beasts; if he does not live among these human beings, with whom can he live? Because the Way does not prevail, he must work for change. This explains his position without pretending the recluses’ choices are meaningless.",
        "Elsewhere he complicates the division further. Some people preserve their principles through withdrawal, others loosen their speech, others bend or refuse. Confucius says he differs by having no fixed ‘may’ and no fixed ‘may not.’ Engagement itself cannot become a form demanded of everyone in every time.",
        "The stable commitment is judgment, not a lifestyle. Confucius stays among people because he judges that this is where his work lies. Another person may rightly leave. When either decision becomes a permanent badge—engaged, withdrawn, pure, compromised—the living reason is replaced by a side in a diagram.",
    ],
    "the-step-only-you-can-take": [
        "We often evaluate teachers by their students’ outcomes. If one student flourishes and another dies pursuing a disastrous loyalty, we want to assign the difference backward. The Analects gives us Zilu and Zigong, two lives formed in the same school and ending along very different lines.",
        "Zilu repeatedly asks about courage, service, and fidelity. Confucius sees his excess of force and applies brakes: consult before acting; courage without rightness creates disorder; serve a ruler without deception but oppose him. In Wei’s civil conflict, Zilu enters danger because he has eaten another man’s food and believes he cannot abandon that man’s trouble. He dies after tying his severed cap cord.",
        "Zigong also asks about fidelity and joins the challenge to Guan Zhong for failing to die with his first lord. Confucius redirects judgment toward the people Guan Zhong spared. Later, Zigong conducts the diplomacy that helps save Lu. He learns a form of loyalty measured not by the beauty of sacrifice but by lives preserved.",
        "It would be too neat to turn the contrast into proof that one understood and one failed. Zilu’s final act grows from courage and obligation as he owned them; Zigong’s from a different capacity and history. A teacher can diagnose, advise, restrain, and offer counterexamples. At the decisive moment, the action cannot be performed through the teacher’s body.",
        "That limit belongs to genuine education. If the teacher guarantees the student’s destination, formation has become manufacture. Confucius can do everything that is his to do and still watch another person carry the teaching somewhere he would not choose. The final step is not evidence that teaching ended too soon. It is the place where a learner’s life becomes irreducibly their own.",
    ],
    "he-left-no-doctrine": [
        "After forty-nine essays, it is worth saying what this reconstruction has tried to do. It has not argued that Confucius secretly anticipated every value a contemporary reader wants. It has not attempted to solve the textual history of the Analects by assigning acceptable lines to the Master and embarrassing ones to later hands.",
        "Nor does it offer a new definitive system of Confucian thought. Its recurring action has been subtraction: restore the names before the sayings, the questions before the answers, the student’s refusal after the teacher’s reason, the laughter and correction around a polished maxim. Remove what later use has added and see whether a person appears beneath it.",
        "The person who appears does not leave a doctrine in the usual sense. He leaves a way of treating learners: see who is present, wait until the problem is theirs, supply materials and direction, draw necessary boundaries, and stop before taking the step that only they can take. Once summarized into rules, even that description risks becoming the kind of portable system he resisted.",
        "This is why the seams have remained visible. Some passages are strong anchors; others are useful counsel but poor evidence of a living encounter; some support structures—rank, unquestionable authority, exclusion—that this reading opposes. None of these judgments is declared immune from revision. A reconstruction faithful to an unfinished teacher must remain unfinished itself.",
        "Whether this really is the person preserved in the Analects, and whether his way of meeting another person is worth carrying forward, have not been answered on the reader’s behalf. Those are the three corners left after one has been shown. Open the book again. Do you see a doctrine waiting to be memorized—or someone still sitting across from a question?",
    ],
}


class TraditionalConverter:
    def __init__(self) -> None:
        self.cf = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
        self.cf.CFStringCreateMutable.argtypes = [ctypes.c_void_p, ctypes.c_long]
        self.cf.CFStringCreateMutable.restype = ctypes.c_void_p
        self.cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint]
        self.cf.CFStringCreateWithCString.restype = ctypes.c_void_p
        self.cf.CFStringAppend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.cf.CFStringTransform.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ubyte]
        self.cf.CFStringTransform.restype = ctypes.c_ubyte
        self.cf.CFStringGetLength.argtypes = [ctypes.c_void_p]
        self.cf.CFStringGetLength.restype = ctypes.c_long
        self.cf.CFStringGetMaximumSizeForEncoding.argtypes = [ctypes.c_long, ctypes.c_uint]
        self.cf.CFStringGetMaximumSizeForEncoding.restype = ctypes.c_long
        self.cf.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint]
        self.cf.CFStringGetCString.restype = ctypes.c_ubyte
        self.cf.CFRelease.argtypes = [ctypes.c_void_p]
        self.transform = self._string("Traditional-Simplified")

    def _string(self, value: str) -> int:
        return self.cf.CFStringCreateWithCString(None, value.encode("utf-8"), UTF8)

    def convert(self, value: str) -> str:
        source_ref = self._string(value)
        mutable = self.cf.CFStringCreateMutable(None, 0)
        try:
            self.cf.CFStringAppend(mutable, source_ref)
            if not self.cf.CFStringTransform(mutable, None, self.transform, 1):
                raise RuntimeError("Traditional Chinese conversion failed")
            length = self.cf.CFStringGetLength(mutable)
            capacity = self.cf.CFStringGetMaximumSizeForEncoding(length, UTF8) + 1
            buffer = ctypes.create_string_buffer(capacity)
            if not self.cf.CFStringGetCString(mutable, buffer, capacity, UTF8):
                raise RuntimeError("Could not decode converted text")
            result = buffer.value.decode("utf-8")
        finally:
            self.cf.CFRelease(source_ref)
            self.cf.CFRelease(mutable)
        # Editorial house forms that the system transform does not choose reliably.
        for simple, traditional in {
            "里面": "裡面", "这里": "這裡", "那里": "那裡", "哪里": "哪裡",
            "为了": "為了", "什么": "什麼", "为什么": "為什麼", "怎么": "怎麼",
            "着": "著", "只": "只", "干": "幹", "才": "才", "余地": "餘地",
            "汉": "漢", "论语": "論語", "孔门": "孔門", "圣人": "聖人",
        }.items():
            result = result.replace(simple, traditional)
        result = result.replace("里", "裡").replace("裡仁", "里仁").replace("台", "臺")
        result = re.sub(r"([十百千萬0-9])裡", r"\1里", result)
        return result

    def close(self) -> None:
        self.cf.CFRelease(self.transform)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def inline(value: str) -> str:
    value = esc(value)
    value = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+?)\*", r"<em>\1</em>", value)
    return value


def markdown_blocks(text: str) -> str:
    blocks: list[str] = []
    for raw in re.split(r"\n\s*\n", text.strip()):
        raw = raw.strip()
        if not raw or raw == "---" or raw.startswith("#"):
            continue
        if raw.startswith(">"):
            quote = "<br>".join(inline(line.lstrip("> ")) for line in raw.splitlines())
            blocks.append(f"<blockquote>{quote}</blockquote>")
        else:
            blocks.append(f"<p>{inline(' '.join(raw.splitlines()))}</p>")
    return "".join(blocks)


def source_item(number: str) -> tuple[Path, str, str, str]:
    matches = list(SOURCE.glob(f"大知解论语_{number}_*.md"))
    if len(matches) != 1:
        raise ValueError(f"Expected one source for {number}, found {matches}")
    path = matches[0]
    text = path.read_text(encoding="utf-8")
    headings = re.findall(r"^# (.+)$", text, re.M)
    if len(headings) < 2:
        raise ValueError(f"Missing headings in {path}")
    title_zh = headings[1]
    parts = re.split(r"\n---\n", text, maxsplit=1)
    body = parts[0]
    body = re.sub(r"^# .+\n", "", body, count=2, flags=re.M)
    body = re.sub(r"^秦汉（字大知）· 2026 年 9 月\n", "", body, count=1, flags=re.M)
    footer = parts[1].strip() if len(parts) == 2 else ""
    return path, title_zh, body.strip(), footer


def movement_for(index: int) -> tuple[int, int, str, str, str]:
    return next(m for m in MOVEMENTS if m[0] <= index <= m[1])


def shell_header(prefix: str, page: str) -> str:
    editions = {
        "ja": "日本語", "fr": "Français", "de": "Deutsch",
        "es": "Español", "ko": "한국어",
    }
    desktop_editions = "".join(
        f'<a href="{code}/{page}">{label}</a>' for code, label in editions.items()
    )
    mobile_editions = "".join(
        f'<a href="{code}/{page}">{label if code in ("ja", "ko") else code.upper()}</a>'
        for code, label in editions.items()
    )
    return f'''<header class="site-shell-header"><div class="header-inner"><a href="{prefix}index.html" class="site-title" aria-label="Non Dubito home"><span class="title-latin">Non <span>Dubito</span></span><span class="title-sub">Essays in the Self-as-an-End Tradition</span></a><nav class="site-shell-nav" aria-label="Primary navigation"><a href="{prefix}start.html"><span class="lang-en">Start Here</span><span class="lang-zh">从这里开始</span><span class="lang-hant">從這裡開始</span></a><a href="{prefix}explore.html"><span class="lang-en">Explore</span><span class="lang-zh">探索</span><span class="lang-hant">探索</span></a><a href="{prefix}latest.html"><span class="lang-en">Latest</span><span class="lang-zh">最近更新</span><span class="lang-hant">最近更新</span></a><a href="{prefix}about.html"><span class="lang-en">About</span><span class="lang-zh">关于</span><span class="lang-hant">關於</span></a></nav><div class="site-shell-tools"><a class="site-shell-tool" href="{prefix}search.html" aria-label="Search"><svg class="site-shell-tool-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="1.5"/><path d="m16 16 4 4" stroke="currentColor" stroke-width="1.5"/></svg><span class="site-shell-tool-label lang-en">Search</span><span class="site-shell-tool-label lang-zh">搜索</span><span class="site-shell-tool-label lang-hant">搜尋</span></a><details class="site-shell-language"><summary class="site-shell-language-summary"><span data-current-language>EN</span><span aria-hidden="true">⌄</span></summary><div class="site-shell-language-options"><button type="button" data-set-language="en">English</button><button type="button" data-set-language="zh">中文</button><button type="button" data-set-language="zh-hant">繁體中文</button>{desktop_editions}</div></details><button class="site-shell-menu-button" type="button" data-site-shell-menu aria-controls="site-shell-drawer" aria-expanded="false"><span class="site-shell-tool-label lang-en">Menu</span><span class="site-shell-tool-label lang-zh">菜单</span><span class="site-shell-tool-label lang-hant">選單</span><span aria-hidden="true">☰</span></button></div></div></header><div class="site-shell-drawer" id="site-shell-drawer" data-site-shell-drawer><nav aria-label="Mobile navigation"><a href="{prefix}start.html"><span class="lang-en">Start Here</span><span class="lang-zh">从这里开始</span><span class="lang-hant">從這裡開始</span></a><a href="{prefix}explore.html"><span class="lang-en">Explore</span><span class="lang-zh">探索</span><span class="lang-hant">探索</span></a><a href="{prefix}latest.html"><span class="lang-en">Latest</span><span class="lang-zh">最近更新</span><span class="lang-hant">最近更新</span></a><a href="{prefix}about.html"><span class="lang-en">About</span><span class="lang-zh">关于</span><span class="lang-hant">關於</span></a><a href="{prefix}library.html"><span class="lang-en">Full Library</span><span class="lang-zh">完整书库</span><span class="lang-hant">完整書庫</span></a><a href="{prefix}credesivis.html">Crede si vis</a></nav><div class="site-shell-mobile-languages" aria-label="Languages"><button type="button" data-set-language="en">EN</button><button type="button" data-set-language="zh">中文</button><button type="button" data-set-language="zh-hant">繁體</button>{mobile_editions}</div></div>'''


def head(title: str, description: str, path: str, page_type: str = "article") -> str:
    canonical = f"https://nondubito.net/{path}"
    tail = "" if path.endswith("/") else Path(path).name
    base = "https://nondubito.net/essays/analects/"
    alternates = "".join(
        f'<link rel="alternate" hreflang="{code}" href="{base}{lang}/{tail}">'
        for code, lang in (("ja", "ja"), ("fr", "fr"), ("de", "de"), ("es", "es"), ("ko", "ko"))
    )
    return f'''<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(description)}"><meta name="author" content="Han Qin (秦汉)"><meta property="og:type" content="{page_type}"><meta property="og:title" content="{esc(title)} — Non Dubito"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta name="twitter:card" content="summary"><link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="en" href="{canonical}"><link rel="alternate" hreflang="zh-Hans" href="{canonical}"><link rel="alternate" hreflang="zh-Hant" href="{canonical}">{alternates}<link rel="alternate" hreflang="x-default" href="{canonical}"><link rel="icon" type="image/svg+xml" href="../../favicon.svg"><link rel="apple-touch-icon" sizes="180x180" href="../../apple-touch-icon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;family=Noto+Serif+JP:wght@400;500;600&amp;family=Noto+Serif+KR:wght@400;500;600&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="analects.css?v=20260909"><script src="../../site-shell.js?v=20260905b"></script></head>'''


def research_note(footer: str, english: bool = False) -> str:
    doi = re.search(r"https://doi\.org/[^)\s]+", footer)
    link = doi.group(0) if doi else RESEARCH[0][3]
    if english:
        return f'<p class="source-note">Research basis: this reader-facing essay is an independent reconstruction of the Chinese original. The underlying structural argument is documented in the <a href="{link}" target="_blank" rel="noopener">research edition ↗</a>.</p>'
    footer = footer.replace("｜ 系列总纲《解论语·涵育者》见置顶。", "｜ 系列理论底本见总目。")
    footer = footer.replace("｜ 系列總綱《解論語·涵育者》見置頂。", "｜ 系列理論底本見總目。")
    return markdown_blocks(footer).replace("<p>", '<p class="source-note">', 1)


def language_article(lang: str, number: str, title: str, deck: str, body: str, footer: str, move_en: str, move_zh: str) -> str:
    label = {"en": f"Essay {number} of 50", "zh": f"第 {number} 篇，共 50 篇", "hant": f"第 {number} 篇，共 50 篇"}[lang]
    movement = move_en if lang == "en" else move_zh
    author = "Han Qin (秦漢)" if lang == "hant" else "Han Qin (秦汉)"
    return f'''<div class="lang-{lang} local"><article class="analects-article"><header class="article-head"><p class="article-kicker">{esc(movement)}</p><p class="article-number">{label}</p><h1>{esc(title)}</h1><p class="article-deck">{esc(deck)}</p><p class="article-byline">{author} · 2026</p></header><div class="article-body">{body}{research_note(footer, lang == "en")}</div></article></div>'''


def article_html(item: tuple[str, str, str, str], position: int, converter: TraditionalConverter) -> str:
    number, slug, title_en, deck_en = item
    _, title_zh, body_zh, footer_zh = source_item(number)
    title_hant, body_hant, footer_hant = map(converter.convert, (title_zh, body_zh, footer_zh))
    move = movement_for(position + 1)
    move_hant = converter.convert(move[3])
    previous = ITEMS[position - 1] if position else None
    following = ITEMS[position + 1] if position + 1 < len(ITEMS) else None
    nav_parts = []
    if previous:
        nav_parts.append(f'<a href="{previous[0]}-{previous[1]}.html"><small>← <span class="lang-en">Previous</span><span class="lang-zh">上一篇</span><span class="lang-hant">上一篇</span></small><span class="lang-en">{esc(previous[2])}</span><span class="lang-zh">{esc(source_item(previous[0])[1])}</span><span class="lang-hant">{esc(converter.convert(source_item(previous[0])[1]))}</span></a>')
    if following:
        nav_parts.append(f'<a class="next" href="{following[0]}-{following[1]}.html"><small><span class="lang-en">Next</span><span class="lang-zh">下一篇</span><span class="lang-hant">下一篇</span> →</small><span class="lang-en">{esc(following[2])}</span><span class="lang-zh">{esc(source_item(following[0])[1])}</span><span class="lang-hant">{esc(converter.convert(source_item(following[0])[1]))}</span></a>')
    english_body = "".join(f"<p>{inline(p)}</p>" for p in ENGLISH[slug])
    contents = (
        language_article("en", number, title_en, deck_en, english_body, footer_zh, move[2], move[3])
        + language_article("zh", number, title_zh, "把名字和场景放回“子曰”之前。", markdown_blocks(body_zh), footer_zh, move[2], move[3])
        + language_article("hant", number, title_hant, "把名字和場景放回「子曰」之前。", markdown_blocks(body_hant), footer_hant, move[2], move_hant)
    )
    desc = deck_en
    schema = json.dumps({"@context":"https://schema.org","@type":"Article","headline":title_en,"description":deck_en,"author":{"@type":"Person","name":"Han Qin (秦汉)"},"isPartOf":{"@type":"CreativeWorkSeries","name":"The Analects, Reopened"},"position":position + 1,"url":f"https://nondubito.net/essays/analects/{number}-{slug}.html"}, ensure_ascii=False, indent=2)
    page = f"{number}-{slug}.html"
    return f'''<!DOCTYPE html><html lang="en" data-lang="en">{head(title_en + " · The Analects, Reopened", desc, f"essays/analects/{page}")}<body class="site-shell-page explicit-hant">{shell_header("../../", page)}<main class="analects-wrap"><div class="article-top"><a href="index.html">← <span class="lang-en">The Analects, Reopened</span><span class="lang-zh">大知解论语</span><span class="lang-hant">大知解論語</span></a></div>{contents}<nav class="series-nav">{"".join(nav_parts)}</nav><aside class="reader-door"><span class="lang-en">This essay belongs to a fifty-part reconstruction. <a href="index.html">Return to the four movements</a>, or continue to the research edition below the series.</span><span class="lang-zh">本文属于五十篇重构。可<a href="index.html">返回四辑总目</a>，或在系列页继续进入理论底本。</span><span class="lang-hant">本文屬於五十篇重構。可<a href="index.html">返回四輯總目</a>，或在系列頁繼續進入理論底本。</span></aside></main><footer class="site-shell-footer"><div class="site-shell-footer-inner"><div><div class="site-shell-footer-mark">Non <span>Dubito</span></div><p>A mind in many languages</p></div><div class="site-shell-footer-links"><a href="../../about.html">About</a><a href="../../library.html">Full Library</a><a href="https://self-as-an-end.net">SAE Theory ↗</a></div></div></footer><script type="application/ld+json">{schema}</script></body></html>'''


def cards(lang: str, converter: TraditionalConverter) -> str:
    groups = []
    for start, end, move_en, move_zh, move_desc in MOVEMENTS:
        title = move_en if lang == "en" else (move_zh if lang == "zh" else converter.convert(move_zh))
        desc = ({"en": {
            1: "Meet Confucius through the way he listens, answers, changes his mind, and knows when to stop.",
            19: "Put famous sayings back into the sentences, scenes, and disagreements from which they were cut.",
            32: "A method for resisting both worship and dismissal without pretending to settle textual history.",
            42: "Watch the students inherit, alter, contest, and honestly preserve a teacher they could not freeze in place.",
        }[start], "zh": move_desc, "hant": converter.convert(move_desc)}[lang])
        article_cards = []
        for item in ITEMS[start - 1:end]:
            number, slug, title_en, deck_en = item
            title_zh = source_item(number)[1]
            title_i = title_en if lang == "en" else (title_zh if lang == "zh" else converter.convert(title_zh))
            deck_i = deck_en if lang == "en" else ("把人和场景放回这句话。" if lang == "zh" else "把人和場景放回這句話。")
            read = {"en":"Read essay", "zh":"阅读", "hant":"閱讀"}[lang]
            article_cards.append(f'<a class="essay-card" href="{number}-{slug}.html"><span class="essay-no">{number}</span><h3>{esc(title_i)}</h3><p>{esc(deck_i)}</p><span class="read-arrow">{read} →</span></a>')
        groups.append(f'<section class="movement"><header><span>{start:02d}—{end:02d}</span><h2>{esc(title)}</h2><p>{esc(desc)}</p></header><div class="essay-grid">{"".join(article_cards)}</div></section>')
    return "".join(groups)


def index_html(converter: TraditionalConverter) -> str:
    routes = {"en": [], "zh": [], "hant": []}
    for number in ("01", "02", "05", "25", "32", "37", "47", "50"):
        item = next(i for i in ITEMS if i[0] == number)
        zh = source_item(number)[1]
        for lang, title in (("en", item[2]), ("zh", zh), ("hant", converter.convert(zh))):
            routes[lang].append(f'<a href="{number}-{item[1]}.html"><span>{number}</span>{esc(title)}</a>')
    research_en = "".join(f'<a href="{url}" target="_blank" rel="noopener"><small>{label}</small><strong>{esc(en)}</strong><span>{esc(zh)} ↗</span></a>' for label, en, zh, url in RESEARCH)
    research_zh = "".join(f'<a href="{url}" target="_blank" rel="noopener"><small>{label.replace("General Introduction", "总论").replace("Part", "卷")}</small><strong>{esc(zh)}</strong><span>{esc(en)} ↗</span></a>' for label, en, zh, url in RESEARCH)
    research_hant = converter.convert(research_zh)
    sections = []
    for lang, title, deck, note in [
        ("en", "The Analects, Reopened", "Fifty encounters with Confucius—putting the names back before ‘The Master said.’", "This is one structural reading, not a claim to settle the philology or textual history of the Analects. It asks a narrower question: when we restore the person, occasion, and reply, what kind of teacher appears?"),
        ("zh", "大知解论语", "把“子曰”前面的名字放回去。五十篇，重新遇见孔子。", "这是一种结构阅读，不是训诂与文本史的最终裁决。它只问一个更窄的问题：把人名、场景与来回放回原处以后，我们看见的是怎样一个老师？"),
        ("hant", "大知解論語", "把「子曰」前面的名字放回去。五十篇，重新遇見孔子。", "這是一種結構閱讀，不是訓詁與文本史的最終裁決。它只問一個更窄的問題：把人名、場景與來回放回原處以後，我們看見的是怎樣一個老師？"),
    ]:
        route_title = {"en":"Eight ways in", "zh":"如果不想一次读完：八篇入口", "hant":"如果不想一次讀完：八篇入口"}[lang]
        route_desc = {"en":"A short route through method, authority, misreading, disagreement, and the limits of the record.", "zh":"从教法、权威与误读，走到争辩、记录的限度与最后留下的问题。", "hant":"從教法、權威與誤讀，走到爭辯、記錄的限度與最後留下的問題。"}[lang]
        research_title = {"en":"Research edition", "zh":"理论底本", "hant":"理論底本"}[lang]
        research_desc = {"en":"The five formal SAE papers document the argument in full. The fifty essays above are the public-facing reconstruction; readers do not need the papers in order to begin.", "zh":"五篇 SAE 论文保存完整论证。上面的五十篇是面向普通读者的重写；读者无需先读论文，也可以从任何一篇开始。", "hant":"五篇 SAE 論文保存完整論證。上面的五十篇是面向普通讀者的重寫；讀者無需先讀論文，也可以從任何一篇開始。"}[lang]
        research_cards = {"en":research_en, "zh":research_zh, "hant":research_hant}[lang]
        author = "Han Qin (秦漢)" if lang == "hant" else "Han Qin (秦汉)"
        sections.append(f'''<div class="lang-{lang} local"><section class="series-hero"><p class="series-kicker">Non Dubito · Chinese Classics</p><h1>{title}</h1><p class="series-deck">{deck}</p><div class="series-meta">{author} · 2026 · 4 movements · 50 essays · 8 languages</div></section><aside class="method-note"><strong>{"A note on the reading" if lang == "en" else ("关于这套读法" if lang == "zh" else "關於這套讀法")}</strong><p>{note}</p></aside><section class="reading-route"><h2>{route_title}</h2><p>{route_desc}</p><div class="route-grid">{"".join(routes[lang])}</div></section>{cards(lang, converter)}<section class="research"><header><p>SAE · Analects</p><h2>{research_title}</h2><span>{research_desc}</span></header><div class="research-grid">{research_cards}</div></section></div>''')
    schema = json.dumps({"@context":"https://schema.org","@type":"CollectionPage","name":"The Analects, Reopened","alternateName":["大知解论语","大知解論語"],"description":"Fifty encounters with Confucius, putting the names back before ‘The Master said.’","url":"https://nondubito.net/essays/analects/","author":{"@type":"Person","name":"Han Qin (秦汉)"},"mainEntity":{"@type":"ItemList","numberOfItems":50,"itemListElement":[{"@type":"ListItem","position":n,"name":item[2],"url":f"https://nondubito.net/essays/analects/{item[0]}-{item[1]}.html"} for n, item in enumerate(ITEMS, 1)]}}, ensure_ascii=False, indent=2)
    return f'''<!DOCTYPE html><html lang="en" data-lang="en">{head("The Analects, Reopened · Fifty Encounters with Confucius", "Fifty essays put the names and scenes back before ‘The Master said,’ reopening the Analects as encounters rather than a book of slogans.", "essays/analects/", "website")}<body class="site-shell-page explicit-hant">{shell_header("../../", "index.html")}<main class="analects-wrap">{"".join(sections)}</main><footer class="site-shell-footer"><div class="site-shell-footer-inner"><div><div class="site-shell-footer-mark">Non <span>Dubito</span></div><p>A mind in many languages</p></div><div class="site-shell-footer-links"><a href="../../about.html">About</a><a href="../../library.html">Full Library</a><a href="https://self-as-an-end.net">SAE Theory ↗</a></div></div></footer><script type="application/ld+json">{schema}</script></body></html>'''


def serialize_updates(data: dict) -> str:
    """Keep the update ledger's deliberately compact, reviewable house style."""
    lines = [
        "{",
        f'  "version": {json.dumps(data["version"], ensure_ascii=False)},',
        f'  "policy": {json.dumps(data["policy"], ensure_ascii=False)},',
        '  "updates": [',
    ]
    for index, item in enumerate(data["updates"]):
        comma = "," if index + 1 < len(data["updates"]) else ""
        lines.extend([
            "    {",
            f'      "id": {json.dumps(item["id"], ensure_ascii=False)},',
            f'      "date": {json.dumps(item["date"], ensure_ascii=False)},',
            f'      "kind": {json.dumps(item["kind"], ensure_ascii=False)},',
            f'      "domain": {json.dumps(item["domain"], ensure_ascii=False)},',
            f'      "url": {json.dumps(item["url"], ensure_ascii=False)},',
            f'      "languages": {json.dumps(item["languages"], ensure_ascii=False)},',
            f'      "title": {json.dumps(item["title"], ensure_ascii=False)},',
            f'      "summary": {json.dumps(item["summary"], ensure_ascii=False)}',
            f"    }}{comma}",
        ])
    lines.extend(["  ]", "}"])
    return "\n".join(lines) + "\n"


def updated_hubs() -> dict[Path, str]:
    paths = {"library":ROOT / "library.html", "explore":ROOT / "explore.html", "updates":ROOT / "data/site-updates.json", "latest":ROOT / "latest.html"}
    out = {k:p.read_text(encoding="utf-8") for k,p in paths.items()}
    if 'href="essays/analects/index.html"' not in out["library"]:
        marker = '    <a href="essays/daodejing/index.html" class="series-card">'
        card = '''    <a href="essays/analects/index.html" class="series-card">
      <span class="series-card-count"><span class="lang-en">50 essays · 3 reading modes</span><span class="lang-zh">50 篇 · 英 / 简 / 繁</span><span class="lang-hant">50 篇 · 英 / 簡 / 繁</span></span>
      <div class="series-card-title-zh"><span class="lang-zh">大知解论语</span><span class="lang-hant">大知解論語</span></div>
      <div class="series-card-title-en">The Analects, Reopened</div>
      <p class="series-card-desc-zh lang-zh">把“子曰”前面的名字放回去：五十篇从问答、分歧、误读与记录的毛边，重新遇见孔子。</p>
      <p class="series-card-desc-zh lang-hant">把「子曰」前面的名字放回去：五十篇從問答、分歧、誤讀與記錄的毛邊，重新遇見孔子。</p>
      <p class="series-card-desc-en lang-en">Fifty encounters restore the names, occasions, disagreements, and unfinished edges before “The Master said.”</p>
      <span class="series-card-arrow lang-en">Read series</span><span class="series-card-arrow lang-zh">阅读系列</span><span class="series-card-arrow lang-hant">閱讀系列</span>
    </a>
'''
        out["library"] = out["library"].replace(marker, card + marker, 1)
    if 'href="essays/analects/index.html"' not in out["explore"]:
        marker = '        <a class="shelf-link" href="essays/literature/index.html">'
        card = '''        <a class="shelf-link" href="essays/analects/index.html"><span class="shelf-label lang-en">Chinese classic</span><span class="shelf-label lang-zh">中国经典</span><span class="shelf-label lang-hant">中國經典</span><h3 class="lang-en">The Analects, Reopened</h3><h3 class="lang-zh">大知解论语</h3><h3 class="lang-hant">大知解論語</h3><p class="lang-en">Fifty encounters put the names back before “The Master said.”</p><p class="lang-zh">五十次相遇，把“子曰”前面的名字放回去。</p><p class="lang-hant">五十次相遇，把「子曰」前面的名字放回去。</p><span class="shelf-arrow">→</span></a>
'''
        out["explore"] = out["explore"].replace(marker, card + marker, 1)
    data = json.loads(out["updates"])
    update = {"id":"2026-09-08-analects-reopened","date":"2026-09-08","kind":"new","domain":"literature","url":"essays/analects/index.html","languages":["en","zh","zh-hant"],"title":{"en":"The Analects, Reopened","zh":"大知解论语","zh-hant":"大知解論語"},"summary":{"en":"Fifty essays restore names, scenes, disagreements, and unfinished edges before ‘The Master said,’ with an eight-essay entrance route and five formal research papers.","zh":"五十篇把人名、场景、分歧与记录的毛边放回“子曰”之前，并设置八篇入口与五篇理论底本。","zh-hant":"五十篇把人名、場景、分歧與記錄的毛邊放回「子曰」之前，並設置八篇入口與五篇理論底本。"}}
    if not any(x["id"] == update["id"] for x in data["updates"]):
        data["updates"].insert(0, update)
    out["updates"] = serialize_updates(data)
    if 'data-update-id="2026-09-08-analects-reopened"' not in out["latest"]:
        marker = '    <section class="latest-feed"'
        # Insert a complete day section immediately inside the feed container.
        open_marker = '<section class="updates-section"><div class="latest-inner">'
        section = '''<section class="updates-day" aria-labelledby="date-2026-09-08"><header class="updates-date"><div><p class="latest-date-label">Publication date</p><h2 id="date-2026-09-08"><time datetime="2026-09-08"><span class="lang-en">8 September</span><span class="lang-zh">9 月 8 日</span><span class="lang-hant">9 月 8 日</span></time></h2></div><p class="lang-en">A flagship reconstruction returns the Analects to names, rooms, questions, and disagreement.</p><p class="lang-zh">一套旗舰重构，把《论语》放回人名、房间、问题与分歧之中。</p><p class="lang-hant">一套旗艦重構，把《論語》放回人名、房間、問題與分歧之中。</p></header><div class="updates-grid"><article class="update-card" data-update-id="2026-09-08-analects-reopened"><div class="update-meta"><span class="update-kind"><span class="lang-en">New flagship</span><span class="lang-zh">新旗舰</span><span class="lang-hant">新旗艦</span></span><span class="update-languages">EN / 简 / 繁</span></div><h3 class="lang-en">The Analects, Reopened</h3><h3 class="lang-zh">大知解论语</h3><h3 class="lang-hant">大知解論語</h3><p class="lang-en">Fifty encounters restore the names and scenes before “The Master said,” with four movements, an eight-essay entrance route, and five research papers.</p><p class="lang-zh">五十篇把人名与场景放回“子曰”之前，并以四辑、八篇入口和五篇理论底本重新组织。</p><p class="lang-hant">五十篇把人名與場景放回「子曰」之前，並以四輯、八篇入口和五篇理論底本重新組織。</p><a href="essays/analects/index.html"><span class="lang-en">Enter the series →</span><span class="lang-zh">进入系列 →</span><span class="lang-hant">進入系列 →</span></a></article></div></section>'''
        if open_marker not in out["latest"]:
            raise ValueError(f"Could not find latest feed marker after {marker}")
        out["latest"] = out["latest"].replace(open_marker, open_marker + section, 1)
    return {paths[k]:v for k,v in out.items()}


def render() -> dict[Path, str]:
    missing = [slug for _, slug, _, _ in ITEMS if slug not in ENGLISH]
    if missing:
        raise ValueError("Missing English rewrites: " + ", ".join(missing))
    converter = TraditionalConverter()
    try:
        outputs = updated_hubs()
        outputs[TARGET / "index.html"] = index_html(converter)
        outputs.update({TARGET / f"{item[0]}-{item[1]}.html":article_html(item, i, converter) for i,item in enumerate(ITEMS)})
        return {
            path: text.replace("analects.css?v=20260909", "analects.css?v=20260909b")
            for path, text in outputs.items()
        }
    finally:
        converter.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    stale = [path for path,text in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != text]
    if args.check:
        if stale:
            raise SystemExit("Stale Analects pages:\n" + "\n".join(str(p.relative_to(ROOT)) for p in stale))
        print(f"OK: {len(outputs)} Analects files")
        return
    for path,text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"Wrote: {len(outputs)} Analects files")


if __name__ == "__main__":
    main()
