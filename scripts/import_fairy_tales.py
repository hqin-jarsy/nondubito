#!/usr/bin/env python3
"""Build the Chinese, English, and Traditional Chinese fairy-tale collection."""

from __future__ import annotations

import argparse
import ctypes
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/hanqin/Documents/SAE日常/童话里的结构_v1")
TARGET = ROOT / "essays" / "everyday" / "stories" / "fairy-tales"
UTF8 = 0x08000100


ITEMS = [
    {"file": "01_会纺金子的侏儒_v0.2.md", "slug": "01-rumpelstiltskin", "work_zh": "《侏儒怪》", "work_en": "Rumpelstiltskin", "title_en": "Rumpelstiltskin: Does a Promise Made under Threat Bind a Future Child?", "deck_en": "A rescue can be real without making every requested price legitimate—especially when the price is another person's life.", "source_en": "The essay follows the Grimms’ 1857 version, including the first two death threats, the marriage reward, the naming trial, and Rumpelstiltskin’s final destruction."},
    {"file": "02_小美人鱼失去声音_v0.2.md", "slug": "02-little-mermaid", "work_zh": "《小美人鱼》", "work_en": "The Little Mermaid", "title_en": "The Little Mermaid Loses Her Voice: How Much of Yourself Can You Change for Love?", "deck_en": "She wanted the human world before she wanted the prince, yet reaching both required a price she could not fully understand until she had paid it.", "source_en": "The essay follows Andersen’s 1837 tale, including the mermaid’s threefold longing, the stated price of transformation, the mistaken rescue, her refusal to kill, and the Daughters of the Air."},
    {"file": "03_青蛙拿着一句承诺进入宫殿_v0.2.md", "slug": "03-frog-king", "work_zh": "《青蛙王子，或铁亨利》", "work_en": "The Frog King", "title_en": "The Frog Carries a Promise into the Palace: How Far Must It Be Kept?", "deck_en": "A promise can create duties of honesty and repair without granting advance ownership of intimacy.", "source_en": "The essay follows the Grimms’ 1857 version: the golden ball, the request to share plate, cup, and bed, the king’s command, the wall-throwing transformation, and Iron Henry."},
    {"file": "04_蓝胡子把钥匙交给妻子_v0.2.md", "slug": "04-bluebeard", "work_zh": "《蓝胡子》", "work_en": "Bluebeard", "title_en": "Bluebeard Gives His Wife the Key: What Is the Forbidden Room Protecting?", "deck_en": "Privacy deserves protection; a rule that hides murdered wives is doing something else.", "source_en": "The essay follows Perrault’s 1697 tale and its two morals, retaining the bloodstained key, Sister Anne at the tower, the brothers’ rescue, and the wife’s later life."},
    {"file": "05_美女为什么重新回到野兽身边_v0.2.md", "slug": "05-beauty-and-beast", "work_zh": "《美女与野兽》", "work_en": "Beauty and the Beast", "title_en": "Why Does Beauty Return to the Beast? Can Later Consent Change a Coercive Beginning?", "deck_en": "A relationship may become real after beginning in fear, but later love does not retroactively cleanse the threat that opened it.", "source_en": "The essay follows Leprince de Beaumont’s short 1756 version, including the father’s resistance, repeated proposals, Beauty’s one-week promise, the Beast’s self-starvation, and the final transformation."},
    {"file": "06_父亲以为许出的是苹果树_v0.2.md", "slug": "06-girl-without-hands", "work_zh": "《无手少女》", "work_en": "The Girl Without Hands", "title_en": "Her Father Thought He Had Promised an Apple Tree: Why Are Her Hands Cut Off?", "deck_en": "A misunderstanding explains the first promise; it cannot explain away what the father does after learning whom the bargain contains.", "source_en": "The essay follows the Grimms’ complete 1857 version, including the pious resistance, severed hands, silver hands, falsified letters, two departures, and eventual reunion."},
    {"file": "07_格尔达去救一个不想回家的凯_v0.2.md", "slug": "07-snow-queen", "work_zh": "《冰雪女王》", "work_en": "The Snow Queen", "title_en": "Gerda Goes to Save a Kay Who Does Not Want to Return: Who Knows the ‘Real You’?", "deck_en": "Care can refuse to abandon someone without claiming permanent authority to define who that person truly is.", "source_en": "The essay follows Andersen’s seven-part 1844 tale, retaining Gerda’s own episodes of forgetting, Kay’s tears, the word ‘eternity,’ and their grown return home."},
    {"file": "08_皇帝想把夜莺留在宫里_v0.2.md", "slug": "08-nightingale", "work_zh": "《夜莺》", "work_en": "The Nightingale", "title_en": "The Emperor Wants the Nightingale in His Palace: Why Doesn’t Love of Its Song Grant Control of Its Life?", "deck_en": "The song that finally saves the emperor returns through an open window, not from the cage that once guaranteed possession.", "source_en": "The essay follows Andersen’s 1843 tale, including the twelve ribbons, the mechanical bird’s genuine uses and limits, Death at the bedside, and the nightingale’s free return."},
    {"file": "09_真正的公主不能直接说出真相_v0.2.md", "slug": "09-goose-girl", "work_zh": "《牧鹅姑娘》", "work_en": "The Goose Girl", "title_en": "The Goose Girl Cannot Tell the Truth Directly: How Else Can a Fact Enter the World?", "deck_en": "When a threat has sealed a person’s speech, the absence of accusation cannot be treated as the absence of another story.", "source_en": "The essay follows the Grimms’ 1857 version, including the coerced oath, Falada’s death, Conrad’s complaint, the king’s observation, the iron stove, and the false bride’s sentence."},
    {"file": "10_乌龟只答应唱给一个人听_v0.2.md", "slug": "10-hunter-and-tortoise", "work_zh": "《猎人与乌龟》", "work_en": "The Hunter and the Tortoise", "title_en": "The Tortoise Agreed to Sing for One Person: May She Still Refuse the Crowd?", "deck_en": "A private gift does not become a public performance merely because its recipient has wagered his reputation—or his life—on it.", "source_en": "The essay is limited to ‘The Hunter and the Tortoise’ as collected and arranged in Barker and Sinclair’s 1917 West African Folk-Tales; it does not claim to represent a single people or oral tradition."},
    {"file": "11_三个纺纱女坐上婚宴_v0.2.md", "slug": "11-three-spinners", "work_zh": "《三个纺纱女》", "work_en": "The Three Spinners", "title_en": "The Three Spinners Sit at the Wedding Feast: Why Should the Helpers Remain Visible?", "deck_en": "The bride cannot disclose every part of the deception, yet she can refuse the neatest form of success: hiding those who did the work.", "source_en": "The essay follows the Grimms’ 1857 tale, retaining the girl’s dislike of spinning, her mother’s lie, the three helpers’ condition, the concealed labor, and the prince’s final ban on spinning."},
    {"file": "12_长发公主放下头发_v0.2.md", "slug": "12-rapunzel", "work_zh": "《长发公主》", "work_en": "Rapunzel", "title_en": "Rapunzel Lets Down Her Hair: Why Can the Road In Not Become Her Road Out?", "deck_en": "A tower can be perfectly accessible to its keeper and still offer no exit to the person who lives inside.", "source_en": "The essay follows the Grimms’ 1857 version, including the window hook, the prince’s uninvited first ascent, Rapunzel’s silk ladder plan, the leap from the tower, and reunion in the wilderness."},
    {"file": "13_灰姑娘换上礼服以前_v0.2.md", "slug": "13-cinderella", "work_zh": "《灰姑娘》", "work_en": "Cinderella", "title_en": "Before Cinderella Changes Clothes: Why Didn’t Her Existing Abilities Count?", "deck_en": "The gown and slipper make Cinderella visible; they do not create the judgment, taste, and desire that were already hers.", "source_en": "The essay follows Perrault’s 1697 Cinderella rather than the Grimms’ version, retaining the sisters’ requests for advice, two balls, the fairy godmother, both slippers, forgiveness, and the appended morals."},
    {"file": "14_丑小鸭被认出是天鹅_v0.2.md", "slug": "14-ugly-duckling", "work_zh": "《丑小鸭》", "work_en": "The Ugly Duckling", "title_en": "The Ugly Duckling Is Recognized as a Swan: Did That Make Him Worthy of Kindness?", "deck_en": "Belonging answers the question of what he is; it should not be allowed to answer whether the suffering creature deserved protection.", "source_en": "The essay follows Andersen’s 1843 tale, including the mother duck’s early defense and later rejection, the cat and hen’s standards, the farmer’s rescue, and the duckling’s genuine happiness as a swan."},
    {"file": "15_影子坐在前面学者跟在后面_v0.2.md", "slug": "15-shadow", "work_zh": "《影子》", "work_en": "The Shadow", "title_en": "The Shadow Sits in Front and the Scholar Follows: Why Is the Knower No Longer Heard?", "deck_en": "Once public roles decide who represents whom, even a correct answer can become evidence for the wrong person’s authority.", "source_en": "The essay follows Andersen’s 1847 literary tale, retaining the shadow’s acquired status, the scholar’s acceptance of patronage, the princess’s test, the demand that he accept the name ‘shadow,’ and his death."},
    {"file": "16_穿靴子的猫替主人造出一位侯爵_v0.2.md", "slug": "16-puss-in-boots", "work_zh": "《穿靴子的猫》", "work_en": "Puss in Boots", "title_en": "Puss in Boots Invents a Marquis: Why Does Unanimous Testimony Still Fail to Make It True?", "deck_en": "Every witness gives the same answer, but agreement produced by one moving threat is not independent evidence.", "source_en": "The essay follows Perrault’s 1697 tale, retaining the cat’s real hunting, months of gifts, the bathing trick, the peasants’ coerced testimony, the ogre’s death, and the successful marriage."},
    {"file": "17_太阳东边月亮西边_v0.2.md", "slug": "17-east-sun-west-moon", "work_zh": "《太阳东边、月亮西边》", "work_en": "East of the Sun and West of the Moon", "title_en": "East of the Sun and West of the Moon: She Was Asked to Trust without Knowing the Whole Bargain", "deck_en": "Trust cannot carry consequences that one person alone was allowed to understand only after the rule was broken.", "source_en": "The essay follows George Webbe Dasent’s version of the Norwegian tale, retaining the girl’s initial refusal, the incomplete warning, the disclosed one-year term, the three golden gifts, and the prince’s effort to avoid the sleeping draught."},
    {"file": "18_叶限的鱼骨不再回应_v0.2.md", "slug": "18-ye-xian", "work_zh": "《叶限》", "work_en": "Ye Xian", "title_en": "Ye Xian’s Fish Bones Stop Answering: How Did a Private Bond Become a King’s Treasury?", "deck_en": "The bones once answered the girl who fed the fish; after they become royal property, their silence marks a change in the relationship asking for wealth.", "source_en": "The essay follows the Ye Xian passage in Duan Chengshi’s Youyang Zazu sequel, preserving the fish bones’ later silence, burial, intended military use, and disappearance in a sea tide."},
    {"file": "19_快乐王子劝燕子离开_v0.2.md", "slug": "19-happy-prince", "work_zh": "《快乐王子》", "work_en": "The Happy Prince", "title_en": "The Happy Prince Tells the Swallow to Leave: Can Care Preserve the Helper’s Own Destination?", "deck_en": "The prince’s need is real, but he still tells the swallow that help already given does not cancel a life elsewhere.", "source_en": "The essay follows Wilde’s 1888 tale, retaining the prince’s commands, his explicit advice that the swallow fly to Egypt after he becomes blind, the swallow’s renewed choice to stay, and the religious ending."},
    {"file": "20_卷发里凯让公主变得聪明_v0.2.md", "slug": "20-riquet-with-tuft", "work_zh": "《卷发里凯》", "work_en": "Riquet with the Tuft", "title_en": "Riquet Makes the Princess Clever: May Her New Judgment Reconsider Their Marriage?", "deck_en": "A gift of judgment cannot be declared successful only when its recipient reaches the conclusion the giver reserved in advance.", "source_en": "The essay follows Perrault’s 1697 Riquet with the Tuft, focusing on the underground kitchen, the gift of wit, the anniversary objection, Riquet’s reply, the renewed promise, and the tale’s two accounts of beauty."},
    {"file": "21_王子提前烧掉青蛙皮_v0.2.md", "slug": "21-frog-princess", "work_zh": "《青蛙公主》", "work_en": "The Frog Princess", "title_en": "The Prince Burns the Frog Skin Too Soon: How Can Rescue Take Away Her Own Way Out?", "deck_en": "He wants to end his wife’s enchantment, yet acts at the one moment when her knowledge and timing matter most.", "source_en": "The essay follows Afanasyev tale 269, with bread, carpet, feast, the burned skin, the later disclosure of the three-year term, animal helpers, and reunion; it does not import the common three-day variant."},
    {"file": "22_拇指姑娘两次面对燕子的邀请_v0.2.md", "slug": "22-thumbelina", "work_zh": "《拇指姑娘》", "work_en": "Thumbelina", "title_en": "Thumbelina Receives the Swallow’s Invitation Twice: May She Leave in Her Own Time?", "deck_en": "The same invitation can be rightly refused in spring and freely accepted in autumn because the person answering has lived through the months between.", "source_en": "The essay follows Andersen’s 1835 tale, preserving the two invitations, the field mouse’s care and coercion, Thumbelina’s rescue of the swallow, the unresolved butterfly, the flower marriage, wings, and new name."},
    {"file": "23_格蕾特打开哥哥的笼门_v0.2.md", "slug": "23-gretel-opens-cage", "work_zh": "《汉塞尔与格蕾特》", "work_en": "Hansel and Gretel", "title_en": "Gretel Opens Her Brother’s Cage: Why Needn’t the Protected Child Always Wait?", "deck_en": "The sibling who once followed pebbles and reassurance becomes the one who sees the opening, acts, and releases the former protector.", "source_en": "The essay follows the Grimms’ 1857 tale, retaining the father’s participation, pebbles and crumbs, the bone at the cage, Gretel’s oven ruse, the two river crossings, and the return from poverty."},
    {"file": "24_渔夫说自己并不想要_v0.2.md", "slug": "24-fisherman-and-wife", "work_zh": "《渔夫和他的妻子》", "work_en": "The Fisherman and His Wife", "title_en": "The Fisherman Says He Wants Nothing: Why Does Every Wish Still Pass through His Mouth?", "deck_en": "He is not the author of his wife’s desires, but calling himself only a messenger cannot describe everything he does—or loses—their way to the sea.", "source_en": "The essay follows the Grimms’ 1857 tale, preserving the fisherman’s initial unconditional release, the sequence from cottage to pope, the worsening sea, violence at home, and return to the original dwelling."},
    {"file": "25_小裁缝完成了任务国王为什么又加一道_v0.2.md", "slug": "25-brave-little-tailor", "work_zh": "《勇敢的小裁缝》", "work_en": "The Brave Little Tailor", "title_en": "The Tailor Finishes the Task. Why Does the King Add Another?", "deck_en": "A rule that promises recognition after proof can keep moving the finish line until no successful outsider is ever allowed to arrive.", "source_en": "The essay follows the Grimms’ 1857 tale, including the seven flies, the king’s fear after his soldiers resign, the giant, unicorn, and boar tasks, the false battle story, and the failed removal plot."},
    {"file": "26_驴皮公主不再提出下一道难题_v0.2.md", "slug": "26-donkeyskin", "work_zh": "《驴皮公主》", "work_en": "Donkeyskin", "title_en": "Donkeyskin Stops Asking for Impossible Dresses: When Should Refusal Leave the Negotiation?", "deck_en": "When every impossible condition is met, another condition may only keep the refusing person inside a process the other side controls.", "source_en": "The essay follows Perrault’s verse Donkeyskin through an 1826 edition, retaining the three dresses, the threatened craftspeople, the fairy’s failed strategy, the portable chest, escape, ring, and the father’s later attendance."},
    {"file": "27_公主刚为木偶流过眼泪_v0.2.md", "slug": "27-birthday-infanta", "work_zh": "《西班牙公主的生日》", "work_en": "The Birthday of the Infanta", "title_en": "The Infanta Has Just Wept for a Puppet: Why Does She Ask a Dying Person to Keep Performing?", "deck_en": "She can feel sorrow where art tells her to feel it, yet cannot recognize pain when the sufferer falls outside the role of an object made for her pleasure.", "source_en": "The essay follows Wilde’s 1891 literary fairy tale, retaining the puppet show, the dwarf’s forest life, his misunderstanding of the white rose, the mirror, the audience’s renewed applause, and the unrepentant ending."},
    {"file": "短篇01_野天鹅留下了一只翅膀_v0.2.md", "slug": "28-wild-swans", "work_zh": "《野天鹅》", "work_en": "The Wild Swans", "title_en": "The Wild Swans Leave One Wing Behind: Can an Incomplete Recovery Still Be a Happy Ending?", "deck_en": "The unfinished sleeve does not cancel the reunion, and the reunion need not erase the wing that remains.", "source_en": "The essay follows Andersen’s 1838 Wild Swans rather than the Grimms’ Six Swans, retaining the eleven nettle shirts, the rule of silence, the unfinished sleeve, and the youngest brother’s remaining wing."},
    {"file": "短篇02_卡伦终于不再被问起红鞋_v0.2.md", "slug": "29-red-shoes", "work_zh": "《红鞋》", "work_en": "The Red Shoes", "title_en": "Karen Is No Longer Asked about the Red Shoes: May a Life Continue after Admitting Wrong?", "deck_en": "Repentance cannot become a permanent identity in which every new invitation is merely another hearing about the old shoes.", "source_en": "The essay follows Andersen’s 1845 tale, distinguishing the two pairs of red shoes and the two losses of control, and retaining Karen’s severed feet, the pastor’s household, the children’s invitation, and the angel’s changed branch."},
    {"file": "短篇03_大家都说皇帝没有穿衣服以后_v0.2.md", "slug": "30-emperors-new-clothes", "work_zh": "《皇帝的新衣》", "work_en": "The Emperor’s New Clothes", "title_en": "After Everyone Says the Emperor Is Naked: Why Does the Procession Continue?", "deck_en": "Truth becomes public in a moment; changing the conduct organized around the lie still requires another decision from everyone present.", "source_en": "The essay follows Andersen’s 1837 tale, retaining the emperor’s wish to test his officials, the father who carries the child’s words outward, the emperor’s private recognition, and the attendants who keep holding the train."},
]


