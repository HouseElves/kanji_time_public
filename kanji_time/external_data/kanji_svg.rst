General
=======

A Kanji stroke diagram has two large components:

- the drawing instructions
- textual annotations

KanjiSVG collects the drawing instructions for a kanji into an SVG group with a `StrokePaths` id.
Similarly, it collects the textual annotations into an SVG group with a `StrokeNumbers` id.

The `StrokePaths` record itself provides header and styling information applicable to the kanji as a whole.
`StrokePaths` records further decompose into the `Element` header, which contains `StrokeGroups` and then `Strokes` (or nested `StrokeGroup`s) within each `StrokeGroup`.

- A `Stroke` corresponds to a single brush stroke of a kanji.
- A `StrokeGroup` is a collection of `Strokes` or `StrokeGroup`s for a sub-structure within a kanji that roughly corresponds to a well-known kanji radical.
- The `Element` header identifies the kanji to which these drawing instructions pertain.

The textual annotations in a `StrokeNumbers` record directly pairs with a `StrokePaths` record.
Each annotation in the `StrokeNumbers` associates with exactly one `id` value within its paired `StrokePaths`.
The annotation also contains drawing and postioning instructions for the annotation.
In particular, KanjiSVG assocates annotations with individual stokes.
These annotations are a sequential numbering from 1 to the # of strokes that show the drawing order.

'id' Magic
----------

Each kanji's stroke diagram lives in a file NNNNN.svg, where NNNNN is the 5 digit hex representation of the kanji's Unicode code point.
The various XML elements within that file each have an 'id' attribute.
KanjiSVG imposes a smart-encoding scheme on these 'id' values to define relationship links between them.

The process of moving KanjiSVG into an RDBMS can exploit these smart-encoding schemes to define and enforce the same relationships between tables.

Drawing Instructions' 'id' Encoding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following the above convention, NNNNN always refers to the 5 digit hex representation of a particular kanji's Unicode code point in this discussion.

* The topmost SVG group is the Strokepaths group. It is marked as such with an id of the form `id="kvg:StrokePaths_NNNNN"`.
* Within this group is the Element group (which is not explicitly called out in the KanjiSVG documentation). Its id attribute has the form `id="kvg:NNNNN"`.
* The Element group contains one or more SVG groups marked as a StrokeGroup with an id of the form `id="kvg:NNNNN-gJ"`, where `J` is the 1-based index of the group across the entire Element group..
* Each StrokeGroup contains one or more SVG paths marked as a StrokePath with an ide of the form `id="kvg:NNNNN-sK"`, where `K` is the 1-based index of the stroke across the entire Element group.


Enumerated Values as PostGRES Domains
-------------------------------------

Kanji Variants
^^^^^^^^^^^^^^

Kanji variants are identified by a suffix on the id.

