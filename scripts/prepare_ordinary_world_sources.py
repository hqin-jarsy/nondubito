#!/usr/bin/env python3
"""Apply the authorized, documented source corrections, keeping block alignment."""
from pathlib import Path
import json,re,hashlib,sys,html
sys.path.insert(0,str(Path(__file__).resolve().parent))
from prepare_action_sources import Document,Node
R=Path(__file__).resolve().parents[1];D=R/'data/ordinary-world/multilingual'
s=json.loads((D/'source.json').read_text()); original=D/'source-original.json'
if not original.exists():original.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
base=json.loads(original.read_text());base_now=json.loads((D/'source.json').read_text())
# article / one-based block / simplified / traditional / reason
changes=[
(2,77,'她这些年干着最重的活，后来又在砖窑边劳作，烟熏火燎，粉尘满天。','她這些年幹著最重的活，後來又在磚窯邊勞作，煙熏火燎，粉塵滿天。','Brickworks begins spring 1980; diagnosis is 1985, not over ten kiln-working years.'),
(2,86,'秀莲得的是肺癌。而书里此前反复写过她在砖窑边的劳作。','秀蓮得的是肺癌。而書裡此前反覆寫過她在磚窯邊的勞作。','Remove unsupported ten-plus-year kiln chronology.'),
(2,88,'把她的病和那些劳动场面放在一起读，身体付出的代价就显出来了；这不等于小说已经给出了确定的医学病因。','把她的病和那些勞動場面放在一起讀，身體付出的代價就顯出來了；這不等於小說已經給出了確定的醫學病因。','Separate literary juxtaposition from unestablished medical causation.'),
(3,23,'他求他妈，亲事在两家大人之间推动，后来压到了润叶头上。二妈徐爱云及其父亲徐国强参与劝说；田福军起初并不知道其中的内情。','他求他媽，親事在兩家大人之間推動，後來壓到了潤葉頭上。二媽徐愛雲及其父親徐國強參與勸說；田福軍起初並不知道其中的內情。','Tian Fujun was not party to the political coercion; book I chapter 46.'),
(3,26,'而润叶那边，有二妈的劝说，也有徐国强把二爸的前途摆出来施压，是“这门亲事很好”，是“你这个年纪了”，是“人家条件那么好”。','而潤葉那邊，有二媽的勸說，也有徐國強把二爸的前途擺出來施壓，是「這門親事很好」，是「你這個年紀了」，是「人家條件那麼好」。','Distinguish pressure invoking uncle’s career from pressure by uncle.'),
(4,107,'她对他说了她的心意。她在信里说，大学毕业后愿意到他的矿医院来当医生。她愿意走近他的生活，而不是要求他离开矿井。','她對他說了她的心意。她在信裡說，大學畢業後願意到他的礦醫院來當醫生。她願意走近他的生活，而不是要求他離開礦井。','Jin Xiu offers to work at the mine hospital; book III chapter 54.'),
(4,108,'另有一条去省城工作的路，是兰香和吴仲平提出的。这是两个不同的提议：一个人愿意走到他的生活里，另一些人替他找了离开的路。','另有一條去省城工作的路，是蘭香和吳仲平提出的。這是兩個不同的提議：一個人願意走到他的生活裡，另一些人替他找了離開的路。','Separate urban transfer from love proposal.'),
(5,9,'她说她一直喜欢他。她不把那道疤当作障碍；她在信里说，大学毕业后准备到他的矿医院来当医生。','她說她一直喜歡他。她不把那道疤當作障礙；她在信裡說，大學畢業後準備到他的礦醫院來當醫生。','Correct Jin Xiu proposal.'),
(5,11,'她愿意到矿区来。另一个调到省城工作的提议，来自兰香和吴仲平。对孙少平来说，这两件事都需要回答，但它们不是同一条“上去”的路。','她願意到礦區來。另一個調到省城工作的提議，來自蘭香和吳仲平。對孫少平來說，這兩件事都需要回答，但它們不是同一條「上去」的路。','Correct premise underlying class-ascent interpretation.'),
(5,20,'王世才是他刚到矿上时的师傅，教了他许多东西。后来在一次事故里，钢梁朝安锁子袭来，王世才把钢梁扳向自己，救下安锁子，自己牺牲了。孙少平亲眼见到了这一幕。','王世才是他剛到礦上時的師傅，教了他許多東西。後來在一次事故裡，鋼梁朝安鎖子襲來，王世才把鋼梁扳向自己，救下安鎖子，自己犧牲了。孫少平親眼見到了這一幕。','Rescued worker is An Suozi, not Shaoping; book III chapter 17.'),
(5,23,'惠英、明明和小狗向他迎来。','惠英、明明和小狗向他迎來。','Remove invented closing dialogue; book III chapter 54.'),
(5,58,'而王世才为救工友而死，是孙少平亲眼见到的一次最重的承认。','而王世才為救工友而死，是孫少平親眼見到的一次最重的承認。','Witnessed recognition, not rescue personally received.'),
(5,59,'一个人把朝着另一个人的钢梁扳向自己——在那一秒钟里，没有任何一份档案在起作用。没有户口，没有工种，没有出身，没有前途。','一個人把朝著另一個人的鋼梁扳向自己——在那一秒鐘裡，沒有任何一份檔案在起作用。沒有戶口，沒有工種，沒有出身，沒有前途。','Correct rescue action while preserving interpretation.'),
(5,60,'只有一个人，挡在另一个人的危险前面。','只有一個人，擋在另一個人的危險前面。','Correct physical action.'),
(5,64,'这两种解释未必穷尽了他的选择，但也不能只凭“拒绝上升”就把它们全部排除。','這兩種解釋未必窮盡了他的選擇，但也不能只憑「拒絕上升」就把它們全部排除。','Remove unsupported exclusive explanation after correcting offer.'),
(5,66,'她提出的是爱情，以及毕业后到矿医院工作的打算。去省城的机会，则是兰香和吴仲平另行提出的。','她提出的是愛情，以及畢業後到礦醫院工作的打算。去省城的機會，則是蘭香和吳仲平另行提出的。','Separate two proposals.'),
(5,67,'后一条路可以叫“上去”。前一件事，不能只用这个名字来概括。','後一條路可以叫「上去」。前一件事，不能只用這個名字來概括。','Retain supported ascent reading only.'),
(5,70,'金秀这一次却不完全是同样的东西。她愿意走到矿区来；把她的感情只当成晋升的包装，也会把她本人抹掉。','金秀這一次卻不完全是同樣的東西。她願意走到礦區來；把她的感情只當成晉升的包裝，也會把她本人抹掉。','Withdraw false equivalence of affection and promotion.'),
(5,71,'他没有接受这段感情，也没有接受调到省城的提议。但两次拒绝，不必被说成只有同一个理由。','他沒有接受這段感情，也沒有接受調到省城的提議。但兩次拒絕，不必被說成只有同一個理由。','Avoid unsupported motive identity.'),
(5,72,'所以，说他在拒绝那把尺子，应当落在他选择回到矿区的方向上，而不能以此替金秀的感情定性。','所以，說他在拒絕那把尺子，應當落在他選擇回到礦區的方向上，而不能以此替金秀的感情定性。','Constrain interpretation to supported destination choice.'),
(5,73,'如果把他从双水村出来、在黄原背石头、下到矿井的经历，都只讲成换一个更好位置的准备，这一路就只剩下了一段爬升的过程。','如果把他從雙水村出來、在黃原背石頭、下到礦井的經歷，都只講成換一個更好位置的準備，這一路就只剩下了一段爬升的過程。','Preserve ranking critique without saying accepting love invalidates life.'),
(5,74,'而他的返回，拒绝了对这段人生只有这一种解释。','而他的返回，拒絕了對這段人生只有這一種解釋。','Maintain author’s supported point.'),
(5,99,'孙少平出走。孙少安留下。贺秀莲要一间自己的窑洞。田润叶走进那间病房。田晓霞跳进洪水。王世才救下工友。','孫少平出走。孫少安留下。賀秀蓮要一間自己的窯洞。田潤葉走進那間病房。田曉霞跳進洪水。王世才救下工友。','Correct recap rescue.'),
(5,104,'路遥一九八八年完成这本书，一九九二年去世，相隔四年，四十二岁。','路遙一九八八年完成這本書，一九九二年去世，相隔四年，四十二歲。','1988 completion and 1992 death.'),
(5,111,'我想说的是：一个人写一本一百万字的书，长年耗尽心力，在病痛中坚持，这件事在任何一份实用的账上都是不划算的。把这些经历并置，不等于能够断言写作就是他的医学死因。','我想說的是：一個人寫一本一百萬字的書，長年耗盡心力，在病痛中堅持，這件事在任何一份實用的帳上都是不划算的。把這些經歷並置，不等於能夠斷言寫作就是他的醫學死因。','Do not state writing as medically established cause of death.'),
(5,113,'而他把多年时间交给了这本书。写完四年后，他去世了。','而他把多年時間交給了這本書。寫完四年後，他去世了。','Correct interval, avoid immediate-death implication.'),
]
changes += [
(4,29,'## 她给过帮助，但不止于安排','## 她給過幫助，但不止於安排','Correct the no-help premise while preserving distinction between practical help and recognition.'),
(4,32,'她确实借助父亲的名头，替孙少平疏通了煤矿招工的关系。这件事是她背着父亲做的，出面的是她，不是田福军本人。','她確實借助父親的名頭，替孫少平疏通了煤礦招工的關係。這件事是她背著父親做的，出面的是她，不是田福軍本人。','Book II chapter 53: Xiaoxia uses father’s name without his knowledge.'),
(4,33,'她确实给过他一个现实的机会。','她確實給過他一個現實的機會。','Withdraw contradicted absolute.'),
(4,34,'她还提过，过一两年再央求父亲把他调出来。','她還提過，過一兩年再央求父親把他調出來。','She explicitly proposes later transfer out of mine.'),
(4,35,'她并不是一个从不介入他生活的人；她也担心他的处境，也想替他找一条容易些的路。','她並不是一個從不介入他生活的人；她也擔心他的處境，也想替他找一條容易些的路。','Keep practical intervention visible.'),
(4,36,'那么，她跟别人究竟不同在哪里？','那麼，她跟別人究竟不同在哪裡？','Reframe question after factual correction.'),
(4,37,'不在于她从没有给过现实帮助。','不在於她從沒有給過現實幫助。','Remove contradicted nonhelp explanation.'),
(4,38,'更要紧的是：她看见的并不只有一个需要换位置的人。','更要緊的是：她看見的並不只有一個需要換位置的人。','Retain supported noninstrumental regard.'),
(4,39,'孙少平有自己的坚持，也实际受过她的帮助。接受一次帮助，并没有让他把今后的每一步都交出去。','孫少平有自己的堅持，也實際受過她的幫助。接受一次幫助，並沒有讓他把今後的每一步都交出去。','Her intervention undermines absolute refusal-of-connections claim.'),
(4,40,'她借书给他，跟他讨论那些不直接改变职位的事。这些交往，没有被安排工作的那一面耗尽。','她借書給他，跟他討論那些不直接改變職位的事。這些交往，沒有被安排工作的那一面耗盡。','Preserve original books-and-conversation argument.'),
(4,42,'田晓霞面对孙少平，也有资源不对等的一面。她确实动用了资源。两段关系的区别，并不在于有没有给过现实的帮助。','田曉霞面對孫少平，也有資源不對等的一面。她確實動用了資源。兩段關係的區別，並不在於有沒有給過現實的幫助。','Remove unsupported symmetry based on nonexistent restraint.'),
(4,43,'真正需要看的，是一次帮助是否把对方整个未来都收归自己判断；而送书、对话和那个约定，还让我们看见了职位以外的孙少平。','真正需要看的，是一次幫助是否把對方整個未來都收歸自己判斷；而送書、對話和那個約定，還讓我們看見了職位以外的孫少平。','Keep decision-ownership question without inventing no practical help.'),
(4,70,'一个地委书记的女儿，省报的记者。一个煤矿工人，农民出身。两个人要在一起，这一篇先考察几条可以想见的路：','一個地委書記的女兒，省報的記者。一個煤礦工人，農民出身。兩個人要在一起，這一篇先考察幾條可以想見的路：','His registration is no longer Shuangshui; routes are essay hypotheses.'),
(4,71,'一，孙少平通过田家的关系调到更体面的职位。他曾受过晓霞的帮助，不能因此就说他失去自我；但如果把他所有坚持都理解成通往好位置的手段，这一路的意义就被缩窄了。','一，孫少平通過田家的關係調到更體面的職位。他曾受過曉霞的幫助，不能因此就說他失去自我；但如果把他所有堅持都理解成通往好位置的手段，這一路的意義就被縮窄了。','Remove false all-connections-refusal premise while retaining rank critique.'),
(5,69,'田晓霞在的时候，他受过她疏通招工关系的帮助。后来，他并没有把这份帮助延伸成由别人替他决定今后一定要去哪里。','田曉霞在的時候，他受過她疏通招工關係的幫助。後來，他並沒有把這份幫助延伸成由別人替他決定今後一定要去哪裡。','Acknowledge help actually received; do not equate any help with lost agency.')
]
changes.append((5,22,'孙少平从那以后就照顾这一家。而这本书的最后一页，是他回到矿区，再走向那个熟悉的地方。','孫少平從那以後就照顧這一家。而這本書的最後一頁，是他回到礦區，再走向那個熟悉的地方。','Remove unsupported train-station departure; finale places his arrival at mining administration before walking along railway.'))
records=[]
for ep,no,zh,hant,reason in changes:
 a=s['articles'][ep-1];old=base['articles'][ep-1]['body_zh'][no-1];a['body_zh'][no-1]=zh
 p=R/a['source_html'];txt=p.read_text();doc=Document(txt);body=next(n for n in doc.root.walk() if n.has('essay-body','lang-zh'));node=next((n for n in body.children if isinstance(n,Node) and n.text().strip() in (old.removeprefix('## '),zh.removeprefix('## '),base_now['articles'][ep-1]['body_zh'][no-1].removeprefix('## '))),None);assert node is not None,(ep,no);p.write_text(txt[:node.open_end]+html.escape(zh.removeprefix('## '))+txt[node.close_start:])
 hp=p.parent/'zh-hant-data'/(p.stem+'.js');ht=hp.read_text();m=re.search(r'var variants = (\{.*?\});',ht,re.S);v=json.loads(m.group(1));v.pop(old.removeprefix('## '),None);v[zh.removeprefix('## ')]=hant.removeprefix('## ');hp.write_text(ht[:m.start(1)]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+ht[m.end(1):])
 records.append({'article':ep,'source_block':no,'before':old,'after':zh,'reason':reason,'applied_to':['zh','zh-hant','source.json']})
