# Frostpunk (2018) independent preaudit — moon

## Scope
Read all four existing Chinese essays in full, coordinator preaudit and cities primary-evidence report. No repository source edits. Original PC game only, not Frostpunk 2, tabletop rules or 1886 remake. This is targeted primary visual corroboration, not a complete playthrough or code audit.

## Directly inspected primary game visuals

### Individual assistance exists
Event screenshot actually opened at 1920x1080: `/tmp/frost-moon-father.jpg`.
https://static.wikia.nocookie.net/frostpunk_gamepedia_en/images/2/29/Desperate_Father_-_Runaway_child.png/revision/latest?cb=20190608022922
Linked by https://frostpunk.fandom.com/wiki/Desperate_Father_(Arc)
The original event UI presents a father asking to search for his daughter and three choices: provision his journey, ignore him, or prevent departure. This directly contradicts EP1’s claim that no button can help a particular individual. The screenshot does not establish the exact provisioning cost, because that option is not selected. Do not add a precise food quantity from this image alone.
Minimum prose repair: most sustained management works through resources, laws and buildings, but individual events also let the captain help or refuse a specific person. Preserve aggregate vision as a tendency, not an interface impossibility.

### Heating is not only concentric generator distance
Two original 2018 technology UI screenshots inspected at 1280x720:
https://www.pwrdown.com/wp-content/uploads/2018/05/Heaters.jpg
https://www.pwrdown.com/wp-content/uploads/2018/05/SteamHub.jpg
Host article published 2018-05-26: https://www.pwrdown.com/gaming/frostpunk-how-to-keep-the-arks-warm/
Local `/tmp/frost-moon-heater.jpg`, `/tmp/frost-moon-hub.jpg`.
The heater tooltip describes workplace heating during working hours. The hub tooltip describes additional local heat zones powered by the Generator. These are direct game UI, hosted by a third party. The central Generator remains essential, but the article cannot assert that every further ring is necessarily colder or that all building heat comes only from its original radius. Minimum repair: describe initial dependence on central heat, then briefly acknowledge extensions/workplace heat rather than turn the essay into a technical guide.

### Decisions continue during the storm
Original event screenshot inspected at 1920x1080: `/tmp/frost-moon-mine.jpg`.
https://static.wikia.nocookie.net/frostpunk_gamepedia_en/images/7/78/Coal_Mine_Crisis_-_The_mines_are_freezing%21.png/revision/latest?cb=20190608023535
Linked by https://frostpunk.fandom.com/wiki/Coal_Mine_Crisis_(Arc)
The displayed mine-freezing event offers sending volunteers to replace failing supports or abandoning the lower levels; its selected tooltip warns of possible deaths. The community event page locates this arc during the storm. Thus the event image is direct corroboration of agency under extreme cold, with timing corroborated by the event transcription rather than a full storm recording here. Withdraw the categorical claim that once the storm starts nothing can be done. Keep the feeling of constrained agency and helpless waiting without presenting total input lockout.

### Not every successful ending asks whether it was worth it
Public original-game recording: Zsolt Korossy, 2018-06-11, Frostpunk - New Home Order good ending (Medium difficulty).
https://www.youtube.com/watch?v=5w2x-iGJuiM
Actually inspected public 160x90 storyboard frames every two seconds from 50 to 142 seconds, not continuous video/audio. Cached metadata `/tmp/frost-moon-ending.html`; sheets `/tmp/frost-moon-ending-sheet1.jpg`, `/tmp/frost-moon-ending-sheet2.jpg`.
Near 116–118 seconds, visible ending text says the line has not been crossed; around 124–126 seconds it says the city thrived. It then ends on the New London year/population card. This is sufficient visual counterevidence to the essay’s universal worth-it ending formulation. The small images do not support exact transcription of all intermediate recap text; no such claim is made.
Minimum repair: open EP4 with a particular crossing-the-line ending, not every victory. Do not equate the entire retrospective moral reckoning with one literal line appearing in every result.

## Crossing-the-line flags remain only partly established here
No original game script, source code or developer-authored exhaustive flag table was obtained. Community lists commonly name the late Purpose laws, but reports dispute some ability/event interactions. A single good-ending recording cannot prove all necessary/sufficient conditions. Therefore do not certify the six-law list as an exhaustive algorithm or absolute claims about every use of Public Penance. The strongest defensible essay wording distinguishes the game’s explicit crossing marker from all suffering recounted in the ending, identifies final New Order/New Faith as clear endpoints, and presents the civic-voice argument as interpretation rather than a code-level fact. Signing a final law changes hope mechanics, not literal impossibility of discontent.

## Coordination boundaries
Cities separately established Winterhome New Order visuals and original developer scenario slides; this report does not claim independent re-viewing of those files. Their limited-evacuation correction is consistent with the four-essay reading. Preserve the author’s arguments about cumulative expediency and allocation; remove false categorical premises without replacing them with an opposite political thesis. No verified basis was added for prison-graffiti costs, music or all flag edge cases.

## Candidate source independent full review and final delta

Reviewer moon, independent of source editor catch22. Status: passed for translation freeze.
Final source SHA256: 5d2c81df235859906cb43d3c3a2a0b36fc4f7c45b0618bfda4fb8cda26625d33

Read original four Chinese essays in full, then candidate revised Chinese 64 / 63 / 63 / 64 = 254 blocks in full, including headings and source notes. Subsequently re-read the final 14 changed blocks: 1:11/49/64; 2:24/60/61/63; 3:1/2/3/19/63; 4:19/64. This is a full candidate read plus delta verification, not a claim of another complete fresh read after the final changes.

Final changes consistently remove unverified absolute claims: captain visibility is limited to ordinary management; the ethical boundary is read interpretively, not as a certified flag algorithm; child labour is not claimed to directly raise discontent as the inevitable first step toward Order; the second essay explicitly returns to the earlier branch point; scout discovery does not require the party to return physically; the better-generator comparison is removed. Chinese terminology is no longer certified as an exact official localization.

Also read /tmp/frostpunk-law-ui-primary.md and actually inspected /tmp/frost-vandalism.png. The latter visibly places the writing on the Propaganda Centre, offers punishment or removal, and shows the selected removal option slightly raising hope. The revised example preserves the institutional-treatment argument without inventing imprisonment, zero cost, or an unobserved punishment tooltip. This reviewer did not separately re-view the four child-law screenshots described by the coordinator or the Winterhome recording inspected by cities; those are attributed corroboration, not my own visual claims.

All major revised dependencies were examined: shelter/apprenticeship separation; individual aid versus aggregate management; heat zones; ultimatums; purpose-route functional differences; overt final-law violence; hope versus discontent; storm agency; differentiated ending text; Winterhome evacuation and usable laws. The cumulative-expediency and authority/answerability interpretations remain the author’s argument, not a new opposing thesis. Exact exhaustive crossing flags, every difficulty/patch behavior and precise unobserved audiovisual details remain uncertified. No source text was edited by this reviewer.
