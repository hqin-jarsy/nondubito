"""One-time, explicit publication preparation; never rewrites received manuscripts.

Prints an apply_patch payload. Kept as a receipt of the editorial substitutions.
Run from a clean pre-chapter-83 checkout after importing the author ZIP's text files.
"""
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data/originals/hongloumeng'
RECEIVED = DATA/'translations/received/ch083'
DATE = '2026-10-24'
patch = ['*** Begin Patch']


def update(path, content):
    if path.exists():
        patch.append('*** Update File: '+str(path))
        patch.extend('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(path.read_text().splitlines(),content.splitlines(),n=2,lineterm=''))[2:])
    else:
        patch.append('*** Add File: '+str(path))
        patch.extend('+'+line for line in content.splitlines())


NAMES = {
 'en': [('贾母','Lady Jia','Grandmother Jia'),('彩明','Cai-ming','Sunshine'),('藕香榭','Lotus-scented Pavilion','Lotus Pavilion')],
 'de': [('贾母','Dame Chia','Dame'),('贾母','alte Dame','Alte Fürstin'),('贾母','alten Dame','Alten Fürstin'),
        ('史太君','Frau Shih','Frau Shi'),('黛玉','Tai Yü','Blaujuwel'),('凤姐','Feng Chieh','Phönix'),
        ('王夫人','Frau Wang','Frau Tschong'),('贾政','Chia Cheng','Herr Tschong'),('贾琏','Chia Lien','Jia Lian'),
        ('贾赦','Chia She','Jia She'),('邢夫人','Frau Hsing','Frau Xing'),('李贵','Li Kuei','Li Gui'),
        ('鸳鸯','Yüan Yang','Yuanyang'),('琥珀','Hu P’o','Hupo'),('平儿','P’ing Erh',"Ping'er"),('鹦鹉','Ying Wu','Yingwu'),
        ('宝钗','Pao Ch’ai','Pao Tschai'),('探春','T’an Ch’un','Tanchun'),('湘云','Hsiang Yün','Xiangyun'),
        ('宝琴','Pao Ch’in','Baoqin'),('琴儿','Ch’in Erh','Qin'),('敏儿','Min Erh','Min'),('贾兰','Chia Lan','Jia Lan'),
        ('琏儿','Lien Erh','Lian'),('文官','Wen Kuan','Wenguan'),('翡翠','Fei Ts’ui','Feicui'),('翠缕','Ts’ui Lü','Cuilü'),
        ('珍珠','Chen Chu','Zhenzhu'),('玻璃','Po Li','Boli'),('紫鹃','Tzu Chüan','Kuckuck'),
        ('林之孝','Lin Chih Hsiao','Lin Zhixiao'),('彩明','Ts’ai Ming','Caiming'),('锄药','Ch’u Yao','Chuyao'),
        ('扫红','Sao Hung','Saohong'),('茗烟','Ming Yen','Mingyan'),('善姐','Shan Chieh','Shanjie'),
        ('夏老爷','Herr Hsia','Herr Xia'),('蓉大奶奶','Herrn Jung','Herrn Rong'),('甄家','Familie Chen','Familie Zhen'),
        ('荣府','Hauses Jung','Rong-Hauses'),('荣府','Haus Jung','Rong-Haus'),
        ('沁芳亭','Pavillon der Durchdringenden Düfte','Qinfang-Pavillon'),('稻香村','Dorf des Reisduftes','Dorf im Reisduft'),
        ('藕香榭','Wasserpavillon des Lotusduftes','Pavillon des Lotosduftes'),('恒舒典','Heng Shu','Hengshu'),
        ('唐寅','T’ang Yin','Tang Yin'),('董其昌','Tung Ch’i Ch’ang','Dong Qichang')],
 'fr': [('平儿','Ping’er','Petite Quiète'),('凤姐','Sœur Phénix','Grande Sœur Phénix'),
        ('王夫人','Madame Wang','la Seconde Dame Wang'),('探春','Tanchun','la Demoiselle Printemps Tierce-née'),
        ('鹦鹉','Yingwu','Perroquet'),('紫鹃','Zijuan','Cri de Coucou'),('茗烟','Mingyan','Brume de Thé'),
        ('荣府','palais Rong','palais de la Gloire'),('沁芳亭','pavillon Qin-fang','kiosque Qin-Fang'),
        ('稻香村','Village au Parfum de Riz','Village du Parfum de Riz'),('藕香榭','Pavillon au Parfum de Lotus','Pavillon des Senteurs de Lotus')],
 'es': [('平儿',"Ping'er",'Pinger'),('贾母','abuela Jia','Anciana Dama'),('王夫人','señora Wang','dama Wang'),
        ('藕香榭','pabellón Ouxiang','pabellón del Aroma de Loto'),('稻香村','Daoxiang Cun','la aldea Daoxiang')],
 'ja': [],
 'ko': [('凤姐','봉저','희봉'),('老太太','대부인','노마님'),('王夫人','왕 부인','왕부인'),('邢夫人','형 부인','형부인'),('恒舒典','항서 전당포','항서전')],
}
LOCAL = {
 'en': [("My very life must always be with my heart's own flesh.","The one who is my very life must always be with my heart's own flesh.",'Preserve an affectionate reference to a person, without naming Baoyu.')],
 'fr': [('Ce qui me tient à la vie doit toujours demeurer avec la chair de mon cœur.','L’être qui est toute ma vie doit toujours demeurer auprès de la chair de mon cœur.','Preserve the human referent, not an abstract attachment to life.')],
 'es': [('Lo que me da la vida ha de estar siempre junto a la carne de mi corazón','Quien es mi vida ha de estar siempre junto a la carne de mi corazón','Preserve the human referent without spelling out the marriage.')],
 'de': [('Pass lieber auf, dass du nicht selbst stolperst und mir noch um dich weh wird.','Pass lieber auf, dass du nicht selbst stolperst und ich mir dann um dich Sorgen machen muss.','Natural German for the grandmother’s concern, without added action.'),
        ('Phönixs','Phönix’','German genitive after restoring the established name ending in x.'),
        ('ließ Herr Tschong','ließ Herrn Tschong','Accusative inflection after name restoration.'),
        ('an Herr Tschong','an Herrn Tschong','Accusative inflection with sich wenden an.'),
        ('zu Herr Tschong','zu Herrn Tschong','Dative after zu.'),
        ('sah Herr Tschong an','sah Herrn Tschong an','Accusative with ansehen.'),
        ('Herr Tschong entglitt','Herrn Tschong entglitt','Dative with entgleiten.'),
        ('Herr Tschong blieb nichts anderes übrig','Herrn Tschong blieb nichts anderes übrig','Dative with übrigbleiben.')],
 'ja': [('蒲団','蒲草の円座','蒲团 is a sitting cushion, not bedding.')],
 'ko': [],
}


def main():
    corrections=json.loads((DATA/'translations/corrections.json').read_text())
    assert not any(x['chapter']=='ch083' for x in corrections), 'Already prepared'
    registry={'baseline':'Published chapters 81–82 plus explicit chapter-83 choices; aliases may be contextual, not new identities.',
              'policy':'Preserve existing published forms. New chapters require an explicit terminology comparison, not a fresh naming system.',
              'languages':{}}
    for lang, rules in NAMES.items():
        text=(RECEIVED/f'ch083_{lang}.md').read_text()
        for identity,before,after in rules:
            count=text.count(before)
            assert count,(lang,before)
            corrections.append({'chapter':'ch083','language':lang,'before':before,'after':after,'count':count,'reason':'Cross-chapter name continuity: '+identity})
            registry['languages'].setdefault(lang,[]).append({'identity':identity,'preferred':after,'retired':before})
            text=text.replace(before,after)
        for before,after,reason in LOCAL[lang]:
            count=text.count(before);assert count,(lang,before)
            corrections.append({'chapter':'ch083','language':lang,'before':before,'after':after,'count':count,'reason':reason})
            text=text.replace(before,after)
        # Restore French sentence-initial capitals after adding named titles.
        if lang=='fr':
            for prefix in ('\n\n','. ','» '):
                for title in ('la Seconde Dame Wang','la Demoiselle Printemps Tierce-née'):
                    before=prefix+title;count=text.count(before)
                    if count:
                        after=prefix+title[0].upper()+title[1:]
                        corrections.append({'chapter':'ch083','language':lang,'before':before,'after':after,'count':count,'reason':'Sentence-initial capitalization after title normalization.'})
                        text=text.replace(before,after)
    update(DATA/'translations/corrections.json',json.dumps(corrections,ensure_ascii=False,indent=2)+'\n')
    update(DATA/'translations/continuity.json',json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    raw=(RECEIVED/'ch083_zh-Hans.md').read_bytes()
    assert raw.startswith(b'# ')
    original=raw[2:]
    update(DATA/'ch083.zh.txt',original.decode())
    record=json.loads((DATA/'publication.json').read_text())
    record['published_chapters'].append(83)
    record['chapter_sources']['ch083']={'source':'ch083.zh.txt','source_sha256':hashlib.sha256(original).hexdigest(),'source_bytes':len(original),'received_sha256':hashlib.sha256(raw).hexdigest(),'modified':DATE,'paragraphs':32,'source_filename':'83回_r55_定稿.md','note':'Author-supplied Simplified manuscript unchanged except the Markdown title marker removed. Terminal whitespace is preserved.'}
    receipt=record['multilingual_publication']
    for f in sorted(RECEIVED.iterdir()):receipt['received_files'][str(f.relative_to(DATA))]=hashlib.sha256(f.read_bytes()).hexdigest()
    package=Path('/Users/hanqin/Documents/SAE旗舰系列多语言/大知续红楼梦/Hongloumeng_Ch083_8Languages_Full_Review_v0.1_20261025.zip')
    receipt['source_packages']['ch083']={'filename':package.name,'sha256':hashlib.sha256(package.read_bytes()).hexdigest()}
    record['chapter_publications']={'ch083':{'published':DATE,'languages':record['editions'],'source':'translations/received/ch083','continuity':'translations/continuity.json','note':'Chapter 83 added; chapter 81–82 author revisions and foreign reading text unchanged.'}}
    record['checks'] += ['Chapter 83: 32 body units in eight editions; closing couplet separated for reading', 'Chapter 83: repeated private message identical after local edits; names checked against published chapters 81–82']
    update(DATA/'publication.json',json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print('\n'.join(patch+['*** End Patch']))


if __name__=='__main__':main()