ENGLISH: dict[str, list[str]] = {
    "01-rumpelstiltskin": [
        "The miller’s boast makes him interesting to the king and makes his absent daughter responsible for proving a miracle. She is locked beside straw and a spinning wheel and told that failure means death. Rumpelstiltskin enters a room whose terms were set before she arrived. His work is real: twice he turns straw into gold, and twice he helps her live until morning.",
        "The third bargain looks like more of the same, but its object has changed. A necklace and a ring belonged to the girl who offered them. Her future child does not. The promise therefore raises a question that ordinary talk about keeping one’s word can conceal: can I bind a person who never asked for the rescue, entered the bargain, or authorized me to place their life inside it?",
        "The queen’s consent matters, but so does the room in which it was given. She understands the demand and chooses immediate survival over an uncertain future. That is a judgment, not the absence of will. Yet the door is locked, the king has threatened her life, and she cannot perform the task herself. A spoken yes does not carry the same authority regardless of the conditions that produced it.",
        "When Rumpelstiltskin returns, the queen does not pretend that no help was given. She offers all the wealth of the kingdom. He refuses because the living child matters more to him than treasure. His attachment may be sincere; sincerity still cannot supply the missing right to take the child. Valuing a life and possessing a claim over that life are different things.",
        "The naming trial creates an escape, not a proof that the original price was just. It also pulls attention away from the first authors of the danger. Rumpelstiltskin loses, but the king keeps the gold, wife, and child; the miller’s boast is never tried. The fairy tale leaves us with a stricter account of responsibility: help should be acknowledged and promises taken seriously, while no promise may silently turn another person into the currency of our survival."
    ],
    "02-little-mermaid": [
        "Before she sees the prince, the little mermaid already wants the world above the sea. She has listened to her sisters describe forests, cities, fragrance, and birdsong. The prince gives that distant world a face, but he does not create her longing from nothing. This matters because her journey cannot be reduced either to foolish romance or to a purely spiritual quest. Love, curiosity, and the hope of an immortal soul become entangled.",
        "The sea witch does not hide the major terms. Legs will feel like knives, return will be impossible, and the prince’s marriage to another woman will mean death. The payment is the mermaid’s voice—the very ability for which she has just been applauded at home. She knows the price in words. What she cannot yet know is how a voiceless life will distribute that price through every ordinary encounter.",
        "On land, the prince cares for her. She rides, climbs, dances, and remains close to him. None of this is false. Yet the relationship cannot hold the story she most needs to tell: where she came from, whom she rescued, what each graceful step costs, and why marriage carries life-or-death stakes for her. Attraction and affection do not automatically become mutual knowledge.",
        "When the prince chooses the woman he believes saved him, the mermaid’s sisters purchase a knife. Killing him would restore her tail and her old life. She refuses without knowing that another future will open. Her love does not entitle her to marriage, and her sacrifice does not make his life a debt. She will not repair her body by making an uninformed sleeper pay for a bargain he never knew existed.",
        "As a Daughter of the Air she gains a voice that human beings cannot hear and a path toward a soul through her own actions. Andersen’s ending remains religious and conditional; it does not return what she lost. Still, the route is no longer confined to one man’s love. Her story asks not whether change is always betrayal, but whether a person can cross into another world while keeping some way for her history, pain, and purposes to be heard there."
    ],
    "03-frog-king": [
        "The princess wants her golden ball back, and the frog names a price: companionship, a place at her table, her cup, and her bed. She promises because she assumes a frog cannot follow her home. The frog retrieves the ball; she runs away. The first wrong is plain enough. She has treated another creature’s help as usable while treating its stated condition as ridiculous.",
        "The king is therefore right to object to deception. He insists that a promise made in difficulty cannot simply be forgotten after the difficulty passes. Yet his command does more than require acknowledgment or repayment. He orders his daughter to admit the frog into bodily and domestic intimacy. A parent can teach honesty without acquiring the authority to assign another person’s bed.",
        "The frog’s request also changes as it enters the palace. Food at the same table, sleep on the same pillow, and permanent companionship are not interchangeable prices. A promise can support demands for explanation, repair, and perhaps the withdrawal of future trust. It cannot turn yesterday’s frightened agreement into unlimited advance consent to closeness.",
        "In the Grimms’ version the princess does not kiss the frog. She throws him against the wall in anger, and the act breaks the enchantment. Magic makes the outcome fortunate. That success cannot serve as a general defense of violence, any more than transformation can make every earlier demand retrospectively welcome. The tale’s mechanism solves the spell without resolving the relations that brought three wills into one room.",
        "Iron Henry’s bands burst with joy as the prince and princess depart. The ending offers restoration and marriage, but it need not close the question. A ball can be returned intact. A relationship cannot be fetched from a well in the same way. If it is to become more than the enforcement of a debt, both people must still be able to answer from where they now stand."
    ],
    "04-bluebeard": [
        "Bluebeard’s wealth and hospitality soften the fear created by his appearance and by the unexplained disappearance of his former wives. After marriage he gives his new wife every key in the house and forbids only one small room. Perrault makes her curiosity explicit. She leaves her guests, nearly falls on the stairs, pauses at the warning, and opens the door without already knowing that someone needs rescue.",
        "That admission does not settle the meaning of the prohibition. Intimacy does not require total access to every room, letter, or memory. Private space can protect a life that remains one’s own inside a relationship. But the room in Bluebeard’s house protects murdered women and allows their murderer to continue. A boundary that conceals ongoing violence cannot borrow all the moral force of ordinary privacy.",
        "The bloodstained key shifts the story from disobedience to survival. The wife lies because the person demanding honesty is holding the power to kill her. Her concealment and Bluebeard’s secret are not symmetrical failures of openness. One hides evidence of discovery while trying to stay alive; the other hides the lives already taken and prepares to add hers to them.",
        "Sister Anne’s view from the tower and the brothers’ arrival reconnect the sealed house to an outside world. Their intervention is not general family revenge against an unwanted marriage. Bluebeard has seized his wife by the hair and raised the blade. The rescue answers an immediate act of killing. It also reminds us that escape often depends on someone beyond the private terms imposed by the person who controls the room.",
        "Perrault appends a warning against curiosity, and a responsible reading should not erase it. Yet the story itself has shown what waits behind the door. Curiosity may explain how the wife entered danger; it cannot explain why Bluebeard may kill anyone who discovers his crimes. His most powerful trick is to redescribe injury as the deserved consequence of breaking his rule. The dead women prevent that rule from having the final word."
    ],
    "05-beauty-and-beast": [
        "Beauty reaches the Beast’s palace because her father has been threatened with death for taking a rose. He objects when she offers to go in his place, but she insists. Her arrival is courageous and chosen within a situation she did not create. The palace is therefore neither a simple kidnapping nor an ordinary courtship. A real decision begins inside a coercive frame.",
        "The Beast feeds her, gives her rooms and books, and asks her to marry him night after night. He accepts each refusal. That restraint matters. So does the continuing fact that Beauty believes her presence is the price of her father’s life. Good treatment can change what a relationship becomes without making the threat at its origin disappear.",
        "When Beauty asks to visit her father, the Beast allows it after she promises to return in a week. Away from the palace, the meaning of return changes. She is no longer merely staying because departure seems forbidden. She sees her family, remains longer than promised, then decides to go back after dreaming that the Beast is dying. The choice now comes from a wider field of possibilities.",
        "The Beast’s refusal to eat is not a clean argument for her love. He does not threaten her with it in advance, but his collapse still places enormous weight on her answer. Beauty finds him near death and agrees to marriage before the transformation. Her affection is directed toward the being she has lived with, not toward a handsome prince revealed as a reward.",
        "Later consent cannot travel backward and make the first threat innocent. The first threat also need not dictate every meaning the relationship later acquires. Beauty’s return is valuable precisely because it is a new answer rather than proof that she always belonged there. The tale lets readers hold both facts: a coercive beginning should be named, and a person may still create a different future from within a history she did not choose."
    ],
    "06-girl-without-hands": [
        "The miller thinks he has promised the stranger an apple tree. Only after riches fill the house does his wife tell him that their daughter had been standing behind the mill. The mistake distinguishes him from a father who knowingly sells his child. But three years pass after he learns the truth, and the bargain’s consequences continue to gather around the person who never made it.",
        "When the devil threatens to take the father instead, he asks his daughter to help and forgive him. She extends her hands. The disturbing fact is not that the story contains no consent; it is that a loving consent becomes part of the machinery of harm. Her refusal would mean watching her father be taken. His fear is real, her wish to save him is real, and only her body is cut.",
        "The devil fails to claim her, but failure arrives after the injury. Her father offers lifelong comfort from the wealth the bargain produced. She leaves instead. Departure does not require proof that he never loved or regretted what he did. It means that compensation cannot be conditioned on the injured person remaining inside the household and future arranged by the beneficiary of the wound.",
        "The king later meets and marries her with silver hands; the tale does not wait for a natural body to return before granting love. Then falsified letters force her to leave a second home with her child. The queen mother saves them by disobeying what she believes is the king’s murderous order, but survival again takes the form of exile. Help can be genuine and still leave a cost for the person helped.",
        "Years later her hands have grown back. The old silver pair helps the king recognize the shared history between the wife he lost and the changed person before him. Recovery is real without deleting the past. Reunion is real without requiring her to become the earlier version he remembers. The ending leaves the first father outside the palace: happiness does not silently complete the explanation he still owes."
    ],
}