.. code:: sql

    CREATE DOMAIN kanji_variant AS TEXT CHECK
        (
        VALUE IN
            (
             'DgLst'
            ,'Dg3'
            ,'Hyougai'
            ,'Hz'
            ,'HzFst'
            ,'HzFstLeRi'
            ,'HzFstRiLe'
            ,'HzFstVtLst'
            ,'HzLst'
            ,'Insatsu'
            ,'Jinmei'
            ,'Kaisho'
            ,'Le'
            ,'LeFst'
            ,'MdLst'
            ,'MidFst'
            ,'NoDot'
            ,'Ri'
            ,'Ten3'
            ,'TenLst'
            ,'Vt'
            ,'Vt4'
            ,'Vt6'
            ,'VtFst'
            ,'VtFstRiLe'
            ,'VtLst'
            ,''
            )
        );

    COMMENT ON DOMAIN kanji_variant IS
        '
    KanjiVG includes data on variations of characters and stroke order. For example, when characters in the schoolbook style deviate from traditional kaisho, there might be an extra file containing the kaisho version of the character. This file is named using the same Unicode value as the schoolbook style kanji, with the suffix -Kaisho. For example the kaisho variant of 島, 05cf6.svg is named 05cfa-Kaisho.svg.
    
    There are also different versions for different stroke orders. 
        ';

    CREATE TABLE kanji_variant_metadata 
        (
         kanji_variant_value     kanji_variant PRIMARY KEY
        ,help_text               TEXT NOT NULL
        );
    INSERT INTO kanji_variant_metadata 
        (
         kanji_variant_value
        ,help_text
        )
    VALUES  
         ('DgLst', 'Used for a stroke order variant of 癶.')
        ,('Dg3', 'Used for a stroke order variant of 癶.')
        ,('Hyougai', 'Variant forms of the character, called "hyougai" (表外) in Japanese. These are often the characters for different Unicode code points, or otherwise inconsistent.')
        ,('Hz', 'Horizontal')
        ,('HzFst', 'Horizontal First stroke order')
        ,('HzFstLeRi', 'Horizontal First, Left to Right stroke order')
        ,('HzFstRiLe', 'Horizontal First, Right to Left stroke order')
        ,('HzFstVtLst', 'Horizontal First, Vertical Last')
        ,('HzLst', 'Horizontal Last')
        ,('Insatsu', 'Printed form (印刷), where it differs from the schoolbook format. This is used inconsistently.')
        ,('Jinmei', 'Versions of the character used for names, which appear in the Jinmei list. In practice these often refer to different Unicode code points than the ones given.')
        ,('Kaisho', 'Kaisho variant. In practice this usually seems to mean something like 月 or 日 with a shorter middle stroke which doesn''t go all the way to the right side of the element.')
        ,('Le', 'Left')
        ,('LeFst', 'Left First')
        ,('MdLst', 'Middle Last')
        ,('MidFst', 'Middle First')
        ,('NoDot', 'Used for a variant of 饗 only.')
        ,('Ri', 'Right')
        ,('Ten3', 'These characters all contain a 必 element, with the strokes in a different order than usual.')
        ,('TenLst', 'These characters all contain a 卵 element, with the centre right shortest stroke coming last in the stroke order.')
        ,('Vt', 'Vertical')
        ,('Vt4', 'These characters contain a variant stroke order with a vertical as the fourth stroke.')
        ,('Vt6', 'These characters contain a variant stroke order with a vertical as the sixth stroke.')
        ,('VtFst', 'Vertical First')
        ,('VtFstRiLe', 'Vertical First Right to Left')
        ,('VtLst', 'Vertical Last')
        ,('', 'Primary')
        ;


Stroke Types
^^^^^^^^^^^^

