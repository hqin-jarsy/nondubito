#!/usr/bin/env python3
"""Apply narrowly sourced factual errata to Moon Chinese pages; preserve the argument.
One-time idempotent correction. See the series editorial-review.md for evidence.
"""
from pathlib import Path
import json,re
from build_emperor_traditional import TraditionalConverter,TextCollector
R=Path(__file__).resolve().parents[1]
S=R/'essays/literature/the-moon-and-sixpence'
corrections={
'晚饭已经准备好了':'晚饭会在她和孩子们到家时准备好',
'他四十岁，做了十七年证券经纪人':'他四十岁，做证券经纪人，结婚十七年',
'这些理由思特里克兰德一条也没有。':'这些经历并非全然没有，但思特里克兰德并没有拿它们作成功的保证。',
'他没有受过训练，没有画过几张，没有任何人说过他有才能。他自己也不知道行不行。他不是从小热爱——他从来没有表现出对艺术有一点兴趣，他妻子的文学沙龙他去了都是坐在角落里不说话。':'他小时候想当画家，被父亲安排去经商；离家前的一年，他还上过夜间绘画课，妻子以为他是在俱乐部打牌。但这些经历并不能保证他会成功。他妻子的文学沙龙他去了都是坐在角落里不说话。',
'这个结构里的每一格，思特里克兰德都不占。':'思特里克兰德的经历有这个结构的一些材料，却没有按它走到最后。',
'他没有热爱。他没有被压着——没人拦他，他自己也没憋着。':'他并非从未想过画画，也曾被父亲拦阻。但他没有把这些经历讲成一套要求别人认可的理由。',
'他在塔希提画完最后那面墙，眼睛已经瞎了，然后吩咐把房子烧掉。':'他在塔希提画完最后那些墙，后来失明，临终前吩咐在自己下葬后把房子烧掉。',
'斧子':'刮刀',
'不但没有劈，他后来还做了一件更难理解的事：他把那些画收起来，托运回荷兰，带回了母亲家里——他要保存它们。':'他没有毁画。后来思特里克兰德把这幅勃朗什的画给了他；他卖掉家什，带着自己的画回荷兰。',
'而且把那批画保存了下来':'而且接受了思特里克兰德送给他的那幅画',
'在瞎了之后的那段时间里，他在那间小屋的四面墙上画了一幅巨大的画。他看不见自己画的东西，靠记忆，靠手，一点一点画完。':'失明之前，他已在小屋的墙上画下巨幅壁画。失明以后，他常在已经画好的房间里坐上很久，用看不见的眼睛朝着那些画。',
'儿子在军队里，模样端正，说话得体。':'儿子是随军牧师，穿军装、戴牧师领，模样端正，说话得体。',
'儿子引了一句《圣经》，大意是磨坊的磨盘转得很慢，但磨得很细。':'儿子引了一句格言，大意是上帝的磨坊转得很慢，但磨得很细。“我”怀疑他们把它误认成了《圣经》的话。',
'他儿子用《圣经》量他':'他儿子用被误认作《圣经》的格言量他',
'而那面墙已经烧成了灰，没有人看见过。':'而那些墙已经烧成了灰。阿塔和医生看见过，后来的公众再也无法看见。'
}
c=TraditionalConverter()
for p in S.glob('*.html'):
 t=p.read_text()
 for old,new in corrections.items():t=t.replace(old,new)
 p.write_text(t)
 # Preserve existing curated variants; add only changed/new text nodes.
 jp=S/'zh-hant-data'/(p.stem+'.js')
 if not jp.exists():continue
 js=jp.read_text();m=re.search(r'var variants = (\{.*?\});',js,re.S);v=json.loads(m.group(1))
 collector=TextCollector();collector.feed(t)
 for node in collector.text:
  if node not in v:v[node]=c.convert(node)
 jp.write_text(js[:m.start(1)]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+js[m.end(1):])
c.close()
print('Moon: factual Chinese errata applied; new Traditional text nodes added.')