ENGLISH.update({
    "07-snow-queen": [
        "Kay’s change does not initially resemble an abduction. A splinter from the mirror enters his eye and heart; roses become ugly, Gerda’s tears ridiculous, and cleverness a pleasure in itself. The Snow Queen later takes him away, but by then he no longer experiences home as something he wants. Gerda sets out to rescue a friend who would not describe himself as waiting to be rescued.",
        "This creates the story’s hardest question. Gerda remembers the boy before the splinters and has good reason to believe something has happened to him. Yet the language of the ‘real Kay’ can become dangerous outside a fairy tale. People change, sometimes away from us. Love cannot claim that every unwelcome change is an enchantment and that one person owns the authoritative version of another’s identity.",
        "Andersen keeps Gerda from becoming a perfectly transparent rescuer. In the old woman’s garden she too forgets. At the palace she mistakes another boy for Kay. She receives help from a crow, a princess, a robber girl, a reindeer, and two women of the North. Her loyalty matters, but it does not make her interpretation infallible or her journey self-sufficient.",
        "When Gerda finally reaches the ice palace, her tears thaw Kay’s heart. Then Kay himself weeps, and the fragment leaves his eye. He looks around and asks where he is. That question is crucial. Rescue is not complete because Gerda has transferred him from the Snow Queen’s possession to her own. It opens a place in which he can again see, remember, and ask.",
        "They return home together and discover that they have grown. Gerda’s devotion does not earn permanent authority over Kay’s future, and his recovery need not be certified by never changing again. The most generous form of her claim—‘this is not all that you are’—ends by returning the next answer to him."
    ],
    "08-nightingale": [
        "The emperor first hears of the nightingale in a foreign book. He is offended that the finest thing in his realm has not been reported to him and orders the court to produce it that evening. A free song in a forest becomes an imperial requirement before the singer has been asked. The kitchen maid, who actually knows where the bird lives, leads the dignitaries outside.",
        "The nightingale agrees to sing at court, and the emperor’s tears become its greatest reward. That feeling is real. The next step is quieter: admiration is translated into residence, title, and twelve ribbons held by servants whenever the bird goes outside. The court calls this protection. It also makes every movement depend on an arrangement the singer did not design.",
        "The jeweled mechanical bird is not worthless. It is beautiful, reliable, and can repeat the tune without needing rest or permission. Its failure comes from being asked to substitute for a living relation rather than from being a machine. Eventually its mechanism wears down, and even careful repair allows only rare performances.",
        "Years later, Death sits beside the emperor while memories of his deeds whisper from the bed curtains. The real nightingale returns through the open window and sings until Death leaves. The emperor asks it to stay. The bird refuses the cage but promises to visit and sing of what happens beyond the palace—provided the visits remain secret. It also asks him not to destroy the mechanical bird.",
        "The rescue does not create a new ownership claim. The nightingale can love the emperor’s tears, save his life, and still retain the right to arrive from elsewhere. A window permits return without guaranteeing it. A cage tries to secure the next song before the singer has chosen it. The tale finally lets the emperor live because he accepts the difference."
    ],
    "09-goose-girl": [
        "On the road to her marriage, the princess loses the cloth bearing her mother’s three drops of blood. Her maid has watched it float away and immediately changes the terms between them. She forces the princess to exchange clothes and horses, then extracts an oath of silence under threat of death. By the time they reach the palace, the first account of who is who already belongs to the person occupying the bride’s place.",
        "The true princess becomes a goose girl. Her silence does not mean she has accepted the theft. That is exactly what coerced silence is designed to produce: observers see no objection and treat the lack of speech as the lack of another fact. Falada, the speaking horse who witnessed the journey, is killed at the false bride’s request. Even so, his head continues to answer the girl beneath the city gate.",
        "Small actions preserve parts of her position. She pays to keep Falada’s head where she can see it and calls the wind to protect her hair from Conrad. Those powers do not make her responsible for solving the whole danger alone. The fact that someone can resist in one place is not evidence that no one else needs to notice, investigate, or help.",
        "The old king listens to Conrad’s complaint, observes the girl, and asks what troubles her. She still cannot tell him. He suggests that she speak into an iron stove, then secretly listens through the flue. The device saves her. It is also eavesdropping she did not knowingly authorize. A helpful result does not make every means of obtaining a vulnerable person’s speech harmless.",
        "Truth enters through several imperfect routes: a dead horse, an irritated boy, a king willing to look beyond the first explanation, and finally speech addressed to a place rather than a person. The tale then restores rank and delivers a brutal punishment. Its more lasting insight comes earlier. When someone cannot directly tell what happened, listening may need to begin with the traces around the silence rather than with a demand that the speaker become louder."
    ],
    "10-hunter-and-tortoise": [
        "A hunter discovers a tortoise singing and playing a small harp in the forest. He returns because the song is beautiful. When he asks to bring her home, she agrees on one condition: she will sing for him alone. The arrangement changes her location without changing the audience she has authorized. At first, the hunter receives exactly the private companionship he requested.",
        "Then possession begins to look like reputation. He tells others about the marvelous singer, and the story reaches the chief. When the assembly laughs, the hunter promises to produce a performance and stakes his life on it. His report is true. What he does not possess is the tortoise’s agreement to demonstrate that truth before a crowd.",
        "The people wait patiently while he pleads. Their patience does not address the actual condition. They assume that the performance is owed and that kindness consists in allowing more time for it to happen. But ‘not yet’ and ‘not for you’ are different answers. Repeatedly waiting for compliance can remain a way of refusing to hear refusal.",
        "At sunset the hunter is executed. Only then does the tortoise sing and explain that he caused his fate by exposing her secret and turning her into a spectacle. She identifies a real betrayal. Still, the assembly chose a lethal test of truth and carried it out. His reckless wager does not turn their decision into a natural event for which no one else must answer.",
        "The tortoise’s silence should not be converted into an uncomplicated triumph of boundaries; the tale never fully tells us what she knew about the wager. Nor may the hunter use danger he created to manufacture her duty to perform. The tragedy grows because every participant treats the stage as already narrowed to two outcomes. The original permission—‘I will sing for you’—was a relation, not a transferable right to her voice."
    ],
    "11-three-spinners": [
        "The three spinners enter at the wedding, each bearing the bodily mark she says spinning has produced: a broad foot, a hanging lip, an enlarged thumb. The bride greets them publicly as relatives. The prince is embarrassed by guests who seem unfit for his beautiful wife. He does not yet know that every room of flax he admires was completed by their labor.",
        "The deception begins earlier. The girl dislikes spinning; her mother beats her, then tells a passing queen that the daughter spins so obsessively the family cannot afford enough flax. The queen carries the girl to the palace and offers marriage to her son if she completes impossible quantities. What looks like recognition of skill is already recognition built on a lie.",
        "The three women offer rescue on a specific condition: they must be invited to the wedding and treated as kin. They do not demand the girl’s child, future, or body. They ask not to vanish once their work has generated her new position. Their request is modest in material terms and difficult in social terms, because their presence disrupts the polished story of the talented bride.",
        "The girl still conceals the subcontracting. Public kinship acknowledges the helpers without telling the prince everything. The tale does not supply a perfectly transparent solution. It does, however, refuse the cleanest injustice: a success in which the workers disappear at the door while the beneficiary alone receives admiration.",
        "The prince sees the spinners’ bodies and forbids his wife ever to spin again. His response frees her from the labor while leaving every other woman where she was. Even this narrow change depends on the helpers being visible. The wedding feast becomes a place where the cost of admired production sits down beside its result."
    ],
    "12-rapunzel": [
        "Rapunzel’s tower has no door and no stairs. It is nevertheless easy for the witch to enter: call the girl’s name, ask for her hair, and climb. The repeated ritual resembles knocking, except that only the visitor possesses a route in both directions. Accessibility for the keeper coexists with confinement for the person inside.",
        "The prince observes the ritual and climbs without invitation. That first entry should not be rewritten as consent simply because affection later develops. Surprise gives way to conversation; conversation gives way to Rapunzel’s agreement and to her own plan for a ladder woven from silk. The distinction matters. A relation can change after an uninvited beginning, but the beginning remains what it was.",
        "Hair is an ambivalent road. It belongs to Rapunzel’s body and connects her to the world, yet everyone else uses it to move. The witch cuts it and turns it into a trap for the prince. He leaps from the tower and loses his sight. The route that never allowed Rapunzel to leave is still available for others to use against one another.",
        "Rapunzel has meanwhile been expelled into the wilderness. Years later the prince hears her singing and walks toward the voice on the ground. Her tears restore his sight; reunion does not return either person to the tower. They meet after each has lived through a separate landscape the other could not control.",
        "The famous braid is often remembered as the device by which Rapunzel is found. Being found is not enough. A person needs more than a path others can use to reach her; she needs a path by which she can enter the world herself. The happy ending begins only after the window ceases to be the sole direction of the relationship."
    ],
})