.. code:: sql

    CREATE DOMAIN kanji_stroke_type_primitive AS TEXT CHECK
        (
        VALUE IN
            (
             '㇀'
            ,'㇁' 
            ,'㇂'
            ,'㇃'
            ,'㇄'
            ,'㇅'
            ,'㇆'
            ,'㇇'
            ,'㇈'
            ,'㇉'
            ,'㇋'
            ,'㇏'
            ,'㇐'
            ,'㇑'
            ,'㇒'
            ,'㇓'
            ,'㇔'
            ,'㇕'
            ,'㇖'
            ,'㇗'
            ,'㇙'
            ,'㇚'
            ,'㇛'
            ,'㇜'
            ,'㇞'
            ,'㇟'
            ,'㇡'
            ,'６'
            ,'a'
            ,'b'
            ,'c'
            ,'v'
            ,'/'
            ,'㇌'
            ,'㇊'
            ,'㇎'
            ,'㇣'
            )
        );

    COMMENT ON DOMAIN kanji_stroke_type_primitive IS
        '
    The type attribute of a stroke specifies its shape. It can be used to know how the stroke should be rendered.

    The values of this attribute use the keys of Unicode's CJK Strokes.

    The best documentation available on the meanings of these stroke types seems to be that found in Proposed additions to the CJK Strokes block of the UCS, and the explanation of the stroke types there mostly consists of a list of examples, so there is some remaining ambiguity about how best to use these.

    In some cases these stroke types, in particular ㇁ (U+31C1), or ㇔ (U+31D4), may appear to be in error, but check the explanations below before suggesting changes.

    In other cases another field consisting of alphabetical letters. These letters refer to a set of stroke types which Ulrich Apel designed but has not documented. The letters seem to indicate the intersections of the ends of strokes with other strokes. See issue 324 on Github for more details.
        ';

    CREATE TABLE kanji_stroke_type_primitive_metadata 
        (
         kanji_stroke_type_value    kanji_stroke_type PRIMARY KEY
        ,cjk_stroke                 TEXT NOT NULL
        ,help_text                  TEXT NOT NULL
        );
    INSERT INTO kanji_stroke_type_metadata 
        (
         kanji_stroke_type_value
        ,help_text
        )
    VALUES  
         ('㇀', 'CJK Stroke T U+31C0', 'This stroke is the lower left one in 冰 and 氾. It always goes from left to right and upwards. See ㇒ (CJK Stroke P) for a similar-looking stroke which goes in the opposite direction.')
        ,('㇁', 'CJK Stroke WG U+31C1', 'This is used for the down stroke of 犭 and the lower right part of ⻖. Some fonts, including the default font used by KanjiVG's host, github.com, represent this shape as being almost identical to ㇓ (CJK Stroke SP), so it may appear to be an error on a browser screen. However, this is the correct shape for 犭 and ⻖.')
        ,('㇂', 'CJK Stroke XG U+31C2', 'This is used in, for example, for the long vertical stroke of 戈. ')
        ,('㇃', 'CJK Stroke BXG U+31C3', 'Used for the second, long stroke of 心. ')
        ,('㇄', 'CJK Stroke SW U+31C4', '')
        ,('㇅', 'CJK Stroke HZZ U+31C5', 'This relatively rare shape is used, for example, for stroke 15 of 麌. ')
        ,('㇆', 'CJK Stroke HZG U+31C6', 'This is used for the right side of 印 or 掏. ')
        ,('㇇', 'CJK Stroke HP U+31C7', ' This is the correct stroke type for 又，双，叒， and 今. See also See also ㇖ (CJK Stroke HG). ')
        ,('㇈', 'CJK Stroke HZWG U+31C8', 'The examples given in the Unicode reference are 飞，风，瘋，九，几，气，虱 ')
        ,('㇉', 'CJK Stroke SZWG U+31C9', 'This is used, for example, for the bottom part of 弓. ')
        ,('㇋', 'CJK Stroke HZZP U+31CB', '')
        ,('㇏', 'CJK Stroke N U+31CF', 'This stroke type is used for the right part of 人 and similar strokes in 大 and 天, and also for the long stroke at the bottom of 道 and 走. ')
        ,('㇐', 'CJK Stroke H U+31D0', 'This is used for horizontal lines, such as the top and bottom strokes of 西.')
        ,('㇑', 'CJK Stroke S U+31D1', '')
        ,('㇒', 'CJK Stroke P U+31D2', 'This stroke is the lower left one in 木, always goes from right to left and downwards. See ㇀ (CJK Stroke T) for a similar-looking stroke which goes in the opposite direction. ')
        ,('㇓', 'CJK Stroke SP U+31D3', 'This stroke is used for vertical strokes whose ends turn left. Depending on the font, it is easily confused with ㇁ (CJK Stroke WG), but that is actually a stroke going diagonally left to right at its top. ')
        ,('㇔', 'CJK Stroke D U+31D4', ' This is used for a short dash. Although the usual form of this in fonts is a line slanting down to the right, the dash may slant either down and left, such as the left stroke of 心 or 灬, or down and right, such as the right strokes of 心 or 灬. ')
        ,('㇕', 'CJK Stroke HZ U+31D5', 'This is used for the upper right part of 口, or the middle upper stroke of 巨. ')
        ,('㇖', 'CJK Stroke HG U+31D6', 'This is the correct stroke type for 疋，了，予，矛， 子，字，疏，写，and 冖. See also ㇇ (CJK Stroke HP). ')
        ,('㇗', 'CJK Stroke SZ U+31D7', '')
        ,('㇙', 'CJK Stroke ST U+31D9', 'This is used for the bottom left of 衣 or 食. ')
        ,('㇚', 'CJK Stroke SG U+31DA', '')
        ,('㇛', 'CJK Stroke PD U+31DB', 'This stroke type is used for the left vertical stroke of 女, or kanji which contain 女 as a component, or for 巛 and kanji containing a 巛 element. ')
        ,('㇜', 'CJK Stroke PZ U+31DC', '')
        ,('㇞', 'CJK Stroke SZZ U+31DE', 'This rare stroke type is only used in the character 亞, and characters such as 壼 which contain 亞 as a component. ')
        ,('㇟', 'CJK Stroke SWG U+31DF', '')
        ,('㇡', 'CJK Stroke HZZZG U+31E1', '')
        ,('６', '', 'For reasons which have not been documented, this was used in some characters such as 蠣 or 寓 to represent one of the lower strokes. ')
        ,('a', '', 'End touches middle part of other stroke')
        ,('b', '', 'End touches end of other stroke')
        ,('c', '', 'Unknown')
        ,('v', '', 'Unknown')
        ,('/', '', 'Where the value has two possibilities, a slash is used to separate them. For example, the bottom dash in 冬 (fuyu, "winter") may slant either upwards or downwards, so this is represented by kvg:type="㇔/㇀" in the KanjiVG source file.')
        ,('㇌', 'CJK Stroke HPWG U+31CC', 'This stroke pattern is used to represent the right side of ⻖ and related shapes when it is written as two strokes, per the Chinese convention. KanjiVG always uses three strokes to write ⻖, with the right side broken into upper and lower pieces, so this pattern is not used by KanjiVG.')
        ,('㇊', 'CJK Stroke HZT', 'U+31CA The main use of this seems to be to represent the 言 component known as gonben in simplified Chinese characters like 计, or other simplified Chinese forms such as so it is not very useful for Japanese.' )
        ,('㇎', 'CJK Stroke HZZZ U+31CE' 'This rare pattern seems to only be used in the Chinese drawing of 凸. Japanese uses a different stroke pattern for this character.')
        ,('㇣', 'CJK Stroke Q U+31E3' 'This only occurs in characters which are not part of KanjiVG, such as 㔔.')
        ;

    CREATE DOMAIN kanji_stroke_type AS TEXT CHECK
        (
        VALUE IN
            (
             '㇀'
            ,'㇀/㇏'
            ,'㇀/㇐'
            ,'㇀/㇑'
            ,'㇁'
            ,'㇂'
            ,'㇃'
            ,'㇄'
            ,'㇄/㇟'
            ,'㇄a'
            ,'㇅'
            ,'㇆'
            ,'㇆/㇚'
            ,'㇆a'
            ,'㇆v'
            ,'㇇'
            ,'㇇/㇆'
            ,'㇇a'
            ,'㇈'
            ,'㇈a'
            ,'㇈b'
            ,'㇉'
            ,'㇋'
            ,'㇏'
            ,'㇏/㇒'
            ,'㇏/㇔'
            ,'㇏a'
            ,'㇐'
            ,'㇐/㇑a'
            ,'㇐/㇒'
            ,'㇐/㇔'
            ,'㇐a'
            ,'㇐b'
            ,'㇐b/㇔'
            ,'㇐c'
            ,'㇐c/㇀'
            ,'㇐c/㇔'
            ,'㇑'
            ,'㇑/㇐'
            ,'㇑/㇒'
            ,'㇑/㇔'
            ,'㇑/㇙'
            ,'㇑/㇚'
            ,'㇑a'
            ,'㇑a/㇒'
            ,'㇑a/㇔'
            ,'㇒'
            ,'㇒/㇀'
            ,'㇒/㇐'
            ,'㇒/㇑'
            ,'㇒/㇔'
            ,'㇒/㇚'
            ,'㇓'
            ,'㇔'
            ,'㇔/㇀'
            ,'㇔/㇏'
            ,'㇔/㇐'
            ,'㇔/㇑'
            ,'㇔/㇑a'
            ,'㇔/㇒'
            ,'㇔/㇚'
            ,'㇔a'
            ,'㇕'
            ,'㇕/㇆'
            ,'㇕/㇑'
            ,'㇕a'
            ,'㇕a/㇆'
            ,'㇕b'
            ,'㇕b/㇆'
            ,'㇕c'
            ,'㇖'
            ,'㇖a'
            ,'㇖b'
            ,'㇖b/㇆'
            ,'㇗'
            ,'㇗/㇛'
            ,'㇗a'
            ,'㇙'
            ,'㇙/㇄'
            ,'㇙/㇏'
            ,'㇙/㇑'
            ,'㇙/㇟'
            ,'㇚'
            ,'㇚/㇑'
            ,'㇛'
            ,'㇜'
            ,'㇞'
            ,'㇟'
            ,'㇟/㇏'
            ,'㇟/㇑'
            ,'㇟a'
            ,'㇟a/㇏'
            ,'㇟b'
            ,'㇡'
            ,'一'
            ,'丶'
            ,'丿'
            ,'６'
            )
        );

    COMMENT ON DOMAIN kanji_stroke_type IS
        '
        One of:

          * A single kanji_stroke_type_primitive
          * 2 kanji_stroke_type_primitives speparated by a '/' primitive

        where each primitive might be decorated with a touch-type primitive 'a', 'b', 'c', or 'v'.
        ';

Group Position
^^^^^^^^^^^^^^

.. code:: sql

    CREATE DOMAIN group_position AS TEXT CHECK 
        (
        VALUE IN 
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
            )
        );
    COMMENT ON DOMAIN group_position IS
        '
    Defines where this groups is located with respect to the other groups with the same parent. Not every element has a "position" value. Value descriptions are in the group_position_metadata table.
        ';
    CREATE TABLE group_position_metadata 
        (
         group_position_value    group_position PRIMARY KEY
        ,help_text               TEXT NOT NULL
        );
    INSERT INTO group_position_metadata 
        (
         group_position_value
        ,help_text
        )
    VALUES
         ('bottom', 'This part is under another part.')
        ,('kamae',  'This part is wrapped around another part, such as 門. This is used very inconsistently in KanjiVG as a grab-bag for various different structures.')
        ,('left',   'This part is left of another part.')
        ,('nyo',    'This part is left and under another part, such as 辶.')
        ,('nyoc',   'This part is the complement or counterpart of a nyo part.')
        ,('right',  'This part is right of another part.')
        ,('tare',   'This part is left and above another part, such as 广.')
        ,('tarec',  'This part is the complement or counterpart of a tare part.')
        ,('top',    'This part is above another part.')
        ;

