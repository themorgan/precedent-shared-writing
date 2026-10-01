---
slug:        language-variety
title:       English is American English; Spanish is Argentine Spanish
tier:        resident
severity:    default
applies_to:  ["**"]
occasion:    "writing anything in English or in Spanish -- a reply, a document, a commit message"
gates:       []
index_clause: "English is American (color, apartment); Spanish is Argentine (vos tenés, auto)"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-09-29
approved_by: "Morgan F, 2026-09-29 -- requested directly, with Go update, in the same message; sole approver in approvers.json. Rule text shortened, same meaning, on 2026-10-01 in the reduction pass Morgan approved that day: \"Question 3 - all are great, approved\" (strength: decided)."
strength:    decided
---
## Rule
**Write English as an American writes it and Spanish as an Argentine
writes it** (*color*, *apartment*; *vos tenés*, *celular*) in replies,
documents and commit messages. **Quoted material, proper names, and a
variety asked for on a given piece keep their own form**; `## Detail` has
the specifics.

## Detail
**Spelling, vocabulary and grammar alike**, in both languages. So
*color*, *organize*, *apartment*, *the team is*; and *vos tenés*, *mirá*,
*ustedes*, *auto*, *celular*.

**American English.**

- **Spelling:** *-or* not *-our* (color, behavior), *-ize* not *-ise*
  (organize, realize), *-er* not *-re* (center, theater), *-se* in nouns
  (defense, license), single *l* before a suffix (traveled, canceled),
  *program*, *check*, *gray*, *catalog*.
- **Vocabulary:** apartment, elevator, cell phone, truck, gas, sidewalk,
  vacation, fall (the season), line (not queue), zip code.
- **Grammar and punctuation:** a collective noun takes a singular verb
  (*the team is*, *the committee has decided*); *gotten* is fine; periods
  and commas go inside the closing quotation mark; double quotes outside,
  single quotes inside. Dates read *September 29, 2026* in prose.

**Argentine Spanish.**

- **Voseo, wherever *tú* would go:** *vos tenés*, *vos sabés*, *vos
  sos*; imperatives *mirá*, *decime*, *fijate*, *tené en cuenta*. **Formal
  *usted* stays *usted*** -- voseo replaces *tú*, not the formal register.
- **Plural address is *ustedes*,** never *vosotros* or its forms
  (*tenéis*, *os*).
- **Vocabulary:** auto (not coche or carro), computadora (not ordenador),
  celular (not móvil), departamento (not piso), colectivo, manejar (not
  conducir), heladera, pileta, remera, frutilla, palta, lapicera.
- **Grammar:** prefer the simple past for a finished event, even today's
  (*hoy terminé el informe*, not *hoy he terminado*). Spelling follows the
  Real Academia Española (RAE), which Argentine usage shares.

**What keeps its own form.** A direct quotation stays as the source wrote
it. So does a proper name or an official title (*Ministry of Defence*,
*Centre Pompidou*), a code identifier, and a file or product name. When
the person asks for another variety on a particular piece -- British
English for a UK client, neutral Spanish for a pan-regional audience --
that request governs the piece; this rule is the default, not a ceiling.

**Other languages** are outside this rule.

## Why
A document that drifts between varieties -- *color* in one paragraph and
*colour* in the next, *vos* in one line and *tú* in the following -- reads
as careless even when every word is correct. Models drift easily, because
their training mixes every variety of both languages. Naming the variety
once, as a standing default, means nobody has to spot and fix it by eye.

## Story
Requested by Morgan on 2026-09-29, in a session rooted in this set:
*"when writing in English, use American spelling, vocabulary, and grammar;
and when writing in Spanish, use Argentine spelling, vocabulary, and
grammar."* Placed here rather than in an individual set because he asked
for it in this repository, which is about the craft of writing for a human
reader. Made resident rather than on-demand because nearly everything a
session writes is in one of the two languages, so an occasion that fires on
"writing in English" would fire on every reply.

**Shortened 2026-10-01**, in the reduction pass Morgan approved that day
("Question 3 - all are great, approved", strength: decided), because a
resident rule is paid for in every session. The meaning is unchanged: the
examples the Rule dropped, and its "spelling, vocabulary and grammar
alike", opened `## Detail` instead.

## Install
Nothing to install: the rule is carried by the resident block. No
mechanical check -- telling a quoted *colour* or a proper name from a
drift needs judgment a pattern match does not have.