ENGLISH.update({
    "25-brave-little-tailor": [
        "The king’s soldiers find two dead giants and the wrecked forest around them. The little tailor returns to claim the promised princess and half the kingdom. The king answers with another requirement: capture the unicorn. When that is done, a wild boar remains. The contract has a finish line in language and no finish line in practice.",
        "The king’s fear did not begin as pure prejudice. He welcomed the apparent warrior, then watched his own soldiers resign rather than serve beside a man they believed had killed seven at one blow. Keeping the tailor now seemed dangerous. Yet instead of revising the agreement openly, the king preserved the language of merit while using new tests as an instrument of removal.",
        "The tailor survives because he is better at problems than the rule expects. He turns the giants against each other, traps the unicorn in a tree, and locks the boar in a chapel. Each task contains a real end. The king’s evaluation does not. Proof fails not because it is weak but because recognition was never the actual purpose of asking for it.",
        "The tailor’s own claim began in ambiguity. ‘Seven at one blow’ referred to flies, and he allows others to imagine soldiers. He later invents a battle story. Exposing the moving goalposts does not make him transparent or establish that marriage is owed as an ordinary prize. Several kinds of deception can coexist without becoming equal.",
        "After the wedding, the king tries once more to have him carried away. The plan fails, and the tailor remains king. The comedy is satisfying because ingenuity outlasts power. Its institutional question is sharper: when a system promises that achievement will earn entry, can anyone actually arrive, or will each completed test merely reveal the next reason the gatekeeper wanted them outside?"
    ],
    "26-donkeyskin": [
        "Donkeyskin’s first strategy is negotiation through impossibility. To avoid marrying her father, the princess asks for a dress the color of the sky, then the moon, then the sun. Each garment appears. The craftsmen’s achievement is splendid; for her it is terrifying, because every solved problem carries her closer to the answer she has already refused.",
        "The fairy adviser devised the conditions and expected them to work. When they fail, the princess does not owe the strategy endless loyalty. A difficult requirement can delay an unwanted outcome, but it also keeps the refusing person inside a process whose basic premise belongs to the other side: if he eventually meets the condition, she must consent.",
        "Her father’s prized donkey supplies the final demand. Its skin is delivered too. At that point the fairy changes direction and helps the princess flee, carrying dresses and resources in a chest that can follow her. Departure is not a louder bargaining position. It is an end to bargaining over something that was never available for exchange.",
        "The escape has costs. She hides under the skin, works in degradation, and lives far below her former rank. Later recognition through the ring and dresses opens another future. None of this makes flight easy or proves that leaving always provides safety. It shows why a person may need practical resources and another’s help before refusal can cease to be merely one more sentence spoken inside captivity.",
        "Perrault eventually brings the father to the new wedding after he has abandoned the desire that caused the danger. The ending allows change without requiring the daughter to remain nearby while he changes. The crucial moment came earlier: she stopped inventing a fourth impossible condition and walked out of the place where her no was being treated as an invitation to try harder."
    ],
    "27-birthday-infanta": [
        "At the puppet play, the Infanta’s eyes fill with tears. Wooden and wax figures suffer convincingly; children need sweets to recover, and adults praise the pathos. The court clearly possesses the language of pity. Minutes later, a living performer collapses before the princess, and the same audience decides that his pain is an especially amusing part of the show.",
        "The dwarf has grown up in the forest, loved by animals and unaware that the court has hired him because of his body. He reads laughter as admiration and the Infanta’s white rose as affection. His error is not stupidity. He has been placed in a world whose signals are organized around entertainment, while no one tells him the role assigned to him.",
        "A mirror supplies the knowledge the audience withheld. He sees his appearance, connects it to their laughter, and realizes that the princess never regarded him as a possible companion. This discovery does not mean she owed him love. No one owes romance in exchange for performance or suffering. What he was owed was not to have his personhood converted into a joke whose terms only the spectators understood.",
        "When he falls, the children ask him to dance again. The Infanta wants the performer who ‘acts’ heartbreak so well to return at her next celebration. Her earlier tears were not false; they were trained toward an object safely designated as tragic. A living person outside that frame cannot enter the same response.",
        "The dwarf need not possess noble birth, hidden beauty, or reciprocated love to be lifted from the floor and treated as someone whose performance has ended. The story’s coldness lies not in an inability to recognize sorrow. It lies in allowing sorrow to count only where the court has already decided that feeling it will cost nothing."
    ],
    "28-wild-swans": [
        "At the execution ground, Elisa is still weaving the last of eleven nettle shirts. Ten are complete; the final one lacks a sleeve. She throws them over the swans as the executioner reaches for her. Her brothers return to human form, except that the youngest keeps one wing.",
        "The missing sleeve does not make the rescue false. Nor must the remaining wing be redescribed as secretly better than an ordinary arm in order to preserve a happy ending. Incomplete recovery can contain joy, loss, survival, and an unknown future without forcing any one of them to cancel the others.",
        "Fairy tales often seem to promise restoration to an original state. Andersen stops one stitch short. Elisa can speak again and reunite with her brothers, while the youngest brother carries visible evidence of what time and danger did not permit her to finish.",
        "The story gives no later account of the wing. We need not invent resentment, gratitude, cure, or heroic symbolism for him. A good ending can make room for an unanswered life. The reunion is already real; it does not have to wait for the last feather to disappear."
    ],
    "29-red-shoes": [
        "When the angel appears to Karen a second time, the sword has become a green branch covered with roses. This is the same figure who earlier condemned her to dance as a warning to proud children. The tale’s movement toward mercy does not erase punishment; it changes whether punishment will be allowed to occupy every remaining meaning of her life.",
        "Karen has admitted wrongdoing and endured bodily catastrophe. Still, she cannot enter the church because the red shoes dance before her. She works in the pastor’s home instead. The children there ask her to walk with them—not because they have ruled on her entire past, but because she is someone with whom an ordinary afternoon might be shared.",
        "That invitation matters before the miracle. Repentance becomes another form of captivity when a person must forever appear only as the name of the thing regretted. Taking responsibility need not mean surrendering the possibility of new relations, work, affection, and action that are not hearings about the old offense.",
        "Andersen’s conclusion is explicitly Christian and occurs in death, not in bodily recovery. Readers need not translate it into a therapeutic formula. Its narrower human question remains: after wrongdoing has been named, can a community leave room for the wrongdoer to become more than the story of the red shoes?"
    ],
    "30-emperors-new-clothes": [
        "The child has spoken. His father repeats the words; the whisper moves through the crowd until everyone is shouting that the emperor has nothing on. The truth is no longer private, obscure, or punishable only as one child’s mistake. The emperor himself suspects that the people are right.",
        "And then the procession continues. The emperor straightens himself and walks on. The chamberlains keep their hands beneath a train that does not exist. Public knowledge has changed, but the coordinated action built around the lie retains momentum.",
        "This is why exposure and transformation are different events. A fact can become undeniable without supplying a new role for the emperor, a safe way for officials to stop, or a shared decision about what happens next. None of those difficulties makes the truth unimportant. They explain why truth does not act by itself.",
        "Andersen gives us no arrest, revolution, reform, or honest morning after. The unfinished ending protects the responsibility of everyone in the scene. The child opens a place from which the truth can be said. He cannot also lower every raised hand or decide when each adult will stop carrying the invisible cloth."
    ],
})