Radical Class
^^^^^^^^^^^^^

.. code:: sql

    CREATE DOMAIN radical_class AS TEXT CHECK
        (
        VALUE IN
            (
             'general'
            ,'jis'
            ,'nelson'
            ,'tradit'
            )
        );
    COMMENT ON DOMAIN radical_class IS
        '
    This is set to a value if this group of strokes is considered a radical of the kanji, and by which reference. The value of the attribute depends on the reference. Value descriptions are in the radical_class_metadata table.
        ';
    CREATE TABLE radical_class_metadata 
        (
         radical_class_value    radical_class PRIMARY KEY
        ,help_text              TEXT NOT NULL
        );
    INSERT INTO radical_class_metadata 
        (
         radical_class_value
        ,help_text
        )
    VALUES
         ('general', 'The generally accepted radical which authors agree on.')
        ,('jis', 'This marks the radicals used by JIS Kanji Jiten, used by Kanjidic, which sometimes differ from the general or tradit radicals. This value was added to deal with inconsistencies between KanjiVG and Kanjidic and other references.') 
        ,('nelson', 'The keyword "nelson" is used for Nelson radicals.')
        ,('tradit', 'The keyword "tradit" is used for the "traditional" radical, where the Kangxi radical disagrees with Nelson.')

The Kanji Drawing Table
-----------------------

