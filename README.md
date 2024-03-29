# Acquisition Order of Functional Morphemes

Mid-term project for the course [ENG-3040 First Language Acquisition](https://en.uit.no/education/courses/course?p_document_id=567082) at Universitetet i Tromsø, spring semester 2019.

Fourteen functional morphemes/categories in the English language and their order of acquisition, as presented by Brown (1973, pp. 254--274) (see also Owens (2012, pp. 274--286)):

|       | feature                  |
|-------|--------------------------|
| 1.    | present participle       |
| 2./3. | in, on                   |
| 4.    | regular plural           |
| 5.    | irregular past tense     |
| 6.    | possessive -'s/-s'              |
| 7.    | uncontractible copula    |
| 8.    | articles (the, a)                 |
| 9.    | regular past tense       |
| 10.   | regular 3.sg.pres        |
| 11.   | irregular 3.sg.pres      |
| 12.   | uncontractible auxiliary 'to be' |
| 13.   | contractible copula      |
| 14.   | contractible auxiliary 'to be'  |

O'Grady (2005, p. 94):
> [A]n ending or a word had been “acquired” if it appeared in 90 percent or more of the contexts where it was needed in three consecutive recording sessions. (The sessions were held about two weeks apart over a period of many months.)

**To what extent does this hold up to for a larger English corpus?**
What are the **shortcomings of an automated, quantitative analysis,** given that it is more coarse than manual inspection of the data?


## Implementation

The code is written in Python 3.6.7.
I use a version of NLTK's (Bird et al., 2009) corpus reader that I modified to parse the XML files of the CHILDES transcripts.

## Usage

Requires Python 3, and the libraries nltk, numpy, matplotlib.

```
python analyze.py
```

## References

Bird, Steven, Ewan Klein, and Edward Loper. _Natural Language Processing with Python: Analyzing Text with the Natural Language Toolkit._ O'Reilly Media, Inc., 2009.

Brown, Roger. _A first language: The early stages._ Harvard U. Press, 1973.

O'Grady, William. _How children learn language._ Cambridge University Press, 2005.

Owens, Robert E. _Language development: An introduction._ 8th Edition. Pearson, 2012.