ENGLISH.update({
    "19-happy-prince": [
        "The swallow reaches the city late. He has already delayed migration for a summer attachment and now intends to sleep one night beneath the golden statue before flying to Egypt. The Happy Prince’s tears interrupt that plan. From his high place the statue sees suffering he could not see while alive inside the palace and asks the bird to carry away his ruby.",
        "One night becomes another. The prince asks for his sapphire eyes and then for the gold covering his body. The requests often take the form of commands, and the growing need is genuine. The swallow can reach rooms and streets the statue cannot. Care therefore develops under pressure from both compassion and time.",
        "After giving up his second eye, the prince is blind. He explicitly tells the swallow to leave for Egypt. The bird chooses to remain and become his eyes. That exchange is easy to miss because the sacrifice continues, but it changes the relation. Need does not automatically claim the helper’s whole future; the person receiving help can still protect the possibility of departure.",
        "The swallow’s repeated choices are not isolated from attachment, cold, or the prince’s suffering. Freedom does not mean a decision made without reasons or bonds. It means those reasons do not become a standing license for someone else to speak the decision in advance. The prince can want him to stay and still say that what has already been given is enough.",
        "The swallow dies at the statue’s feet, and the prince’s lead heart breaks. Wilde’s religious ending calls them the city’s two most precious things. We need not convert their deaths into a rule that true care must consume the carer. The most portable part of their relationship may be the sentence spoken before the final choice: you have helped me, and you may still go where your own life was headed."
    ],
    "20-riquet-with-tuft": [
        "A year after Riquet gives the princess wit, she walks into the forest to consider several proposals. The ground opens onto a kitchen preparing an enormous wedding feast. It is for her marriage to Riquet, scheduled from the promise she made before she possessed the judgment she now uses in every other part of life. He has remembered the date she has forgotten.",
        "Riquet’s gift has worked. The court values her counsel; princes seek her hand; she can compare temperaments, arguments, and possible futures. Precisely because the gift is real, the old bargain becomes harder rather than easier. If her new intelligence may judge affairs of state and every other suitor but not the condition attached to its own giving, one door in thought has been sealed for the giver.",
        "The princess says she may not want the marriage. Riquet’s reply also deserves weight. Why should a thoughtful person lose the benefit of a promise more readily than a rude one? He has organized his hope around her word. Listening to an objection should not require him to pretend that expectation, hurt, and trust never existed.",
        "The difficulty cannot be solved by assigning all reason to one side. She owes an answer to the promise; an answer is not identical with marriage as compensation. He may describe what her change costs him; his loss does not reserve the conclusion of her newly capable judgment. A gift of thought becomes self-defeating if success means only that its recipient now agrees more intelligently with the giver.",
        "Perrault offers two explanations for Riquet’s transformation: magic makes him beautiful, or love changes how she sees him. In either case, the princess promises again after their argument. The outcome resembles the old bargain but now includes a present answer. The hesitation is not wasted time. It is the moment in which the capacity he gave her is finally allowed to enter the decision that matters most to her."
    ],
    "21-frog-princess": [
        "At the feast, Vasilisa pours wine into one sleeve and bones into the other. A lake and swans appear when she moves her arms. Ivan’s brothers’ wives imitate the visible actions and produce only spilled drink and flying bones. The scene establishes that Vasilisa knows how to work inside her enchantment. Ivan has repeatedly benefited from knowledge he does not possess.",
        "He sees her human form and hurries home to burn the frog skin. His motive is understandable. He wants the humiliating condition gone and assumes that destroying its object will release her permanently. Rescue often looks most decisive when it removes the sign of captivity. Here the same act destroys the method and timing that belong to the person living through the spell.",
        "Vasilisa says that if he had waited a little longer, she would have been free. Only later does an old man explain the three-year term. Ivan may not have known the rule, but ignorance does not make unilateral intervention neutral. It should have made her knowledge more important, especially after she had solved each impossible task without asking him to take over.",
        "Ivan then travels, receives help from animals he once spared, and eventually defeats Kashchei. His effort is real. The long repair does not prove that the first act was wise; it shows what must happen after an urgent attempt at rescue has made another person’s situation worse.",
        "The tale rewards persistence and grants reunion. Its quieter lesson concerns collaboration. Wanting someone free is not the same as knowing the route by which she can become free. At the moment when Vasilisa’s timing mattered most, Ivan treated the skin as the whole problem and lit the fire alone."
    ],
    "22-thumbelina": [
        "In spring, the swallow asks Thumbelina to leave the field mouse’s underground home. She refuses. The mouse sheltered her through winter, and leaving secretly would cause pain. The swallow departs without turning her gratitude into proof that she belongs below ground forever—or turning her refusal into the loss of any future invitation.",
        "During the following months, care becomes control. The field mouse arranges a marriage to the mole, praises his security, and treats Thumbelina’s sorrow as ingratitude. The mole has food and a large house but dislikes sun and flowers. A life can be materially safe and still be wrong for the person expected to inhabit it.",
        "Thumbelina also changes through action. She once nursed the frozen swallow while believing him dead; she now learns that he can carry her beyond the fields. The autumn invitation is not identical to the spring invitation because the person answering has lived through a summer of narrowing choices. Timing belongs inside consent.",
        "She says yes and flies away. In the land of flowers she accepts another marriage, receives wings, and is given a new name. The tale does not invite a simple rule that every offered future should be accepted once it looks beautiful. It shows several responses made in different conditions, none of which automatically owns the next.",
        "The swallow leaves again after bringing her to a place where she can live. Help is not invalidated when companionship ends. Their relation survives a refusal, later supports a departure, and concludes without either party claiming the other as the reward. That is why the two invitations can remain equally important."
    ],
    "23-gretel-opens-cage": [
        "When Gretel opens the cage, Hansel jumps out like a bird. Earlier he had comforted her, gathered white pebbles, and led them home by moonlight. He occupied the position of the child who knew what to do. At the witch’s house the roles do not simply reverse; they become less fixed. The protected child sees and creates the decisive opening.",
        "Their parents’ abandonment matters because childhood agency does not erase adult responsibility. Hansel and Gretel solve dangers that should never have been assigned to them. Praising their resourcefulness must not turn deprivation into an educational program that was good for them.",
        "Inside the house, Hansel uses a bone to delay the witch’s plan, while Gretel is forced to work. Then the witch orders Gretel into the oven. Gretel pretends not to understand and asks for a demonstration. She does not wait for the former protector to produce one more plan; she acts from her own reading of the immediate danger.",
        "After freeing Hansel, the two still need each other. The duck carries them across the river one at a time. Neither sibling becomes the permanent hero whose competence makes the other unnecessary. Their survival is assembled from different acts at different moments, including help from outside the pair.",
        "Opening the cage does not diminish the path of pebbles. It completes a relation in which care can move. A person who has once needed reassurance need not remain forever in the waiting position, and a person who once led the way need not defend that identity when another now sees what must be done."
    ],
    "24-fisherman-and-wife": [
        "Each time the fisherman approaches the sea, he adds distance to the request: his wife wants something, but he does not. Cottage, palace, kingship, empire, papacy—every wish nevertheless reaches the fish through his voice. Calling himself a messenger identifies something true about authorship. It does not finish the account of his participation.",
        "At first he goes because refusing means returning to conflict at home. As the demands grow, so does his dread. The sea darkens before the household openly becomes violent. His wife eventually kicks him and orders him into the storm. It would be shallow to describe each journey as a free endorsement of her desire.",
        "It would also be shallow to treat him as pure conduit from the beginning. He speaks, receives each transformed world, inhabits it, and returns to ask again. There are earlier points at which resistance would have cost less than it later does. Seeing those points should not become an accusation that a frightened person could always have stopped escalation without danger.",
        "The fish repeatedly grants requests without asking what has changed between the people making them. Magical abundance therefore expands the household’s power without changing the way decisions are produced. More capacity does not repair the relation that determines whose desire becomes action.",
        "The final wish returns the couple to the old dwelling. The tale neither separates them nor gives us their later explanation. What remains is a gradual loss of room. The fisherman’s refrain—‘I do not want this’—should be heard as evidence of pressure, but also as an incomplete sentence. Between wanting and doing lies the history of what he could say, what he said, and what became harder to refuse each time."
    ],
})