# Last recap contains the same rescued-pupil error within a long paragraph.
a=s['articles'][4];old=base['articles'][4]['body_zh'][119];new=old.replace('王世才用命把徒弟推开了。','王世才为救工友牺牲，孙少平亲眼见到了这一幕。');a['body_zh'][119]=new
p=R/a['source_html'];txt=p.read_text();doc=Document(txt);body=next(n for n in doc.root.walk() if n.has('essay-body','lang-zh'));node=next(n for n in body.children if isinstance(n,Node) and n.text().strip() in (old,new));p.write_text(txt[:node.open_end]+html.escape(new)+txt[node.close_start:]);hp=p.parent/'zh-hant-data'/(p.stem+'.js');ht=hp.read_text();m=re.search(r'var variants = (\{.*?\});',ht,re.S);v=json.loads(m.group(1));v.pop(old,None);v[new]='孫少安替田潤葉算了一遍她的將來，用的理由是「你會後悔」——而那筆帳不是他的。賀秀蓮把自己全部的力氣投進那個家，因為那是她唯一擁有的東西——她換到了，然後用不上了。田潤葉在別人擺好的牌裡選了很多年，直到有一天走進一間病房，面對一個不能再向她要任何東西的人。田曉霞是唯一一個不給孫少平分類的人，而她跳進那場洪水，跟他一點關係也沒有。王世才為救工友犧牲，孫少平親眼見到了這一幕。';hp.write_text(ht[:m.start(1)]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+ht[m.end(1):]);records.append({'article':5,'source_block':120,'before':old,'after':new,'reason':'Recap rescues fellow worker, not pupil.','applied_to':['zh','zh-hant','source.json']})
for a in s['articles']:a['source_sha256']=hashlib.sha256((R/a['source_html']).read_bytes()).hexdigest()
s['note']='Complete Chinese source with authorized documented corrections. Original snapshot retained in source-original.json; alignment unchanged.'
(D/'source.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
(D.parent/'source-corrections.json').write_text(json.dumps({'date':'2026-11-18','corrections':records,'evidence':{'kiln_start':'https://99csw.com/book/2002/56678.htm','diagnosis':'https://99csw.com/book/2002/56775.htm','rescue':'https://99csw.com/book/2002/56739.htm','finale':'https://99csw.com/book/2002/56776.htm','xiaoxia_help':'https://www.chinesepen.org/blog/archives/172374','marriage_pressure':'https://www.chinesepen.org/blog/archives/172187'},'verification':'Novel passages independently checked by the coordinating factual reviewer; chronology of author completion/death likewise reported to coordinator. Literary interpretations retained except conclusions dependent on corrected false premises. Other rhetorical absolutes are not certified as historical facts.'},ensure_ascii=False,indent=2)+'\n')
print('Updated',len(records),'Chinese/Hant blocks; alignment preserved.')