.. mermaid::

    ---
    title: KanjiSVG as SQL
    config:
        layout: elk
        :zoom:
    ---
    erDiagram
        KanjiDrawing 1 to 0+ KanjiStrokeGroup : substructures
        KanjiStrokeGroup 1 to 0+ KanjiStrokeGroup : "nested substructures"
        KanjiStrokeGroup 1 to 0+ KanjiStroke: stroke
        KanjiStrokeAnnotation 1 to 1 KanjiStroke: "sequence number"


.. code:: sql

    CREATE OR REPLACE FUNCTION codepoint_hex(c TEXT)
    RETURNS char(5)
    IMMUTABLE
    LANGUAGE plpgsql AS
    $$
    DECLARE
        cp int;
    BEGIN
        cp := unicode(c);  -- Postgres 14+ provides unicode()
        RETURN lpad(to_hex(cp), 5, '0');
    END;
    $$;

    CREATE TABLE KanjiDrawing
        (
         id             CHAR(5) NOT NULL
        ,variant        kanji_variant NOT NULL DEFAULT ''
        ,xml_id         TEXT GENERATED ALWAYS AS ('kvg:' || KanjiDrawing_id || COALESCE('-' || variant, ''))
        ,element        CHAR(1) NOT NULL
        ,width          SMALLINT
        ,height         SMALLINT
        ,svg_style      TEXT
        CONSTRAINT id_matches_element_hex CHECK (id = codepoint_hex(element))
        PRIMARY KEY (id, variant)        
        );

    COMMENT ON COLUMN KanjiDrawing.id IS 
        '
    The KanjiVG identification number for this kanji drawing. It contains the Unicode code-point value of the kanji as a five-digit lower-case hexadecimal number.
    The Unicode codepoint itself is stored in the ''element'' column
        ';

    COMMENT ON COLUMN KanjiDrawing.element IS
        '
    The kanji represented by the SVG drawing.
        ';


