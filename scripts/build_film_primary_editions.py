#!/usr/bin/env python3
"""Build/check primary film editions without opening foreign-language sources."""
import argparse
import film_targeted_editions as t

def outputs():
    result={}
    for slug in t.SLUGS:
        root=t.ROOT/'essays/film'/slug
        chapters=sorted(root.glob('[123]-*.html'));assert len(chapters)==3
        film={'slug':slug,'chapters':[p.stem for p in chapters]}
        for path in [root/'index.html',*chapters]:
            result[path]=t.overlay(path.read_text(),film,path.name)
    result.update(t.approved_traditional_outputs())
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=outputs()
    for path,text in result.items():
        if args.check:assert path.read_text()==text,path
        else:path.write_text(text)
    print(('Verified' if args.check else 'Built'),len(result),'primary film pages/dictionaries; foreign sources not opened')
if __name__=='__main__':main()
