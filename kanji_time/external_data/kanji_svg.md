General
=======

A Kanji stroke diagram has two large components:

- the drawing instructions
- textual annotations

KanjiSVG groups drawing instructions into a `StrokePaths` collection (a/k/a SVG group) for each Kanji.
The `StrokePaths` record itself provides header information applicable to the kanji as a whole.
`StrokePaths` records further decompose into `StrokeGroups` and then `Strokes` withing each `StrokeGroup`.

- A `Stroke` corresponds to a single brush stroke of a kanji.
- A `StrokeGroup` is a collection of `Strokes` for a sub-structure within a kanji that roughly corresponds to a well-known kanji radical.

The textual annotations in a `StrokeNumbers` record directly pairs with a `StrokePaths` record.
Each annotation in the `StrokeNumbers` associates with exactly one `id` value within its paired `StrokePaths`.
The annotation also contains drawing and postioning instructions for the annotation.

Kanji SVG assocates annotations with individual stokes.
These annotations are a sequential numbering from 1 to the # of strokes that show the drawing order.

```sql
CREATE TYPE group_position AS ENUM
    (
     'bottom' 
    ,'kamae'
    ,'left'
    ,'nyo'
    ,'nyoc'
    ,'right'
    ,'tare'
    ,'tarec'
    ,'top'
    );

CREATE TYPE radical_class AS ENUM
    (
     'general'
    ,'jis'
    ,'nelson'
    ,'tradit'
    );

CREATE TABLE KanjiStrokePaths
    (
     id             CHAR(5) NOT NULL/* 5 character hex encoding for KanjiSVG, but not required to be */
    ,element        CHAR(1) NOT NULL
    ,number         SMALLINT    /* NULLABLE */
    ,original       CHAR(1)     /* NULLABLE */
    ,part           SMALLINT    /* NULLABLE */
    ,partial        BOOLEAN NOT NULL
    ,phon           CHAR(1)     /* NULLABLE */
    ,position       group_position
    ,radical        radical_class
    ,radical_form   BOOLEAN   /* NULLABLE */
    ,trad_form      BOOLEAN
    ,variant        BOOLEAN
    );
```

StrokePaths
===========


A StrokePath instance is a specialization of an SVG group element <g>

General attributes - from SVG
-----------------------------

id: CHAR(5)

```sql
COMMENT ON COLUMN StrokePaths.id IS 
    '
The KanjiVG identification number for this group. It contains the Unicode value of the kanji as a five-digit lower-case hexadecimal number, followed by a hyphen and the letter "g", followed by a decimal number from one to the total number of groups.

The group ID numbers are always consecutive positive whole numbers.
    ';
```

KVG namespace attributes
------------------------

All these attributes are placed under the kvg namespace, for example kvg:original="家"

element: CHAR(1)

```sql
COMMENT ON COLUMN StrokePaths.element IS
    '
This attribute specifies which kanji best represents the group physically. It should be the Unicode character that resembles the group as much as possible.

The value of element on the outermost group of the strokes is the same as the kanji represented by the SVG.
    ';
```

number: SMALLINT

```sql
COMMENT ON COLUMN StrokePaths.number IS
    '
This relatively rare attribute allows an element of a kanji to be identified when it is both represented several times in the kanji, and, due to the stroke order, more than one of these representations is broken into parts, so that the part attribute has to be used for more than one element. In other words, the number attribute is a way to uniquely identify the part when it becomes ambiguous.

It is only used in a few places in kanjivg where there are two different sets of the same element, such as 05716.svg, the character 圖, where there are four 口 elements, two of which are broken into parts one and two due to the stroke order. Please inspect the source code of that SVG file to understand what kvg:number attribute does.

Generally, elements which can be represented by contiguous blocks of strokes do not have a number attribute, even if multiple cases of the same element occur in a character, so, for example, the 口 elements of 品 do not have a number attribute.
    ';
```

original: CHAR(1)

```sql
COMMENT ON COLUMN StrokePaths.original IS
    '
This attribute specifies which kanji represents the group from a semantic point of view. This attribute only needs to be present if there is a difference between the semantic and physical representation of the group.

For example, 仮 has two groups. The left one has 亻 (called ninben) for its element attribute, and 人, meaning "person", for its original attribute, because ninben is a variation of 人. However, the right side has 反 for element, which is not a variation, so an original attribute is not necessary.
    ';
```

part: SMALLINT 

```sql
COMMENT ON COLUMN StrokePaths.part IS
    '
When the elements of a group of kanji strokes which forms a larger unit are not consecutive strokes, the group of strokes may be spread over several groups of paths in the file. The part attribute allows numbering these groups and defines them as being part of the same component. There is also a number attribute which can be used in the rare cases that two groups with the same element have non-consecutive strokes within the same character.
    ';
```

partial: BOOLEAN 