The Kanji Stroke Group Table
-----------------------------

.. code:: sql

    CREATE TABLE KanjiStrokeGroup
        (
         KanjiDrawing_id                CHAR(5)
        ,KanjiDrawing_variant           kanji_variant NOT NULL DEFAULT ''
        ,idx                            SMALLINT NOT NULL
        ,KanjiStrokeGroup_idx_parent    SMALLINT
        ,xml_id                         TEXT GENERATED ALWAYS AS ('kvg:' || KanjiDrawing_id || COALESCE('-' || kanji_variant, '') || '-g' || ltrim(cast(idx as TEXT)))
        ,sub_element                    CHAR(1) NOT NULL

        /* number, part, and partial are not necessary in a random-access SQL world */
        ,number             SMALLINT
        ,part               SMALLINT
        ,partial            BOOLEAN NOT NULL DEFAULT false

        ,original           CHAR(1)
        ,phon               VARCHAR(3)
        ,position           group_position
        ,radical            radical_class
        ,radical_form       BOOLEAN
        ,trad_form          BOOLEAN
        ,variant            BOOLEAN

        ,CONSTRAINT notnull_number_implies_notnull_part
            CHECK(number is NULL or part is NOT NULL)
        ,CONSTRAINT partial_flags_notnull_part
            CHECK((partial and part is NOT NULL) or (not partial and part is NULL))
        ,CONTRAINT parent_is_null_or_prior
            CHECK((KanjiStrokeGroup_idx_parent is NULL) or (KanjiStrokeGroup_idx_parent < idx>))
        ,PRIMARY KEY (KanjiDrawing_id, KanjiDrawing_variant, idx)
        ,FOREIGN KEY (KanjiDrawing_id, KanjiDrawing_variant) REFERENCES KanjiDrawing(id, variant)
        );

    COMMENT ON COLUMN KanjiStrokeGroup.idx IS 
        '
        The group id number. Groups are numbered with consecutive whole numbers from 1 to the number of groups in the kanji.
        ';

    COMMENT ON COLUMN KanjiStrokeGroup.xlm_id IS 
        '
    The KanjiVG identification number for this group. It contains the Unicode value of the kanji as a five-digit lower-case hexadecimal number, followed by a hyphen and the letter "g", followed by a decimal number from one to the total number of groups.

    The group ID numbers are always consecutive positive whole numbers.
        ';

    COMMENT ON COLUMN KanjiStrokeGroup.sub_element IS
        '
    This attribute specifies which kanji best represents the group physically. It should be the Unicode character that resembles the group as much as possible.
        ';

    COMMENT ON COLUMN KanjiStrokeGroup.number IS
        '
    This relatively rare attribute allows an element of a kanji to be identified when it is both represented several times in the kanji, and, due to the stroke order, more than one of these representations is broken into parts, so that the part attribute has to be used for more than one element. In other words, the number attribute is a way to uniquely identify the part when it becomes ambiguous.

    It is only used in a few places in kanjivg where there are two different sets of the same element, such as 05716.svg, the character 圖, where there are four 口 elements, two of which are broken into parts one and two due to the stroke order. Please inspect the source code of that SVG file to understand what kvg:number attribute does.

    Generally, elements which can be represented by contiguous blocks of strokes do not have a number attribute, even if multiple cases of the same element occur in a character, so, for example, the 口 elements of 品 do not have a number attribute.
        ';

    COMMENT ON COLUMN KanjiStrokeGroup.part IS
        '
    When the elements of a group of kanji strokes which forms a larger unit are not consecutive strokes, the group of strokes may be spread over several groups of paths in the file. The part attribute allows numbering these groups and defines them as being part of the same component. There is also a number attribute which can be used in the rare cases that two groups with the same element have non-consecutive strokes within the same character.
        ';

    COMMENT ON COLUMN KanjiStrokeGroup.partial IS
        '
    Should be present and set to true if the group only represents the element attribute partially, i.e. if not all its strokes are present.
        ';

    COMMENT ON COLUMN KanjiStrokeGroup.original IS
        '
    This attribute specifies which kanji represents the group from a semantic point of view. This attribute only needs to be present if there is a difference between the semantic and physical representation of the group.

    For example, 仮 has two groups. The left one has 亻 (called ninben) for its element attribute, and 人, meaning "person", for its original attribute, because ninben is a variation of 人. However, the right side has 反 for element, which is not a variation, so an original attribute is not necessary.
        ';

    COMMENT ON COLUMN KanjiStrokeGroup.phon IS
        '
    A large number of kanji consist of a radical and a phoneticum, the Sino-Japanese pronunciation. The phon attribute should mark the part indicating the pronunciation.

    The values of this attribute are inconsistent, and the meanings of many of them are completely undocumented. See issue 312 on Github for more details.
        ';

    COMMENT ON COLUMN KanjiStrokeGroup.radical_form IS
        '
    This is set to the value true for a limited number of groups where a radical-like form of a character described by original is provided as the element.
        ';

    COMMENT ON COLUMN KanjiStrokeGroup.trad_form IS
        '
    The Kanjidic file with which Ulrich Apel worked in the beginning favored the radicals given in the Nelson character dictionary, which sometimes differ from the radicals given in "traditional" Japanese dictionaries and have mark-up as well.
        ';

    COMMENT ON COLUMN KanjiStrokeGroup.trad_form IS
        '
    Unknown, possibly used to indicate that the shape of the element is unlike the usual grapheme.
        ';