ENGLISH.update({
    "13-cinderella": [
        "Before the ball, Cinderella’s stepsisters ask her how they should dress and let her arrange their hair. They already know she has taste and skill. In the same room they mock the idea that someone covered in ashes might attend beside them. Her ability is useful when attached to their appearance and ridiculous when attached to her own desire to be seen.",
        "Perrault’s fairy godmother does not create Cinderella’s judgment, generosity, or wish to go. She creates access: clothing, transport, an introduction, and a limited span of time in which existing qualities can become publicly legible. Opportunity matters precisely because worth and recognition do not arrive together by themselves.",
        "At the ball, clothes change what everyone is prepared to notice. This does not mean appearance is irrelevant or that the prince would have recognized the same person in any condition. The story is frank about the social machinery of visibility. It also shows that the machinery has not manufactured the whole person it finally displays.",
        "The slipper then supplies a repeatable test. It is more reliable than memory of a dazzling stranger, but even it does not stand alone: the second shoe confirms the first, and the woman wearing them can speak and act. An identifying object can open a route to recognition without exhausting the identity it helps establish.",
        "Perrault’s morals praise grace and useful assistance. We need not choose between them. Cinderella had qualities before the carriage, and qualities without a door may remain invisible. The slipper answers who attended the ball. It should not be allowed to answer when she first became a person whose hopes and abilities counted."
    ],
    "14-ugly-duckling": [
        "The mother duck’s earliest defense is also the tale’s simplest moral fact. She does not yet know that the awkward gray hatchling is a swan. She says only that he has harmed no one. Protection at that moment cannot be justified by hidden beauty, future prestige, or belonging to a superior species. It responds to the creature before any redeeming identity has been discovered.",
        "The yard soon organizes itself around appearance and usefulness. Other birds bite him; his siblings wish him gone. Later a cat and a hen treat egg-laying and purring as the full inventory of meaningful ability. Because he can do neither, his love of open water appears not merely different but foolish.",
        "Discovery changes something real. Seeing the swans and finally seeing his own reflection explains desires and differences that had remained unintelligible. Belonging is not an illusion. It can release a person from spending every day under a standard built for someone else. The danger lies in using the later discovery to rewrite the earlier cruelty as a reasonable mistake.",
        "Children run toward the new swan, and he initially thinks they mean to hurt him. Their delight cannot instantly remove what repeated treatment has taught him to expect. Nor does their praise prove that beauty is the basis on which kindness should have been granted. The farmer who saved him in winter did not need the final revelation first.",
        "The ending is genuinely happy, and Andersen lets the swan say he never dreamed of such joy. We can celebrate that recognition while keeping the mother duck’s first defense in view. The suffering hatchling, the useless guest, and the creature who did not know his own name already had a claim not to be bitten."
    ],
    "15-shadow": [
        "A princess tests the learning of the elegant stranger she may marry. The person introduced as his shadow answers brilliantly. She does not conclude that the speaker is impressive. She concludes that a man whose shadow knows so much must be greater still. Nothing false has been said in the answer; its authorship has been reassigned before the knowledge reaches her.",
        "Andersen makes the metaphor literal. Years earlier, the scholar’s shadow separated from him, acquired clothes, wealth, secrets, and social fluency, then returned as an independent gentleman. The scholar does not demand ownership. He accepts the shadow’s freedom and agrees to keep its origin private. That recognition could have begun a relation between two beings with different lives.",
        "Instead, economic dependence rearranges their positions. The shadow funds a journey, walks in front, controls forms of address, and lets spectators read the scholar as an attendant. Each concession appears survivable by itself. Together they create a public grammar in which later testimony will already be sorted: one is the person, the other is the person’s shadow.",
        "The princess’s questions therefore intensify the mistake. Every correct response from the scholar proves, within the shadow’s story, how generous and accomplished the master must be. When the scholar objects, the shadow calls him mad. Silence confirms subordination; resistance confirms illness. The content of his speech no longer has a route into judgment.",
        "The city celebrates the marriage after the scholar is killed. No witness or providence arrives to restore moral balance. The cruelty is not merely that knowledge goes unrewarded. The scholar loses the standing to say, ‘I spoke this sentence; I lived this life.’ Once everyone accepts the label, his disappearance no longer registers as the absence of a person."
    ],
    "16-puss-in-boots": [
        "As the king’s carriage passes a meadow, workers say the land belongs to the Marquis of Carabas. At the wheat fields, harvesters give the same answer. Agreement accumulates along the road until the young miller’s son appears to possess an estate. Yet every witness has been visited first by the cat and threatened with being chopped into pieces if the wrong name is spoken.",
        "The testimony is not independent. It is one command moving through many mouths. Counting speakers therefore cannot tell us how much evidence exists. A crowd may repeat a claim for different private reasons, for the same organized reason, or because each person sees the others already complying.",
        "The cat’s achievement is not entirely imaginary. He really hunts, brings gifts for months, reads the king’s route, obtains clothes for his master, and defeats the shape-shifting ogre through nerve and timing. Skill and deception are intertwined. Exposing the false title does not require pretending that nothing difficult was accomplished.",
        "The master’s participation also grows. He does not know the bathing plan in advance, but he accepts the clothes, receives the princess’s genuine interest, and later speaks as owner of land he did not possess. A person can begin as the beneficiary of someone else’s scheme and gradually become an agent inside it.",
        "By the time the castle appears, each earlier answer seems to confirm the next. The king’s belief gives the witnesses’ statements authority; those statements make the king’s belief look well founded. A marquis is produced through a chain in which no single voice has to invent the whole lie. The fairy tale’s comedy leaves a serious warning: unanimity is not yet truth until we know what made the voices agree."
    ],
    "17-east-sun-west-moon": [
        "The girl is told not to follow her mother’s private advice, or misfortune will come. She is not told that the bear who shares her bed is a prince, that his enchantment ends after one year, or that seeing his face too soon will force him to marry a troll princess. Only after the candle wax falls does the full meaning of trust become available—at the exact moment it is too late to use it.",
        "The prince’s predicament is real, and magic may limit what he can safely reveal. But the tale never clearly says that he is forbidden to explain. Readers often supply that rule because it would make the bargain feel fairer. The omission matters. Asking someone to bear a consequence while reserving the consequence’s structure to oneself is not a shared agreement.",
        "The girl nevertheless takes responsibility for what she can do next. She travels beyond ordinary maps, receives help from three women and the winds, and reaches the castle east of the sun and west of the moon. Three golden objects buy three nights near the prince. For the first two, the troll princess drugs him, and the visitor’s voice cannot wake him.",
        "Prisoners in the neighboring room tell the prince that a woman has been weeping beside him. On the third night he refuses the drink. This small act changes the rescue. He is no longer merely an object she must retrieve through endurance. He receives information, revises his own behavior, and becomes able to hear the person who has crossed the world to reach him.",
        "The first light reveals his face and destroys their home. The later waking makes a joint departure possible. Trust is not strongest when one person knows and the other obeys. It becomes a relation when information, risk, and action can move between them, allowing both to participate in the future they are trying to save."
    ],
    "18-ye-xian": [
        "Ye Xian feeds a small fish with food saved from her own portion. It grows until no bowl can hold it and must be moved to a pond. The fish surfaces for her and hides from others. Before bones, gold, and royal discovery enter the story, there is already a relationship recognizable through repeated, different responses.",
        "Her stepmother kills the fish. A mysterious visitor later tells Ye Xian to gather the bones and ask them for what she needs. The bones provide clothing for the festival; a lost golden shoe eventually brings the king to her. These transformations are often grouped into a single ladder from oppression to marriage. The text continues after that apparent happy ending.",
        "The king takes the bones home with Ye Xian and repeatedly asks them for treasure. They answer with limitless gold and jewels. What once responded inside a relation of feeding and recognition becomes a resource in the royal household. The change is not only that a more powerful owner has arrived. The request itself is no longer embedded in the same history.",
        "After a year, the bones stop answering. The king buries them beside the sea. When military unrest later creates need, he intends to use the stored treasure for the army, but a tide carries it away. The source does not explain who sends the wave or why the bones fall silent. Supplying a tidy punishment would close what the tale leaves open.",
        "The sequence invites attention to the person asking. The fish once placed its head near the girl who had kept it alive; later the court waits for repeated extraction. Care does not establish permanent ownership of every future gift, but neither is the early relation irrelevant. The bones’ silence marks the point at which power can preserve an object while losing the answer that once made it meaningful."
    ],
})


CHAPTERS = [
    ("01", "Promises, Prices, and People Written into Bargains", "承诺、价格与被写进约定的人", range(0, 6)),
    ("02", "Rescue, Voice, and the Right to Refuse", "救援、声音与仍可拒绝", range(6, 10)),
    ("03", "Being Seen, Named, and Represented", "被看见、被命名与被代表", range(10, 16)),
    ("04", "Knowing, Helping, and Answering Again", "知情、帮助与重新回答", range(16, 22)),
    ("05", "Who Finishes the Story and Bears Its Cost", "谁完成故事，谁承担后果", range(22, 27)),
    ("CODA", "Three Things Fairy Tales Leave Unfinished", "童话没有说完的三件事", range(27, 30)),
]


class TraditionalConverter:
    def __init__(self) -> None:
        self.cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
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
        self.transform = self._string("Hans-Hant")

    def _string(self, value: str) -> int:
        result = self.cf.CFStringCreateWithCString(None, value.encode("utf-8"), UTF8)
        if not result:
            raise ValueError("CoreFoundation could not create a string")
        return result

    def convert(self, value: str) -> str:
        mutable = self.cf.CFStringCreateMutable(None, 0)
        source_ref = self._string(value)
        try:
            self.cf.CFStringAppend(mutable, source_ref)
            if not self.cf.CFStringTransform(mutable, None, self.transform, 0):
                raise ValueError("CoreFoundation Hans-Hant transform failed")
            length = self.cf.CFStringGetLength(mutable)
            capacity = self.cf.CFStringGetMaximumSizeForEncoding(length, UTF8) + 1
            buffer = ctypes.create_string_buffer(capacity)
            if not self.cf.CFStringGetCString(mutable, buffer, capacity, UTF8):
                raise ValueError("CoreFoundation could not export transformed text")
            result = buffer.value.decode("utf-8")
            for source, target in {
                "余项": "餘項", "余響": "餘響", "里凯": "里凱", "秦汉": "秦漢",
                "这里": "這裡", "那里": "那裡", "故事里": "故事裡", "房里": "房裡",
                "宫里": "宮裡", "家里": "家裡", "手里": "手裡", "眼里": "眼裡",
                "水里": "水裡", "城里": "城裡", "心里": "心裡", "划定": "劃定",
                "身份": "身分", "余食": "餘食", "系在": "繫在", "系到": "繫到",
                "系住": "繫住", "系得": "繫得",
            }.items():
                result = result.replace(source, target)
            result = result.replace("里", "裡")
            for source, target in {
                "克裡斯蒂安": "克里斯蒂安",
                "瓦西裡薩": "瓦西里薩",
                "裡凱": "里凱",
            }.items():
                result = result.replace(source, target)
            return result
        finally:
            self.cf.CFRelease(source_ref)
            self.cf.CFRelease(mutable)

    def close(self) -> None:
        self.cf.CFRelease(self.transform)


def inline_markdown(value: str) -> str:
    escaped = html.escape(value, quote=True)
    return re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        escaped,
    )


def source_copy(item: dict[str, str]) -> tuple[str, list[str], str, str]:
    raw = (SOURCE / item["file"]).read_text(encoding="utf-8").strip()
    blocks = [block.strip() for block in re.split(r"\n\s*\n", raw)]
    title = blocks[0].removeprefix("# ")
    divider = blocks.index("---")
    body = blocks[1:divider]
    note = blocks[divider + 1].strip("*")
    match = re.search(r"\]\((https?://[^)]+)\)", note)
    if not match:
        raise ValueError(f"Missing source link in {item['file']}")
    return title, body, note, match.group(1)


def paragraph(value: str, *, italic: bool = False) -> str:
    copy = inline_markdown(value)
    return f"<p><em>{copy}</em></p>" if italic else f"<p>{copy}</p>"


