---
name: asd-ste100
description: Write in ASD-STE100 Simplified Technical English — one meaning per word, active voice, simple tenses, short sentences, small noun clusters. The visual-explainer and visual-plan skills require it for every human-readable string they produce. Also use it whenever the user asks for Simplified Technical English, or for plain, unambiguous prose.
---

# ASD-STE100 — Simplified Technical English

Write English in ASD-STE100 Simplified Technical English. STE is a controlled language. The aerospace industry built it so a reader who cannot ask a follow-up question still reads the text one way only. The rules are countable. Check your prose against them as you write.

## When to use

- A skill requires it. The `visual-explainer` and `visual-plan` skills require it for every human-readable string in their output.
- The user asks for Simplified Technical English, or for plain, unambiguous prose.

## Precedence

These rules set the default shape of the English you write. A more specific instruction takes precedence on whatever it addresses. This includes an instruction from the user, from project instructions, from an invoked skill, or from an established convention in the file you edit. Where the more specific instruction is silent, these rules apply.

Follow the more specific instruction without comment. Do not cite this style as a reason to override it. Do not ask permission. This exception applies to an explicit instruction only. Do not relax these rules because a topic feels casual or because other prose seems friendlier.

## Never apply these rules to

- Code. This includes identifiers, syntax, and string literals.
- Quoted material. This includes error output, command output, file contents, and another person's words. To rewrite a quotation is falsification, not simplification.
- Text where the exact wording carries the meaning. This includes a command to run, an API name, a config key, and an exact error string.

## Rules

| Rule | Limit |
| --- | --- |
| Noun clusters | Maximum 3 words stacked as a modifier. Break a longer stack apart and name the relationship. |
| Sentence length | Maximum 20 words for an instruction or a procedure. Maximum 25 words for descriptive text. |
| One instruction per sentence | Do not join two instructions with "and" or "then". |
| Active voice | Use the passive voice in descriptive text only, and only when the actor is unknown or irrelevant. |
| Simple tenses only | Use the infinitive, the imperative, the simple present, the simple past, and the simple future. Use a past participle as an adjective only. Do not use the present perfect, the past perfect, or a compound auxiliary. |
| No `-ing` verb forms | Use an `-ing` word as a technical noun, or as part of one, only. |
| No hedge stacking | Do not chain modal verbs, as in "may have been caused by". State the uncertainty as its own plain sentence: "The cause is not confirmed." |
| One word, one meaning | Use one term for one concept and repeat it. Do not rotate synonyms for the same idea. |
| Plainest available word | Prefer the short common word to the formal or rare word. |
| Define domain terms | Define a term that is not common English at its first use. Do not carry undefined shorthand forward. |
| No ellipsis | Keep the subject, the verb, and the article explicit, even when the sentence reads longer. |
| Paragraphs | One topic. Maximum 6 sentences. |
| Vertical lists | Use a numbered or bulleted list for 3 or more steps or conditions. |

## Project vocabulary

STE permits a project to define its own approved vocabulary of technical nouns and verbs. A `CONTEXT.md` file at a repository root is that vocabulary.

If the project has a `CONTEXT.md`, use its terms exactly as it defines them, in the part of speech it defines. Never substitute a synonym for a term it defines. Never use a word that its `_Avoid_` lines reject. Do not redefine its terms inline, because the glossary is the definition.

If the project has no `CONTEXT.md`, do not invent one. Do not present any term as already established. The rules above apply without change: define a term at first use, prefer the plainest word, and use one term for one concept.

## Length is not terseness

The caps apply to each sentence, not to the response. Clarity is the goal, not concision. A long answer in short sentences is correct.

Never drop a fact, a condition, a caveat, or a scope qualifier to meet a limit. Split the sentence instead.
