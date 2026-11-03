"""Print the publication receipt and explicit corrections as an apply_patch.

The received Markdown is immutable. Run once after importing the author's
24 Markdown files and three metadata files; no foreign prose is regenerated.
"""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/language-writing'
FIXES = {
 ('ep01','ja'): [('だから言葉は、約束事を欠かせない一方で', 'だから言葉は、約束事なしには成り立たない一方で', 'Natural Japanese construction for the need for conventions.')],
 ('ep02','ja'): [
  ('これは、きちんとしたお見舞いの手紙みたいすぎる。', 'これは、お見舞いの手紙みたいに、かしこまりすぎている。', 'Natural spoken Japanese, with the same objection to formality.'),
  ('どんなに表現のうまいシステムでも、その能力だけを根拠に、いまのあなたの約束まで代わりに果たしたことにはできない。', 'どんなに表現のうまいシステムでも、その能力だけで、いまその言葉を自分のものとして引き受けるという行為まで、あなたに代わって済ませることはできない。', 'Distinguish undertaking a present commitment from fulfilling it later.')],
 ('ep01','ko'): [('담당자가 모든 행사는 같은 서식을 써야 한다고 한다고 해 보자.', '담당자가 모든 행사에 같은 서식을 쓰라고 한다고 해 보자.', 'Simplify nested reported speech; not a mechanical duplicate.')],
 ('ep02','ko'): [('시스템의 표현 능력이 아무리 뛰어나도 그 능력만으로 지금 내가 해야 할 약속까지 대신 마쳤다고 할 수는 없다.', '시스템의 표현 능력이 아무리 뛰어나도, 그 능력만으로 내가 지금 그 말을 내 말로 받아들이고 책임지는 일까지 대신할 수는 없다.', 'Clarify present ownership and responsibility, without adding an obligation to promise.')],
 ('ep01','es'): [('el texto no puede superar los ochenta palabras', 'el texto no puede superar las ochenta palabras', 'Feminine article agreement with palabras.')],
 ('ep02','es'): [('Por muy bien que se exprese un sistema, esa capacidad no basta para considerar cumplido, en tu lugar, el compromiso que estás adquiriendo ahora.', 'Por muy bien que se exprese un sistema, su capacidad de expresión no puede sustituir tu acto de asumir ahora ese compromiso.', 'Distinguish undertaking a present commitment from fulfilling it later.')],
 ('ep03','es'): [('Quizá esta vez tenga que intentar decirlo todo con claridad, en vez de detenerse otra vez en la puerta.', 'Quizá esta vez tenga que intentar decir de forma explícita aquello que le cuesta decir, en vez de detenerse otra vez en la puerta.', 'Optional precision: make the difficult thing explicit, not exhaust all meaning.')],
 ('ep02','fr'): [
  ('Est-ce que cela me fait de la peine ?', 'Est-ce une raison d’être triste ?', 'Retain the evaluative question, rather than only identifying an emotion.'),
  ('Peut-être deux problèmes étaient-ils jusque-là confondus, et qu’un bon texte vient de les séparer : comment dire cela ?', 'Peut-être un bon texte vient-il de séparer deux problèmes jusque-là confondus : comment dire cela ?', 'Repair incompatible coordination of inversion and et que.'),
  ('Une parole importante ne doit pas nécessairement avoir été inventée seul pour être la nôtre.', 'Nous n’avons pas à inventer seuls une parole importante pour qu’elle soit vraiment la nôtre.', 'Make the human agent of inventing clear.' )],
 ('ep03','fr'): [('des différences qu’il aurait fallu longtemps pour discerner seule', 'des différences qu’elle aurait mis longtemps à discerner seule', 'Clarify who takes time to distinguish the alternatives.')],
}


def main():
    receipt_path = DATA / 'multilingual-publication.json'
    assert not receipt_path.exists(), 'Publication already prepared'
    fixes=[]
    for (episode,language),rules in FIXES.items():
        text=(DATA/'received'/f'{episode}.{language}.md').read_text()
        for before,after,reason in rules:
            assert text.count(before)==1,(episode,language,before)
            fixes.append(dict(episode=episode,language=language,before=before,after=after,count=1,reason=reason))
            text=text.replace(before,after)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    archive=Path('/Users/hanqin/Documents/SAE旗舰系列多语言/语言与写作/language-writing-8-languages.zip')
    files=sorted(p for p in (DATA/'received').iterdir() if p.is_file())
    assert len(files)==27
    baseline=['data/language-writing/'+f'ep{i:02}.json' for i in range(1,4)]
    baseline+=['essays/sae/index.html','essays/language-writing/index.html']+['essays/language-writing/'+f'ep{i:02}.html' for i in range(1,4)]
    receipt={'date':'2026-11-03','baseline_commit':'a0a3d5f',
             'source_package':{'filename':archive.name,'sha256':sha(archive)},
             'languages':['de','fr','es','ja','ko'],'articles':['ep01','ep02','ep03'],
             'received_files':{str(p.relative_to(DATA)):sha(p) for p in files},
             'baseline_files':{name:sha(ROOT/name) for name in baseline},
             'policy':'Original Chinese/Traditional/English narrative text and addresses retained. All 15 new foreign bodies preserve their received paragraphs; only the recorded local corrections are applied during rendering. New localized indexes and UI are editorial additions. Offline HTML wrappers are not imported.',
             'review':'Lead reviewed all fifteen new essays against the approved Chinese. Three user-authorized agents independently cross-reviewed German/French, Spanish and Japanese/Korean. Final local changes were checked by lead; no translation service.'}
    print('*** Begin Patch')
    for path,value in ((DATA/'corrections.json',fixes),(receipt_path,receipt)):
        assert not path.exists()
        print('*** Add File: '+str(path))
        for line in (json.dumps(value,ensure_ascii=False,indent=2)+'\n').splitlines():print('+'+line)
    print('*** End Patch')


if __name__=='__main__':main()