def language_script() -> str:
    return """<script>(function(){var q=new URLSearchParams(location.search).get('lang');var saved=q||localStorage.getItem('nd_lang')||localStorage.getItem('nondubito-lang')||'zh';if(['en','zh','zh-hant'].indexOf(saved)===-1)saved='zh';document.documentElement.dataset.lang=saved;document.documentElement.lang=saved==='zh-hant'?'zh-Hant':(saved==='zh'?'zh-Hans':'en');document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('[data-lang-button]').forEach(function(b){b.classList.toggle('active',b.dataset.langButton===saved);b.addEventListener('click',function(){saved=b.dataset.langButton;document.documentElement.dataset.lang=saved;document.documentElement.lang=saved==='zh-hant'?'zh-Hant':(saved==='zh'?'zh-Hans':'en');localStorage.setItem('nd_lang',saved);localStorage.setItem('nondubito-lang',saved);document.querySelectorAll('[data-lang-button]').forEach(function(x){x.classList.toggle('active',x.dataset.langButton===saved)})})})})})();</script>"""


def page_head(title: str, description: str, canonical: str) -> str:
    return f'''<!DOCTYPE html><html lang="zh-Hans" data-lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{html.escape(title)} — Non Dubito</title><meta name="description" content="{html.escape(description, quote=True)}"><meta name="author" content="Han Qin (秦汉)"><meta property="og:type" content="article"><meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta name="twitter:card" content="summary"><link rel="canonical" href="{canonical}"><link rel="icon" type="image/svg+xml" href="../../../../favicon.svg"><link rel="stylesheet" href="../../../../style.css"><link rel="stylesheet" href="../stories.css">{language_script()}<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script></head>'''


def site_header() -> str:
    return '''<body><header><div class="header-inner"><a href="../../../../index.html" class="site-title"><span class="title-latin">Non <span>Dubito</span></span><span class="title-sub">Essays in the Self-as-an-End Tradition</span></a><nav><a href="../../../../index.html">Essays</a><a href="../../../../start.html">Start Here</a><a href="../../../../library.html" class="active">Library</a><a href="https://credesivis.org/index.html">Crede si vis</a><a href="../../../../about.html">About</a><a href="https://self-as-an-end.net" target="_blank" rel="noopener">SAE Theory ↗</a><a href="https://hqin.substack.com" target="_blank" rel="noopener">Substack ↗</a></nav></div></header>'''


def language_toggle() -> str:
    return '''<div class="lang-toggle" aria-label="Language selector"><button class="lang-btn" data-lang-button="en">EN</button><span class="lang-sep">|</span><button class="lang-btn" data-lang-button="zh">中文</button><span class="lang-sep">|</span><button class="lang-btn" data-lang-button="zh-hant">繁體</button></div>'''


def footer() -> str:
    return '''<footer class="site-footer"><div class="footer-inner"><div class="footer-brand"><div class="footer-logo">Non <span>Dubito</span></div><div class="footer-tagline">Thought has no mother tongue</div></div><div class="footer-langs"><a href="../../../../library.html" class="footer-lang">Library</a><a href="../../../../start.html" class="footer-lang">Start Here</a><a href="https://self-as-an-end.net" class="footer-lang" target="_blank" rel="noopener">SAE Theory</a></div><div class="footer-copy">© 2026 Han Qin · Non Dubito</div></div></footer></body></html>'''


def localized_article(
    lang: str,
    item: dict[str, str],
    index: int,
    title: str,
    work: str,
    body: list[str],
    source_note: str,
    converter: TraditionalConverter,
) -> str:
    total = len(ITEMS)
    labels = {
        "en": ("Structures in Fairy Tales", "Essay", "Previous essay", "Next essay", "This essay begins with a story rather than theoretical vocabulary. Continue through the", "Stories and Structures shelf", "or open", "Five Minutes to Understand Non Dubito"),
        "zh": ("童话里的结构", "第", "上一篇", "下一篇", "这篇文章从故事而不是理论术语进入。可以继续浏览", "“故事里的结构”书架", "，或打开", "五分钟读懂 Non Dubito"),
        "zh-hant": ("童話裡的結構", "第", "上一篇", "下一篇", "這篇文章從故事而不是理論術語進入。可以繼續瀏覽", "「故事裡的結構」書架", "，或打開", "五分鐘讀懂 Non Dubito"),
    }
    series, number_word, previous, nxt, door_a, door_b, door_c, door_d = labels[lang]
    author = "Han Qin (秦漢)" if lang == "zh-hant" else "Han Qin (秦汉)"
    punctuation = "." if lang == "en" else "。"
    if lang == "en":
        number = f"Essay {index + 1:02d} of {total}"
    else:
        number = f"{number_word} {index + 1:02d} 篇，共 {total} 篇"
    body_html = "".join(paragraph(p) for p in body) + paragraph(source_note, italic=True)

    def nav(target_index: int, direction: str) -> str:
        if target_index < 0 or target_index >= total:
            return f'<a class="series-nav-btn" href="index.html"><span class="nav-arrow">←</span><span><small>{series}</small>{series}</span></a>'
        target = ITEMS[target_index]
        target_title = target["title_en"] if lang == "en" else source_copy(target)[0]
        if lang == "zh-hant":
            target_title = converter.convert(target_title)
        css = "series-nav-btn next" if direction == "next" else "series-nav-btn"
        label = nxt if direction == "next" else previous
        arrow_left = '<span class="nav-arrow">←</span>' if direction == "previous" else ""
        arrow_right = '<span class="nav-arrow">→</span>' if direction == "next" else ""
        return f'<a class="{css}" href="{target["slug"]}.html">{arrow_left}<span><small>{label}</small>{html.escape(target_title)}</span>{arrow_right}</a>'

    return f'''<div class="lang-{"hant" if lang == "zh-hant" else lang} local"><article class="article-shell"><div class="article-head"><div class="chapter-label">{series} · {html.escape(work)}</div><div class="essay-number">{number}</div><h1>{html.escape(title)}</h1><div class="article-meta">{author} · 2026</div></div><div class="article-body">{body_html}</div><div class="entry-door">{door_a} <a href="../index.html">{door_b}</a>{door_c} <a href="../../../../start.html">{door_d}</a>{punctuation}</div><nav class="series-nav">{nav(index - 1, "previous")}{nav(index + 1, "next")}</nav></article></div>'''


def article_html(item: dict[str, str], index: int, converter: TraditionalConverter) -> str:
    title_zh, body_zh, source_zh, source_url = source_copy(item)
    title_hant = converter.convert(title_zh)
    body_hant = [converter.convert(p) for p in body_zh]
    source_hant = converter.convert(source_zh)
    work_hant = converter.convert(item["work_zh"])
    source_en = f'Source note: {item["source_en"]} [Source text ↗]({source_url})'
    content_en = localized_article("en", item, index, item["title_en"], item["work_en"], ENGLISH[item["slug"]], source_en, converter)
    content_zh = localized_article("zh", item, index, title_zh, item["work_zh"], body_zh, source_zh, converter)
    content_hant = localized_article("zh-hant", item, index, title_hant, work_hant, body_hant, source_hant, converter)
    canonical = f'https://nondubito.net/essays/everyday/stories/fairy-tales/{item["slug"]}.html'
    return page_head(item["title_en"] + " · Structures in Fairy Tales", item["deck_en"], canonical) + site_header() + f'''<main class="story-wrap"><div class="story-top"><a class="back-link" href="index.html">← <span class="lang-en">Structures in Fairy Tales</span><span class="lang-zh">童话里的结构</span><span class="lang-hant">童話裡的結構</span></a>{language_toggle()}</div>{content_en}{content_zh}{content_hant}</main>''' + footer()


def chapter_cards(lang: str, converter: TraditionalConverter) -> str:
    pieces: list[str] = []
    for chapter_no, chapter_en, chapter_zh, indices in CHAPTERS:
        chapter_title = chapter_en if lang == "en" else chapter_zh
        if lang == "zh-hant":
            chapter_title = converter.convert(chapter_title)
        cards = []
        for index in indices:
            item = ITEMS[index]
            title = item["title_en"] if lang == "en" else source_copy(item)[0]
            deck = item["deck_en"] if lang == "en" else title.split("：", 1)[-1]
            work = item["work_en"] if lang == "en" else item["work_zh"]
            read = "Read" if lang == "en" else "阅读"
            if lang == "zh-hant":
                title, deck, work, read = (converter.convert(value) for value in (title, deck, work, read))
            cards.append(f'<a class="essay-card" href="{item["slug"]}.html"><span class="essay-no">{index + 1:02d}</span><h3>{html.escape(title)}</h3><p>{html.escape(work)} · {html.escape(deck)}</p><span class="read-arrow">{read} →</span></a>')
        end = list(indices)[-1] + 1
        start = list(indices)[0] + 1
        pieces.append(f'<section class="chapter"><div class="chapter-head"><span>{chapter_no}</span><h2>{html.escape(chapter_title)}</h2><em>{start:02d}—{end:02d}</em></div><div class="essay-grid">{"".join(cards)}</div></section>')
    return "".join(pieces)


def route(lang: str, converter: TraditionalConverter) -> str:
    labels = {
        "en": ("If You Don’t Want to Read All Thirty: Six Entrances", "Six scenes reveal the collection’s range. Every essay stands alone and requires no theoretical background."),
        "zh": ("如果不想一次读完：六篇入口", "从六个场景进入，就能看见这组文章怎样把童话重新打开为今天仍要回答的问题。每篇均可独立阅读，无需理论背景。"),
        "zh-hant": ("如果不想一次讀完：六篇入口", "從六個場景進入，就能看見這組文章怎樣把童話重新打開為今天仍要回答的問題。每篇均可獨立閱讀，無需理論背景。"),
    }
    title, deck = labels[lang]
    links = []
    for index in (0, 1, 4, 9, 17, 25):
        item = ITEMS[index]
        label = item["title_en"] if lang == "en" else source_copy(item)[0]
        if lang == "zh-hant":
            label = converter.convert(label)
        links.append(f'<a href="{item["slug"]}.html"><span>{index + 1:02d}</span>{html.escape(label)}</a>')
    return f'<section class="reading-route"><h2>{title}</h2><p>{deck}</p><div class="route-links">{"".join(links)}</div></section>'