The Kanji Stroke Group Table
-----------------------------

.. code:: sql

    CREATE TABLE KanjiStroke
        (
         KanjiDrawing_id        CHAR(5)
        ,KanjiDrawing_variant   kanji_variant NOT NULL DEFAULT ''
        ,idx                    SMALLINT NOT NULL
        ,KanjiStrokeGroup_idx   SMALLINT NOT NULL
        ,xml_id                 TEXT GENERATED ALWAYS AS ('kvg:' || KanjiDrawing_id || COALESCE('-' || kanji_variant, '') || '-s' || ltrim(cast(idx as TEXT)))
        ,type                   CHAR(3) NOT NULL
        ,d                      TEXT
        ,PRIMARY KEY (KanjiDrawing_id, KanjiDrawing_variant, idx)
        ,FOREIGN KEY (KanjiDrawing_id, KanjiDrawing_variant) REFERENCES KanjiDrawing(id, variant)
        ,FOREIGN KEY (KanjiDrawing_id, KanjiDrawing_variant, KanjiStrokeGroup_idx) REFERENCES KanjiStrokeGroup(id, variant, idx)
        );

    COMMENT ON TABLE KanjiStroke IS
        '
    Each individual kanji stroke is represented by one SVG <path> element.        
        ';

    COMMENT ON COLUMN KanjiStroke.idx IS 
        '
        The stroke id number. Strokes are numbered with consecutive whole numbers from 1 to the number of strokes in the kanji.
        ';

    COMMENT ON COLUMN KanjiStroke.xlm_id IS 
        '
    The KanjiVG identification number for this stroke. It contains the Unicode value of the kanji as a five-digit lower-case hexadecimal number, followed by a hyphen and the letter "s", followed by a decimal number from one to the total number of strokes.

    The stroke ID numbers are always consecutive positive whole numbers. Numbering is unique to the drawing as a whole, _it does not restart at 1 in a new stroke group_.
        ';

    COMMENT ON COLUMN KanjiStroke.type IS
        '
    The shape of the stroke. It can be used to know how the stroke should be rendered.

    The values of this attribute use the keys of Unicode''s CJK Strokes, which occupy code positions from U+31C0 to U+31EF. The names of these, such as D or HZ, are the initials of the Chinese names.

    Please see the Stroke types page for full information on stroke types.
        ';

    COMMENT ON COLUMN KanjiStroke.d IS
        '
    The SVG path information itself. This describes the shape of the line.

    Although there is no rule disallowing various SVG elements, in practice all of the KanjiVG data consists of cubic bezier curves. In the SVG terminology the path is made up of only M/m, C/c, and S/s elements. There are no other SVG path elements present. None of the strokes contains a path with more than one sub-path, that is to say there are no strokes with more than one "moveto" element.
        ';