```sql
COMMENT ON COLUMN StrokePaths.partial IS
    '
Should be present and set to true if the group only represents the element attribute partially, i.e. if not all its strokes are present.
    ';
```    

phon: CHAR)1)

```sql
COMMENT ON COLUMN StrokePaths.phon IS
    '
A large number of kanji consist of a radical and a phoneticum, the Sino-Japanese pronunciation. The phon attribute should mark the part indicating the pronunciation.

The values of this attribute are inconsistent, and the meanings of many of them are completely undocumented. See issue 312 on Github for more details.
    ';
```    


position: ENUMERATED

```sql
COMMENT ON COLUMN StrokePaths.position IS
    '
Defines where this groups is located with respect to the other groups with the same parent. Not every element has a "position" value. Possible values are

bottom
    This part is under another part. 
kamae
    This part is wrapped around another part, such as 門. This is used very inconsistently in KanjiVG as a grab-bag for various different structures. 
left
    This part is left of another part. 
nyo
    This part is left and under another part, such as 辶. 
nyoc
    This part is the complement or counterpart of a nyo part. 
right
    This part is right of another part. 
tare
    This part is left and above another part, such as 广. 
tarec
    This part is the complement or counterpart of a tare part. 
top
    This part is above another part. 
    ';
```    

radical: ENUMERATED

```sql
COMMENT ON COLUMN StrokePaths.radical IS
    '
This is set to a value if this group of strokes is considered a radical of the kanji, and by which reference. The value of the attribute depends on the reference, as follows.

general
    The generally accepted radical which authors agree on. 
jis
    This marks the radicals used by JIS Kanji Jiten, used by Kanjidic, which sometimes differ from the general or tradit radicals. This value was added to deal with inconsistencies between KanjiVG and Kanjidic and other references. 
nelson
    The keyword "nelson" is used for Nelson radicals. 
tradit
    The keyword "tradit" is used for the "traditional" radical, where the Kangxi radical disagrees with Nelson. 
    ';
```    

radical_form: BOOLEAN

```sql
COMMENT ON COLUMN StrokePaths.radical_form IS
    '
This is set to the value true for a limited number of groups where a radical-like form of a character described by original is provided as the element.
    ';
```    

trad_form: BOOLEAN

```sql
COMMENT ON COLUMN StrokePaths.trad_form IS
    '
The Kanjidic file with which Ulrich Apel worked in the beginning favored the radicals given in the Nelson character dictionary, which sometimes differ from the radicals given in "traditional" Japanese dictionaries and have mark-up as well.
    ';
```    

variant: BOOLEAN

```sql
COMMENT ON COLUMN StrokePaths.trad_form IS
    '
Unknown, possibly used to indicate that the shape of the element is unlike the usual grapheme.
    ';
```    

Strokes
=======

Each individual kanji stroke is represented by one SVG <path> element.

General attributes - from SVG
-----------------------------

d: XML

```sql
COMMENT ON COLUMN Stroke.d IS
    '
The SVG path information itself. This describes the shape of the line.

Although there is no rule disallowing various SVG elements, in practice all of the KanjiVG data consists of cubic bezier curves. In the SVG terminology the path is made up of only M/m, C/c, and S/s elements. There are no other SVG path elements present. None of the strokes contains a path with more than one sub-path, that is to say there are no strokes with more than one "moveto" element.
    ';
```    


id: VARCHAR(20)

```sql
COMMENT ON COLUMN Stroke.id IS
    '
The KanjiVG identification number for this stroke. It contains the prefix kvg: followed by the Unicode value of the kanji as a five-digit lower-case hexadecimal number, followed by any variant information, followed by a hyphen and the letter "s", followed by a decimal number from one to the total stroke count. For example stroke 3 of the file kanji/053ec.svg has the ID number kvg:053ec-s3.

The stroke IDs are consecutive positive whole numbers starting from 1 which correspond to the stroke number of the stroke.
    ';
```    


KVG namespace attributes
------------------------

These attributes are under the kvg: namespace.

type: CHAR(1)

```sql
COMMENT ON COLUMN Stroke.type IS
    '
The shape of the stroke. It can be used to know how the stroke should be rendered.

The values of this attribute use the keys of Unicode''s CJK Strokes, which occupy code positions from U+31C0 to U+31EF. The names of these, such as D or HZ, are the initials of the Chinese names.

Please see the Stroke types page for full information on stroke types.
    ';
```    

Stroke numbers
==============

Stroke numbers are represented by a top-level group with an ID of the form kvg:StrokeNumbers_abcde, where abcde is the identifier of the file. This group contains text elements. Each text element is located on the diagram using a transform attribute. The text within each text element is the stroke number in digits, from one to the total number of strokes. The stroke numbers should correspond to the id value of the individual strokes.

The stroke numbers are located to the side of the beginning of the stroke whose order they indicate. Generally, they should not overlap the strokes.