def index_local(lang: str, converter: TraditionalConverter) -> str:
    copy = {
        "en": ("Stories and Structures · Collection 04", "Structures in Fairy Tales", "Fairy tales make promises visible: a locked room, a borrowed voice, a skin burned too soon, a shoe that identifies its wearer. These thirty essays do not replace wonder with a moral. They stay with the moment when rescue becomes control, gratitude becomes a debt, or a happy ending still leaves someone’s answer unfinished.", "Five chapters and three codas · Thirty essays · Chinese, English, and Traditional Chinese"),
        "zh": ("故事里的结构 · 系列 04", "童话里的结构", "童话把承诺变成一把钥匙、一副嗓音、一张被过早烧掉的皮，或一只替人证明身份的鞋。这三十篇不急着用另一条寓意替换旧寓意，而是停在救援可能变成接管、感谢可能变成债务、幸福结局仍有回答尚未完成的地方。", "五章与三篇余响 · 30 篇 · 中文、英文与繁体中文"),
        "zh-hant": ("故事裡的結構 · 系列 04", "童話裡的結構", "童話把承諾變成一把鑰匙、一副嗓音、一張被過早燒掉的皮，或一隻替人證明身分的鞋。這三十篇不急著用另一條寓意替換舊寓意，而是停在救援可能變成接管、感謝可能變成債務、幸福結局仍有回答尚未完成的地方。", "五章與三篇餘響 · 30 篇 · 中文、英文與繁體中文"),
    }
    kicker, title, deck, meta = copy[lang]
    css_lang = "hant" if lang == "zh-hant" else lang
    author = "Han Qin (秦漢)" if lang == "zh-hant" else "Han Qin (秦汉)"
    return f'''<div class="lang-{css_lang} local"><section class="story-hero"><div class="story-kicker">{kicker}</div><h1>{title}</h1><p class="story-deck">{deck}</p><div class="story-meta">{author} · 2026 · {meta}</div></section>{route(lang, converter)}{chapter_cards(lang, converter)}</div>'''


def index_html(converter: TraditionalConverter) -> str:
    canonical = "https://nondubito.net/essays/everyday/stories/fairy-tales/"
    head = page_head("Structures in Fairy Tales · 童话里的结构", "Thirty essays reopen fairy tales as questions about promises, voice, recognition, care, refusal, and unfinished endings.", canonical)
    return head + site_header() + f'''<main class="story-wrap"><div class="story-top"><a class="back-link" href="../index.html">← <span class="lang-en">Stories and Structures</span><span class="lang-zh">故事里的结构</span><span class="lang-hant">故事裡的結構</span></a>{language_toggle()}</div>{index_local("en", converter)}{index_local("zh", converter)}{index_local("zh-hant", converter)}</main>''' + footer()


def replace_required(content: str, old: str, new: str, path: Path) -> str:
    if new in content:
        return content
    if old not in content:
        raise ValueError(f"Could not update {path.relative_to(ROOT)}: expected text is missing: {old[:90]!r}")
    return content.replace(old, new)


def replace_once_required(content: str, old: str, new: str, path: Path) -> str:
    if new in content:
        return content
    if old not in content:
        raise ValueError(f"Could not update {path.relative_to(ROOT)}: expected text is missing: {old[:90]!r}")
    return content.replace(old, new, 1)


def updated_hubs() -> dict[Path, str]:
    paths = {
        "stories": ROOT / "essays" / "everyday" / "stories" / "index.html",
        "everyday": ROOT / "essays" / "everyday" / "index.html",
        "library": ROOT / "library.html",
        "explore": ROOT / "explore.html",
        "css": ROOT / "essays" / "everyday" / "stories" / "stories.css",
    }
    values = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}

    story_changes = [
        ("Sixty-two essays reopen fables, ancient stories, and epic traditions as questions about power, judgment, loss, and care.", "Ninety-two essays reopen fables, ancient stories, epic traditions, and fairy tales as questions about power, judgment, loss, and care."),
        ('</a></div><div class="future-card">Fairy tales and further oral and written traditions will be added here as their collections are completed.', '</a><a class="collection-card" href="fairy-tales/index.html"><div><span class="count">Thirty essays · Three languages</span><h2>Structures in Fairy Tales</h2><p>Thirty familiar tales reopened around promises, voice, recognition, care, refusal, and the part of a happy ending that remains unfinished.</p></div><span class="arrow">Enter collection →</span></a></div><div class="future-card">Further oral and written traditions will be added here as their collections are completed.'),
        ('</a></div><div class="future-card">童话及更多口述与书面传统，会在相应系列完成后继续加入这里。', '</a><a class="collection-card" href="fairy-tales/index.html"><div><span class="count">30 篇 · 三种语言</span><h2>童话里的结构</h2><p>三十则熟悉的童话，重新打开承诺、声音、辨认、照顾与拒绝，也停在幸福结局仍未说完的地方。</p></div><span class="arrow">进入系列 →</span></a></div><div class="future-card">更多口述与书面传统，会在相应系列完成后继续加入这里。'),
        ('</a></div><div class="future-card">童話及更多口述與書面傳統，會在相應系列完成後繼續加入這裡。', '</a><a class="collection-card" href="fairy-tales/index.html"><div><span class="count">30 篇 · 三種語言</span><h2>童話裡的結構</h2><p>三十則熟悉的童話，重新打開承諾、聲音、辨認、照顧與拒絕，也停在幸福結局仍未說完的地方。</p></div><span class="arrow">進入系列 →</span></a></div><div class="future-card">更多口述與書面傳統，會在相應系列完成後繼續加入這裡。'),
    ]
    for old, new in story_changes:
        values["stories"] = replace_required(values["stories"], old, new, paths["stories"])
    shared_story_meta = '<div class="story-meta">Han Qin (秦汉) · 2026 · 3 collections · 62 essays · 8 languages</div>'
    for localized_meta in (
        '<div class="story-meta">Han Qin (秦汉) · 2026 · 4 collections · 92 essays · 3–8 languages</div>',
        '<div class="story-meta">Han Qin (秦汉) · 2026 · 4 个系列 · 92 篇 · 3–8 种语言</div>',
        '<div class="story-meta">Han Qin (秦漢) · 2026 · 4 個系列 · 92 篇 · 3–8 種語言</div>',
    ):
        values["stories"] = replace_once_required(values["stories"], shared_story_meta, localized_meta, paths["stories"])

    everyday_changes = [
        ("Story shelf · Three collections · Sixty-two essays", "Story shelf · Four collections · Ninety-two essays"),
        ("Fables, ancient stories, and epic traditions reopen familiar scenes as questions about power, judgment, loss, responsibility, and care.", "Fables, ancient stories, epic traditions, and fairy tales reopen familiar scenes as questions about power, judgment, loss, responsibility, and care."),
        ("Three collections · Sixty-two essays · Three languages", "Four collections · Ninety-two essays · Three to eight languages"),
        ("故事书架 · 三个系列 · 六十二篇", "故事书架 · 四个系列 · 九十二篇"),
        ("从寓言、古老故事与史诗传统进入，重新打开力量、判断、失去、责任与照顾的问题。", "从寓言、古老故事、史诗传统与童话进入，重新打开力量、判断、失去、责任与照顾的问题。"),
        ("三个系列 · 六十二篇 · 三种语言", "四个系列 · 九十二篇 · 三至八种语言"),
        ("故事書架 · 三個系列 · 六十二篇", "故事書架 · 四個系列 · 九十二篇"),
        ("從寓言、古老故事與史詩傳統進入，重新打開力量、判斷、失去、責任與照顧的問題。", "從寓言、古老故事、史詩傳統與童話進入，重新打開力量、判斷、失去、責任與照顧的問題。"),
        ("三個系列 · 六十二篇 · 三種語言", "四個系列 · 九十二篇 · 三至八種語言"),
        ("Further everyday series on failure, loneliness, aging, and care—and further story collections beginning with fairy tales—will be gathered here.", "Further everyday series on failure, loneliness, aging, and care—and further story collections—will be gathered here."),
        ("以后关于失败、孤独、衰老与照护的日常文章，以及从童话开始的更多故事系列，也会继续收在这里。", "以后关于失败、孤独、衰老与照护的日常文章，以及更多故事系列，也会继续收在这里。"),
        ("以後關於失敗、孤獨、衰老與照護的日常文章，以及從童話開始的更多故事系列，也會繼續收在這裡。", "以後關於失敗、孤獨、衰老與照護的日常文章，以及更多故事系列，也會繼續收在這裡。"),
    ]
    for old, new in everyday_changes:
        values["everyday"] = replace_required(values["everyday"], old, new, paths["everyday"])

    library_changes = [
        ("3 collections · 62 essays · 8 languages", "4 collections · 92 essays · 3–8 languages"),
        ("3 个系列 · 62 篇 · 8 种语言", "4 个系列 · 92 篇 · 3–8 种语言"),
        ("3 個系列 · 62 篇 · 8 種語言", "4 個系列 · 92 篇 · 3–8 種語言"),
        ("A separate shelf for fables, ancient stories, and epic traditions—old scenes reopened as present questions rather than reduced to morals.", "A separate shelf for fables, ancient stories, epic traditions, and fairy tales—old scenes reopened as present questions rather than reduced to morals."),
        ("寓言、古老故事与史诗传统单独组成一个书架：不急着提炼寓意，而是让旧场景重新成为今天的问题。", "寓言、古老故事、史诗传统与童话单独组成一个书架：不急着提炼寓意，而是让旧场景重新成为今天的问题。"),
        ("寓言、古老故事與史詩傳統單獨組成一個書架：不急著提煉寓意，而是讓舊場景重新成為今天的問題。", "寓言、古老故事、史詩傳統與童話單獨組成一個書架：不急著提煉寓意，而是讓舊場景重新成為今天的問題。"),
    ]
    for old, new in library_changes:
        values["library"] = replace_required(values["library"], old, new, paths["library"])

    explore_changes = [
        ("Fables, ancient stories, and epic traditions reopened as questions.", "Fables, ancient stories, epic traditions, and fairy tales reopened as questions."),
        ("让寓言、古老故事与史诗传统重新成为问题。", "让寓言、古老故事、史诗传统与童话重新成为问题。"),
        ("讓寓言、古老故事與史詩傳統重新成為問題。", "讓寓言、古老故事、史詩傳統與童話重新成為問題。"),
    ]
    for old, new in explore_changes:
        values["explore"] = replace_required(values["explore"], old, new, paths["explore"])

    values["css"] = replace_required(values["css"], ".collection-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));", ".collection-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));", paths["css"])
    values["css"] = replace_required(values["css"], ".collection-card:nth-child(3){background:#30281f}", ".collection-card:nth-child(3){background:#30281f}.collection-card:nth-child(4){background:#49323a}", paths["css"])
    return {paths[name]: content for name, content in values.items()}


def render() -> dict[Path, str]:
    if len(ENGLISH) != len(ITEMS):
        missing = [item["slug"] for item in ITEMS if item["slug"] not in ENGLISH]
        raise ValueError("Missing English rewrites: " + ", ".join(missing))
    converter = TraditionalConverter()
    try:
        outputs = updated_hubs()
        outputs[TARGET / "index.html"] = index_html(converter)
        outputs.update({TARGET / f'{item["slug"]}.html': article_html(item, index, converter) for index, item in enumerate(ITEMS)})
        return outputs
    finally:
        converter.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    stale = [path for path, text in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != text]
    if args.check:
        if stale:
            raise SystemExit("Stale fairy-tale pages:\n" + "\n".join(str(path.relative_to(ROOT)) for path in stale))
        print(f"OK: {len(outputs)} fairy-tale pages")
        return
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"Wrote: {len(outputs)} fairy-tale pages")


if __name__ == "__main__":
    main()