The Kanji Stroke Annotation Table
---------------------------------

.. code:: sql


CREATE TABLE KanjiStrokeAnnotation
    {
     KanjiDrawing_id        CHAR(5) 
    ,KanjiDrawing_variant   kanji_variant
    ,KanjiStroke_idx        SMALLINT 
    ,svg_transform          TEXT
    ,annotation             TEXT
    PRIMARY KEY (KanjiDrawing_id, KanjiDrawing_variant, idx)
    FOREIGN KEY (KanjiDrawing_id, KanjiDrawing_variant) REFERENCES KanjiDrawing(id, variant) NOT ENFORCED
    FOREIGN KEY (KanjiDrawing_id, KanjiDrawing_variant, KanjiStroke_idx) REFERENCES KanjiStroke(KanjiDrawing_id, KanjiDrawing_variant, idx)
    }

```






General attributes - from SVG
-----------------------------

d: XML

.. code:: sql
```    


id: VARCHAR(20)

.. code:: sql
COMMENT ON COLUMN Stroke.id IS
    '
The KanjiVG identification number for this stroke. It contains the prefix kvg: followed by the Unicode value of the kanji as a five-digit lower-case hexadecimal number, followed by any variant information, followed by a hyphen and the letter "s", followed by a decimal number from one to the total stroke count. For example stroke 3 of the file kanji/053ec.svg has the ID number kvg:053ec-s3.

The stroke IDs are consecutive positive whole numbers starting from 1 which correspond to the stroke number of the stroke.
    ';


KVG namespace attributes
------------------------

These attributes are under the kvg: namespace.

type: CHAR(1)

.. code:: sql
```    

Stroke numbers
==============

Stroke numbers are represented by a top-level group with an ID of the form kvg:StrokeNumbers_abcde, where abcde is the identifier of the file. This group contains text elements. Each text element is located on the diagram using a transform attribute. The text within each text element is the stroke number in digits, from one to the total number of strokes. The stroke numbers should correspond to the id value of the individual strokes.

The stroke numbers are located to the side of the beginning of the stroke whose order they indicate. Generally, they should not overlap the strokes.


