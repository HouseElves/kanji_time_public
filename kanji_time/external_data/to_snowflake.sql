use test_database.public;

CREATE FILE FORMAT IF NOT EXISTS kanjisvg_xml
TYPE = XML 
REPLACE_INVALID_CHARACTERS = TRUE
COMMENT = 'for loading kanji SVG drawing instructions' 
    ;

rEMOVE @kanjisvg_stage;    

create stage kanjisvg_stage if not exists
    ;

put
    file:///home/andrew/portfolio/kanjitime/kanji_time/external_data/kanjivg-20250816-all.zip
    @kanjisvg_stage
    ;


list @kanjisvg_stage;    

put
    file:///home/andrew/portfolio/kanjitime/kanji_time/external_data/kanjivg-20250816-all/kanji/*.svg
    @kanjisvg_stage
    ;

-- In a separate session, check current file count
SELECT COUNT(*) FROM @kanjisvg_stage;

create database kanjitime_ingest;
create schema kanjisvg;
use kanjitime_ingest.kanjisvg;

CREATE TABLE kanji_svg_files 
    (
     filename VARCHAR
    ,svg_content VARCHAR 
    );

SELECT 
     METADATA$FILENAME AS filename
    ,METADATA$
FROM @test_database.public.kanjisvg_stage
    ;

LIST @kanjisvg_stage;

set ksvg_stage = "@test_database.public.kanjisvg_stage";


COPY INTO kanji_svg_files 
    (
     filename
    ,svg_content
    )
FROM 
    (
    SELECT 
         METADATA$FILENAME AS filename
        ,$1 AS svg_content
    FROM @test_database.public.kanjisvg_stage
    )
FILE_FORMAT = test_database.public.kanjisvg_xml
    ;

/*
BEWARE:  session variables can get into a view!  Consider a "constants" table.
 */
use kanjitime_ingest.kanjisvg;
set filename_component_delim = '.';
set kanji_variant_delim = '-';

select top 2 
     SPLIT(filename, $filename_component_delim) as name_ext
    ,name_ext[0] as basename
    ,POSITION($kanji_variant_delim in basename) as codepoint_variant_splitpoint
    ,TRIM(CASE WHEN codepoint_variant_splitpoint > 0 THEN LEFT(basename, codepoint_variant_splitpoint - 1) ELSE basename END) as codepoint_str
    ,REPEAT('x', len(codepoint_str)) as convert_mask    -- !!! use the max file length to avoid repeating calculatins
    ,to_number(codepoint_str, convert_mask) as codepoint  
    ,CHR(codepoint) as glyph
    ,TRIM(CASE WHEN codepoint_variant_splitpoint > 0 THEN SUBSTRING(basename, codepoint_variant_splitpoint + 1) END) as kvg_variant
    ,parse_xml(svg_content) as KanjiVG
from kanji_svg_files
    ;

create or replace view kvg_upload as
with intake 
as 
    (
    select
         SPLIT(filename, $filename_component_delim)                         as name_ext
        ,name_ext[0]                                                        as basename
        ,POSITION($kanji_variant_delim in basename)                         as codepoint_variant_splitpoint
        ,TRIM(
            CASE 
                WHEN codepoint_variant_splitpoint > 0 
                THEN LEFT(basename, codepoint_variant_splitpoint - 1) 
                ELSE basename 
            END)                                                            as codepoint_str
        ,REPEAT('x', len(codepoint_str))                                    as convert_mask    -- !!! use the max file length to avoid repeating calculatins
        ,to_number(codepoint_str, convert_mask)                             as codepoint  
        ,CHR(codepoint)                                                     as glyph
        ,TRIM(
            CASE 
                WHEN codepoint_variant_splitpoint > 0 
                THEN SUBSTRING(basename, codepoint_variant_splitpoint + 1) 
            END)                                                            as kvg_variant_name
        ,parse_xml(svg_content)                                             as kvg
        ,svg_content
    from kanji_svg_files
    )
select top 20
     codepoint_str
    ,codepoint
    ,kvg_variant_name
    ,kvg
from intake
    ;


ALTER VIEW kvg_upload
MODIFY COLUMN kvg_variant_name
    COMMENT 'SUBTYPE: kanji_variant (see table kanji_variant_metadata); DESCRIPTION: Classification of the stroking variant of this kanji character.'
    ;


/* 
as a flattened pair

    '@' is the tag name
    '$' is the tag content -> text, nested tags

 */

select 
     kvg
    ,object_keys(kvg)
    ,xmlget(kvg, )
from kvg_upload
    ;
    
select 
     kvg
    ,kvg['@']           as root_tag
    ,kvg['$']           as content
    ,kvg['@height']     as height
    ,kvg['@width']      as width
    ,kvg['@viewbox']    as viewbox
    ,object_keys(kvg)
from kvg_upload
    ;    

<svg height="109" viewBox="0 0 109 109" width="109" xmlns="http://www.w3.org/2000/svg">
  <g id="kvg:StrokePaths_0796d" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">
    <g id="kvg:0796d" kvg:element="祭">
      <g id="kvg:0796d-g1" kvg:position="top">
        <g id="kvg:0796d-g2" kvg:element="月" kvg:variant="true">
          <path d="M30.5,14.5c0.37,1.58-0.01,3.14-0.74,4.46c-2.04,3.7-6.64,10.42-13.01,15.54" id="kvg:0796d-s1" kvg:type="㇒"></path>
          <path d="M33.75,18.5c1.12,0.25,2.75-0.09,4.26-0.42c3.23-0.71,7.02-1.99,9.24-2.33c3.25-0.5,4.39,0.83,3.5,3.25c-4,10.88-17,28.25-34.5,37.25" id="kvg:0796d-s2" kvg:type="㇇"></path>
          <path d="M29.25,27.12c1.18,0.47,5.89,3.3,8.25,6.12" id="kvg:0796d-s3" kvg:type="㇔"></path>
          <path d="M20.62,35.5c1.78,1.03,7.14,5.42,8.62,7.75" id="kvg:0796d-s4" kvg:type="㇔"></path>
        </g>
        <path d="M58.75,19.25c2,0.75,3.44,0.74,5,0.5c3.25-0.5,8.75-1.62,13.5-3c3.66-1.06,4.93,0.96,3.5,3.75C78.5,24.88,72.5,33,66.5,37.5" id="kvg:0796d-s5" kvg:type="㇇"></path>
        <path d="M54.75,28.75c5,0,25.95,16.58,28.25,18c3.25,2,7.75,4.5,11,5.25" id="kvg:0796d-s6" kvg:type="㇏"></path>
      </g>
      <g id="kvg:0796d-g3" kvg:element="示" kvg:position="bottom" kvg:radical="general">
        <path d="M38.35,52.08c1.13,0.3,3.21,0.38,4.34,0.3c7.06-0.51,16.31-1.88,22.39-2.06c1.89-0.06,3.02,0.14,3.97,0.29" id="kvg:0796d-s7" kvg:type="㇐"></path>
        <path d="M22.46,66.99c2.16,0.43,6.14,0.87,8.3,0.68c16.24-1.42,31.86-2.54,47.63-2.88c3.6-0.08,5.38,0.21,7.57,0.67" id="kvg:0796d-s8" kvg:type="㇐"></path>
        <path d="M53.08,68.74c1.15,1.15,1.58,2.76,1.58,4.73c0,4.03,0.03,12.88,0.03,17.13c0,9.4-6.29,1.2-7.47,0.21" id="kvg:0796d-s9" kvg:type="㇑"></path>
        <path d="M35.7,76.51c0.15,0.98-0.02,1.88-0.52,2.71c-2.67,4.03-9.92,10.28-18.1,14.72" id="kvg:0796d-s10" kvg:type="㇒"></path>
        <path d="M69.88,75.96c5.22,2.58,12.87,9.66,15.05,14.34" id="kvg:0796d-s11" kvg:type="㇔"></path>
      </g>
    </g>
  </g>
  <g id="kvg:StrokeNumbers_0796d" style="font-size:8;fill:#808080">
    <text transform="matrix(1 0 0 1 21.75 16.63)">1</text>
    <text transform="matrix(1 0 0 1 36.75 15.13)">2</text>
    <text transform="matrix(1 0 0 1 36.75 28.63)">3</text>
    <text transform="matrix(1 0 0 1 26.25 36.13)">4</text>
    <text transform="matrix(1 0 0 1 62.25 15.13)">5</text>
    <text transform="matrix(1 0 0 1 62.25 30.13)">6</text>
    <text transform="matrix(1 0 0 1 42.75 48.13)">7</text>
    <text transform="matrix(1 0 0 1 14.25 69.13)">8</text>
    <text transform="matrix(1 0 0 1 45.75 76.63)">9</text>
    <text transform="matrix(1 0 0 1 20.25 79.63)">10</text>
    <text transform="matrix(1 0 0 1 72.75 76.69)">11</text>
  </g>
</svg>    



  SELECT PARSE_XML('<c>3.1</c>'::variant) ;
  
  
  FROM VALUES
    ('<c>3.1</c>'),
    ('<e>2</e>'),
    ('<b>0.123</b>')
    ;


-- Let's start with a drawing table
--

-- do domains work?
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
-- Houston, that's a hard "no"
-- at least there is metadata

DROP TABLE kanji_variant_metadata;
CREATE TABLE kanji_variant_metadata 
    (
     kanji_variant_value     VARCHAR PRIMARY KEY  
                             COMMENT 'SUBTYPE: kanji_variant; DESCRIPTION: Classification of the stroking variant of this kanji character.'
    ,help_text               TEXT NOT NULL
                             COMMENT 'SUBTYPE: html_help_text; DESCRIPTION: Details about this stroking variant classification.'
    )
COMMENT = 'KanjiVG includes data on variations of characters and stroke order. For example, when characters in the schoolbook style deviate from traditional kaisho, there might be an extra file containing the kaisho version of the character. This file is named using the same Unicode value as the schoolbook style kanji, with the suffix -Kaisho. For example the kaisho variant of 島, 05cf6.svg is named 05cfa-Kaisho.svg. There are also different versions for different stroke orders.'
    ;
    
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

/* First attempt 
ALTER TABLE kanji_variant_metadata 
SET
    COMMENT = 'KanjiVG includes data on variations of characters and stroke order. For example, when characters in the schoolbook style deviate from traditional kaisho, there might be an extra file containing the kaisho version of the character. This file is named using the same Unicode value as the schoolbook style kanji, with the suffix -Kaisho. For example the kaisho variant of 島, 05cf6.svg is named 05cfa-Kaisho.svg. There are also different versions for different stroke orders.'
    ;
ALTER TABLE kanji_variant_metadata 
MODIFY COLUMN kanji_variant_value
    COMMENT 'SUBTYPE: kanji_variant (see table kanji_variant_metadata); DESCRIPTION: Classification of the stroking variant of this kanji character.'
    ;
*/

DROP TABLE IF EXISTS kanji_stroke_primitive_metadata;
CREATE TABLE kanji_stroke_primitive_metadata 
    (
     kanji_stroke_primitive_value   VARCHAR PRIMARY KEY
                                    COMMENT 'SUBTYPE: kanji_stroke_primitive; DESCRIPTION: Classification of the shape of a kanji character stroke in the Unicode CJK Strokes block.'
    ,cjk_stroke                     TEXT NOT NULL
                                    COMMENT 'SUBTYPE: codepoint_name; DESCRIPTION: The representation of the kanji stroke shape as a Unicode codepoint.'
    ,help_text                      TEXT NOT NULL
                                    COMMENT 'SUBTYPE: html_help_text; DESCRIPTION: Details about the usage of this stroke primitive.'
    )
COMMENT = 'The type attribute of a stroke specifies its shape. It can be used to know how the stroke should be rendered.<P/>The values of this attribute use the keys of Unicode''s CJK Strokes.<P/>The best documentation available on the meanings of these stroke types seems to be that found in Proposed additions to the CJK Strokes block of the UCS, and the explanation of the stroke types there mostly consists of a list of examples, so there is some remaining ambiguity about how best to use these.<P/>In some cases these stroke types, in particular ㇁ (U+31C1), or ㇔ (U+31D4), may appear to be in error, but check the explanations below before suggesting changes.<P/>In other cases another field consisting of alphabetical letters. These letters refer to a set of stroke types which Ulrich Apel designed but has not documented. The letters seem to indicate the intersections of the ends of strokes with other strokes. See issue 324 on Github for more details.'
    ;

INSERT INTO kanji_stroke_primitive_metadata 
    (
     kanji_stroke_primitive_value
    ,cjk_stroke
    ,help_text
    )
VALUES  
     ('㇀', 'CJK Stroke T U+31C0', 'This stroke is the lower left one in 冰 and 氾. It always goes from left to right and upwards. See ㇒ (CJK Stroke P) for a similar-looking stroke which goes in the opposite direction.')
    ,('㇁', 'CJK Stroke WG U+31C1', 'This is used for the down stroke of 犭 and the lower right part of ⻖. Some fonts, including the default font used by KanjiVG''s host, github.com, represent this shape as being almost identical to ㇓ (CJK Stroke SP), so it may appear to be an error on a browser screen. However, this is the correct shape for 犭 and ⻖.')
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
    ,('/', '', 'Where the value has two possibilities, a slash is used to separate them. For example, the bottom dash in 冬 (fuyu, ''winter'') may slant either upwards or downwards, so this is represented by kvg:type=''㇔/㇀'' in the KanjiVG source file.')
    ,('㇌', 'CJK Stroke HPWG U+31CC', 'This stroke pattern is used to represent the right side of ⻖ and related shapes when it is written as two strokes, per the Chinese convention. KanjiVG always uses three strokes to write ⻖, with the right side broken into upper and lower pieces, so this pattern is not used by KanjiVG.')
    ,('㇊', 'CJK Stroke HZT', 'U+31CA The main use of this seems to be to represent the 言 component known as gonben in simplified Chinese characters like 计, or other simplified Chinese forms such as so it is not very useful for Japanese.' )
    ,('㇎', 'CJK Stroke HZZZ U+31CE', 'This rare pattern seems to only be used in the Chinese drawing of 凸. Japanese uses a different stroke pattern for this character.')
    ,('㇣', 'CJK Stroke Q U+31E3', 'This only occurs in characters which are not part of KanjiVG, such as 㔔.')
    ;

DROP TABLE IF EXISTS kanji_stroke_type_metadata;
CREATE TABLE kanji_stroke_type_metadata 
    -- TODO (downstream):  add some images / SVG drawings to this table for examples of these stoke types w/ connecting strokes
    (
     kanji_stroke_type_value   VARCHAR PRIMARY KEY
                               COMMENT 'SUBTYPE: kanji_stroke_type = kanji_stroke_primitive{1,4}; DESCRIPTION: Encoding of a stroke shape and (possibly) how it touches an adjacent stroke.'
    ,help_text                 TEXT NOT NULL
                               COMMENT 'SUBTYPE: html_help_text; DESCRIPTION: !!! EMPTY COLUMN:  TODO !!!.'
    )
COMMENT = 'A complete description of the shape of a stroke. It consists of up to two <b>kanji_stroke_primitive</b> values separated by a ''/'' primitive, where each primitive might be decorated with a touch-type <b>kanji_stroke_primitive</b> value ''a'', ''b'', ''c'', or ''v''.'
    ;
INSERT INTO kanji_stroke_type_metadata
VALUES
     ('㇀', '')
    ,('㇀/㇏', '')
    ,('㇀/㇐', '')
    ,('㇀/㇑', '')
    ,('㇁', '')
    ,('㇂', '')
    ,('㇃', '')
    ,('㇄', '')
    ,('㇄/㇟', '')
    ,('㇄a', '')
    ,('㇅', '')
    ,('㇆', '')
    ,('㇆/㇚', '')
    ,('㇆a', '')
    ,('㇆v', '')
    ,('㇇', '')
    ,('㇇/㇆', '')
    ,('㇇a', '')
    ,('㇈', '')
    ,('㇈a', '')
    ,('㇈b', '')
    ,('㇉', '')
    ,('㇋', '')
    ,('㇏', '')
    ,('㇏/㇒', '')
    ,('㇏/㇔', '')
    ,('㇏a', '')
    ,('㇐', '')
    ,('㇐/㇑a', '')
    ,('㇐/㇒', '')
    ,('㇐/㇔', '')
    ,('㇐a', '')
    ,('㇐b', '')
    ,('㇐b/㇔', '')
    ,('㇐c', '')
    ,('㇐c/㇀', '')
    ,('㇐c/㇔', '')
    ,('㇑', '')
    ,('㇑/㇐', '')
    ,('㇑/㇒', '')
    ,('㇑/㇔', '')
    ,('㇑/㇙', '')
    ,('㇑/㇚', '')
    ,('㇑a', '')
    ,('㇑a/㇒', '')
    ,('㇑a/㇔', '')
    ,('㇒', '')
    ,('㇒/㇀', '')
    ,('㇒/㇐', '')
    ,('㇒/㇑', '')
    ,('㇒/㇔', '')
    ,('㇒/㇚', '')
    ,('㇓', '')
    ,('㇔', '')
    ,('㇔/㇀', '')
    ,('㇔/㇏', '')
    ,('㇔/㇐', '')
    ,('㇔/㇑', '')
    ,('㇔/㇑a', '')
    ,('㇔/㇒', '')
    ,('㇔/㇚', '')
    ,('㇔a', '')
    ,('㇕', '')
    ,('㇕/㇆', '')
    ,('㇕/㇑', '')
    ,('㇕a', '')
    ,('㇕a/㇆', '')
    ,('㇕b', '')
    ,('㇕b/㇆', '')
    ,('㇕c', '')
    ,('㇖', '')
    ,('㇖a', '')
    ,('㇖b', '')
    ,('㇖b/㇆', '')
    ,('㇗', '')
    ,('㇗/㇛', '')
    ,('㇗a', '')
    ,('㇙', '')
    ,('㇙/㇄', '')
    ,('㇙/㇏', '')
    ,('㇙/㇑', '')
    ,('㇙/㇟', '')
    ,('㇚', '')
    ,('㇚/㇑', '')
    ,('㇛', '')
    ,('㇜', '')
    ,('㇞', '')
    ,('㇟', '')
    ,('㇟/㇏', '')
    ,('㇟/㇑', '')
    ,('㇟a', '')
    ,('㇟a/㇏', '')
    ,('㇟b', '')
    ,('㇡', '')
    ,('一', '')
    ,('丶', '')
    ,('丿', '')
    ,('６', '')
    ;

DROP TABLE IF EXISTS kanji_stroke_group_position_metadata;
CREATE TABLE kanji_stroke_group_position_metadata 
    (
     kanji_stroke_group_position_value   VARCHAR PRIMARY KEY
                               COMMENT 'SUBTYPE: kanji_stroke_group_position; DESCRIPTION: Unique name for the location of a group of strokes within a kanji.'
    ,help_text                 TEXT NOT NULL
                               COMMENT 'SUBTYPE: html_help_text; DESCRIPTION: A qualative description of this group location relative of other stroke groups within a kanji.'
    )
COMMENT = 'Defines where this groups is located with respect to the other groups with the same parent. Not every element has a ''position'' value.'
    ;
INSERT INTO kanji_stroke_group_position_metadata
    (
     kanji_stroke_group_position_value
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


DROP TABLE IF EXISTS kanji_radical_class_metadata;
CREATE TABLE kanji_radical_class_metadata 
    (
     kanji_radical_class_value VARCHAR PRIMARY KEY
                               COMMENT 'SUBTYPE: kanji_radical_class; DESCRIPTION: Name of the lexicon contaning the kanji radical represented in a stroke group.'
    ,help_text                 TEXT NOT NULL
                               COMMENT 'SUBTYPE: html_help_text; DESCRIPTION: A brief description of the usage and variances of this kanji radical lexicon.'
    )
COMMENT = 'This is set to a value if this group of strokes is considered a radical of the kanji, and by which reference. The value of the attribute depends on the reference.'
    ;
INSERT INTO kanji_radical_class_metadata 
    (
     kanji_radical_class_value
    ,help_text
    )
VALUES
     ('general', 'The generally accepted radical which authors agree on.')
    ,('jis', 'This marks the radicals used by JIS Kanji Jiten, used by Kanjidic, which sometimes differ from the general or tradit radicals. This value was added to deal with inconsistencies between KanjiVG and Kanjidic and other references.') 
    ,('nelson', 'The keyword ''nelson'' is used for Nelson radicals.')
    ,('tradit', 'The keyword ''tradit'' is used for the ''traditional'' radical, where the Kangxi radical disagrees with Nelson.')
    ;


CREATE OR REPLACE FUNCTION encode_kanji(c TEXT)
    RETURNS char(5)
    IMMUTABLE
AS
$$
BEGIN
    RETURN to_varchar(unicode(c), '0000x');
END;
$$
    ;

-- Sanity check  for codepoint_hex
select 'A' as val, unicode(val) as cp, to_varchar(cp, '0000x') as enc, encode_kanji(val), encode_kanji('㇏');

CREATE OR REPLACE FUNCTION decode_kanji(c TEXT)
    RETURNS char(5)
    IMMUTABLE
AS
$$
BEGIN
    RETURN chr(to_number(c, 'xxxxx'));
END;
$$
    ;

select
     encode_kanji(val) as encoded
    ,decode_kanji(encoded) as decoded
from 
    (
    select 'A' as val
    union
    select '㇏' as val
    )
    ;


-- some functions to simplify group and path id decoding

--"kvg:05cfa-Kaisho-g1"

WITH ids AS (
  SELECT 'kvg:05cfa-Kaisho-g1' as id
  UNION ALL
  SELECT '05cfa-Kaisho-g1'
  UNION ALL  
  SELECT 'kvg:1a2b3-s42'
)
SELECT
   id
   -- Validation
  ,REGEXP_LIKE(id, '^(kvg:)?[0-9a-f]{5}(-[A-Za-z]{3,})?-[gs][0-9]+$') as is_valid
  ,REGEXP_SUBSTR(id, '^([A-Za-z]+):', 1, 1, 'e') as ns_prefix
  ,REGEXP_SUBSTR(id, '([0-9a-f]{5})', 1, 1, 'e') as hex_code
  ,decode_kanji(hex_code) as kanji
  ,REGEXP_SUBSTR(id, '-([A-Za-z]{3,})-', 1, 1, 'e') as kanji_variant
  ,REGEXP_SUBSTR(id, '([gs])([0-9]+)$', 1, 1, 'e', 1) as stroke_or_group
  ,case when stroke_or_group = 'g' then 1 else 0 end as is_group
  ,case when stroke_or_group = 's' then 1 else 0 end as is_stroke
  ,REGEXP_SUBSTR(id, '([gs])([0-9]+)$', 1, 1, 'e', 2) as seq_number
FROM ids
    ;

WITH ids AS (
  SELECT 'kvg:05cfa-Kaisho-g1' as id
  UNION ALL
  SELECT '05cfa-Kaisho-g1'
  UNION ALL  
  SELECT 'kvg:1a2b3-s42'
)
SELECT OBJECT_CONSTRUCT(
    'ns_prefix', REGEXP_SUBSTR(id, '^([A-Za-z]+):', 1, 1, 'e')
    ,'hex_code', REGEXP_SUBSTR(id, '([0-9a-f]{5})', 1, 1, 'e')
    ,'kanji_variant', REGEXP_SUBSTR(id, '-([A-Za-z]{3,})-', 1, 1, 'e')
    ,'stroke_or_group', REGEXP_SUBSTR(id, '([gs])([0-9]+)$', 1, 1, 'e', 1)
    ,'seq_number', REGEXP_SUBSTR(id, '([gs])([0-9]+)$', 1, 1, 'e', 2)
    ) as decoded
from ids
    ;


CREATE OR REPLACE FUNCTION decode_id(id VARCHAR)
RETURNS OBJECT
AS
$$
OBJECT_CONSTRUCT(
     'ns_prefix', REGEXP_SUBSTR(id, '^([A-Za-z]+):(Stroke(Numbers|Paths)_)?', 1, 1, 'e', 1)
    ,'block_name', REGEXP_SUBSTR(id, '^([A-Za-z]+):(Stroke(Numbers|Paths)_)?', 1, 1, 'e', 3)
    ,'hex_code', REGEXP_SUBSTR(id, '([0-9a-f]{5})', 1, 1, 'e')
    ,'kanji_variant', REGEXP_SUBSTR(id, '-([A-Za-z]{3,})-?', 1, 1, 'e')
    ,'stroke_or_group', REGEXP_SUBSTR(id, '([gs])([0-9]+)?$', 1, 1, 'e', 1)
    ,'seq_number', REGEXP_SUBSTR(id, '([gs])([0-9]+)?$', 1, 1, 'e', 2)
    )
$$;

WITH ids AS (
  SELECT 'kvg:05cfa-Kaisho-g1' as id
  UNION ALL
  SELECT '05cfa-Kaisho-g1'
  union all
  select 'kvg:StrokeNumbers_0796d'
  UNION ALL  
  SELECT 'kvg:1a2b3-s42'
  union all
  select 'kvg:StrokePaths_05cfa-Kaisho'
)
select decode_id(id) as decoded
FROM ids
    ;


select 
     kvg
    ,kvg['@']           as root_tag
    ,kvg['$']           as content
    ,object_keys(content[0]) as first_tag_keys
    ,content[0]['@'] as first_tag_name
    ,content[0]['@id'] as first_tag_id
    ,content[0]['$'] as first_tag_content
    ,decode_id(first_tag_id) as decoded.group_id_0
    ,content[1]['@'] as second_tag_name
    ,content[1]['@id'] as second_tag_id
    ,content[1]['$'] as second_tag_content
    ,decode_id(second_tag_id) as decoded.group_id_1
    ,case 
        when decoded.group_id_0:block_name = 'Paths' then first_tag_content
        when decoded.group_id_1:block_name = 'Paths' then second_tag_content
        else 'bleh'
     end as PathBlock
    --,case 
    --    when decoded.group_id_0:blockname = 'Numbers' then content[0]['$']
    --    when decoded.group_id_1:blockname = 'Numbers' then content[1]['$']
    -- end as LabelBlock
    ,kvg['@height']     as height
    ,kvg['@width']      as width
    ,kvg['@viewbox']    as viewbox
    ,object_keys(kvg)
from kvg_upload
    ;  

select
     codepoint_str                  as encoded_kanji
    ,decode_kanji(codepoint_str)    as kanji
    ,kvg_variant_name               as kanji_variant
    ,kvg['@']                       as root_tag
    ,kvg['@height']                 as height
    ,kvg['@width']                  as width
    ,coalesce(
        -- alternate spellings
         kvg['@viewBox']
        ,kvg['@viewbox']
        )                           as viewbox
    ,kvg['$']                       as children
    ,kvg['$'][x.index]                       as content
    ,decode_id(x.value['@id']) as id
    ,id:block_name as block_name
    ,decode_id(x.value['@id']):hex_code as hex_code  -- I can dereference a computed value directly
    ,x.value as kvg_block
    ,x.*
 from kvg_upload
 cross join lateral flatten(kvg['$']) as x
 where kvg['@'] = 'svg'
    ;

select * from kanji_drawing_extractor;
select * from kanji_paths_extractor;

select * from root_group_extractor;


create or replace view kanji_drawing_extractor
as
select
     codepoint_str                  as encoded_kanji
    ,decode_kanji(encoded_kanji)    as kanji
    ,kvg_variant_name               as kanji_variant
    ,kvg['@']                       as root_tag
    ,kvg['@height']                 as height
    ,kvg['@width']                  as width
    ,kvg['@xmlns']                  as dflt_namespace
    ,coalesce(
        -- alternate spellings
         kvg['@viewBox']
        ,kvg['@viewbox']
        )                           as viewbox
    ,kvg['$']                       as children
from kvg_upload
where kvg['@'] = 'svg'
    ;


create or replace view kanji_paths_extractor
as
select
     decoded.group_id:hex_code                  as encoded_kanji
    ,decoded.group_id:kanji_variant             as kanji_variant
    ,decode_kanji(decoded.group_id:hex_code)    as kanji
    ,d.children[x.index]                        as paths_header
    ,x.value['@style']                          as svg_style
    ,paths_header['@']                          as paths_tag
    ,paths_header['$']                          as stroke_groups
from kanji_drawing_extractor as d
cross join lateral flatten(d.children) as x
cross join lateral 
    (
    SELECT decode_id(x.value['@id']) AS group_id
    ) decoded
where decoded.group_id:block_name = 'Paths' --'Numbers'
    ;



create or replace view root_group_extractor
as
select
     p.stroke_groups['@id']                         as node_id
    ,p.stroke_groups['@']                           as node_tag
    ,p.stroke_groups['$']                           as children
from kanji_paths_extractor p
    ;


-- fixed column name collision w/ alias by decoding into a cross-lateral. 

-- basis case
--
select 
     decoded.group_id:hex_code                  as encoded_kanji
    ,decoded.group_id:kanji_variant             as kanji_variant
    ,decode_kanji(decoded.group_id:hex_code)    as kanji
    ,r.stroke_group_id                          as parent_group_id
    ,decoded.group_id:seq_number                as stroke_or_group_id
    ,decoded.group_id:stroke_or_group           as stroke_or_group
    ,x.value['@kvg:element']                    as kanji_element
    ,x.value['@kvg:position']                   as position
    ,x.value['@']                               as child_tag
    ,x.value['$']                               as child_groups
    ;

create table StrokePath as
    (
    select 
         seq as xml_id
        ,r.node_id              as svg_paths_id
        ,x.value['@id']         as node_id
        ,x.value['@']           as node_tag
        ,x.path                 as node_address
        ,coalesce(
             '[''$'']['||x.index||']'
            ,'['''||x.key||''']'
            )                   as final_address_component
        -- length(final_address_component) is overstated at the first-level child, but that's OK because its parent is the SVG Paths node.
        ,left(
             x.path
            ,length(x.path) - length(final_address_component)
            )                   as parent_node_address
    from root_group_extractor r
    cross join lateral flatten(r.children, recursive=>true) as x
    where x.value['@id'] is not NULL
    order by svg_paths_id, parent_node_address
    )
    ;

/*
-- Convenient model for applying a function 
cross join lateral 
    (
    SELECT decode_id(x.value['@id']) AS group_id
    ) as decoded
 ;

 */



WITH RECURSIVE stroke_group_tree 
AS 
    (
    -- BASIS: children of the root stroke group
    select 
         REGEXP_SUBSTR(x.value['@id'], '([0-9a-f]{5})', 1, 1, 'e')          as encoded_kanji
        ,REGEXP_SUBSTR(x.value['@id'], '-([A-Za-z]{3,})-', 1, 1, 'e')       as kanji_variant
        ,r.stroke_group_id                                                  as parent_group_id
        ,REGEXP_SUBSTR(x.value['@id'], '([gs])([0-9]+)$', 1, 1, 'e', 2)     as stroke_or_group_id
        ,REGEXP_SUBSTR(x.value['@id'], '([gs])([0-9]+)$', 1, 1, 'e', 1)     as stroke_or_group
        --
        ,x.value['@kvg:element']            as kanji_element
        ,x.value['@kvg:position']           as position
        ,x.value['@']                       as child_tag
        ,x.value['$']                       as child_groups
    from root_group_extractor r
    cross join lateral flatten(r.child_groups) as x
    where x.value['@'] = 'g'

    UNION ALL

    -- TAIL LOOP: children of groups found so far
    select
         REGEXP_SUBSTR(x.value['@id'], '([0-9a-f]{5})', 1, 1, 'e')          as encoded_kanji
        ,REGEXP_SUBSTR(x.value['@id'], '-([A-Za-z]{3,})-', 1, 1, 'e')       as kanji_variant
        ,t.stroke_or_group_id                                               as parent_group_id
        ,REGEXP_SUBSTR(x.value['@id'], '([gs])([0-9]+)$', 1, 1, 'e', 2)     as stroke_or_group_id
        ,REGEXP_SUBSTR(x.value['@id'], '([gs])([0-9]+)$', 1, 1, 'e', 1)     as stroke_or_group
        --
        ,x.value['@kvg:element']                    as kanji_element
        ,x.value['@kvg:position']                   as position
        ,x.value['@']                               as child_tag
        ,x.value['$']                               as child_groups
    from stroke_group_tree t
    cross join lateral flatten(t.child_groups) as x
    WHERE x.value['@'] = 'g' AND t.stroke_or_group_id IS NOT NULL
    -- cheap guard; you can set 10 or 20
    -- AND t.depth < 10
    )
select 
    * 
from stroke_group_tree
    ;
    ----> yeah, but no!
    /*
    SQL compilation error: error line 35 at position 23
    A self reference of CTE 'STROKE_GROUP_TREE' cannot be used as an argument to a UDTF
     */

CREATE OR REPLACE FUNCTION flatten_child_groups(child_groups VARIANT)
RETURNS TABLE (value VARIANT)
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
HANDLER = 'FlattenHandler'
AS
$$
class FlattenHandler:
    def process(self, child_groups):
        if child_groups and isinstance(child_groups, list):
            for item in child_groups:
                yield (item,)
$$; 


WITH RECURSIVE stroke_group_tree 
AS 
    (
    -- BASIS: children of the root stroke group
    select 
         x.value['@id']                     as id_attr
        ,NULL                               as parent_id_attr
        --
        ,x.value['@kvg:element']            as kanji_element
        ,x.value['@kvg:position']           as position
        ,x.value['@']                       as child_tag
        ,x.value['$']                       as child_groups
        ,1                                  as depth
    from root_group_extractor r
    CROSS JOIN TABLE(flatten_child_groups(r.child_groups)) AS x
    where x.value['@'] in ('path', 'g')

    UNION ALL

    -- TAIL LOOP: children of groups found so far
    select 
         x.value['@id']                     as id_attr
        ,s.id_attr                          as parent_id_attr
        --
        ,x.value['@kvg:element']            as kanji_element
        ,x.value['@kvg:position']           as position
        ,x.value['@']                       as child_tag
        ,x.value['$']                       as child_groups
        ,s.depth + 1                        as depth
    from stroke_group_tree s
    CROSS JOIN TABLE(flatten_child_groups(s.child_groups)) AS x
    where   s.child_tag = 'g'
        -- cheap guard
        AND s.depth < 10
    )
select 
    * 
from stroke_group_tree

    ;



    -- BASIS: children of the root stroke group
    select 
         x.value['@id']                     as id_attr
       , NULL                               as parent_id_attr
        --
        ,x.value['@kvg:element']            as kanji_element
        ,x.value['@kvg:position']           as position
        ,x.value['@']                       as child_tag
        ,x.value['$']                       as child_groups
    from root_group_extractor r
    CROSS JOIN TABLE(flatten_child_groups(r.child_groups)) AS x
    where x.value['@'] in ('path', 'g')
    ;

    select 
         x.value['@id']                     as id_attr
        --
        ,x.value['@kvg:element']            as kanji_element
        ,x.value['@kvg:position']           as position
        ,x.value['@']                       as child_tag
        ,x.value['$']                       as child_groups
    from root_group_extractor r
    cross join lateral flatten(r.child_groups) as x
    where r.value['@'] = 'g'    -- test the parent tag --> allows in 'path' tags at the leaves.
        ;






/*
XML_ID	SVG_PATHS_ID	NODE_ID	NODE_TAG	NODE_ADDRESS	FINAL_ADDRESS_COMPONENT	PARENT_NODE_ADDRESS
1	kvg:0796d	kvg:0796d-g3	g	[1]	['$'][1]	
1	kvg:0796d	kvg:0796d-g1	g	[0]	['$'][0]	
1	kvg:0796d	kvg:0796d-g2	g	[0]['$'][0]	['$'][0]	[0]
1	kvg:0796d	kvg:0796d-s5	path	[0]['$'][1]	['$'][1]	[0]
1	kvg:0796d	kvg:0796d-s6	path	[0]['$'][2]	['$'][2]	[0]
1	kvg:0796d	kvg:0796d-s1	path	[0]['$'][0]['$'][0]	['$'][0]	[0]['$'][0]
1	kvg:0796d	kvg:0796d-s2	path	[0]['$'][0]['$'][1]	['$'][1]	[0]['$'][0]
1	kvg:0796d	kvg:0796d-s3	path	[0]['$'][0]['$'][2]	['$'][2]	[0]['$'][0]
1	kvg:0796d	kvg:0796d-s4	path	[0]['$'][0]['$'][3]	['$'][3]	[0]['$'][0]
1	kvg:0796d	kvg:0796d-s7	path	[1]['$'][0]	['$'][0]	[1]
1	kvg:0796d	kvg:0796d-s11	path	[1]['$'][4]	['$'][4]	[1]
1	kvg:0796d	kvg:0796d-s10	path	[1]['$'][3]	['$'][3]	[1]
1	kvg:0796d	kvg:0796d-s9	path	[1]['$'][2]	['$'][2]	[1]
1	kvg:0796d	kvg:0796d-s8	path	[1]['$'][1]	['$'][1]	[1]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-g1	g	[0]	['$'][0]	
2	kvg:0798d-HzFst	kvg:0798d-HzFst-g2	g	[1]	['$'][1]	
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s1	path	[0]['$'][0]	['$'][0]	[0]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s4	path	[0]['$'][3]	['$'][3]	[0]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s3	path	[0]['$'][2]	['$'][2]	[0]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s2	path	[0]['$'][1]	['$'][1]	[0]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s5	path	[1]['$'][0]	['$'][0]	[1]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s6	path	[1]['$'][1]	['$'][1]	[1]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s7	path	[1]['$'][2]	['$'][2]	[1]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s8	path	[1]['$'][3]	['$'][3]	[1]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-g3	g	[1]['$'][4]	['$'][4]	[1]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-g4	g	[1]['$'][5]	['$'][5]	[1]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s9	path	[1]['$'][4]['$'][0]	['$'][0]	[1]['$'][4]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s10	path	[1]['$'][4]['$'][1]	['$'][1]	[1]['$'][4]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s11	path	[1]['$'][5]['$'][0]	['$'][0]	[1]['$'][5]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s12	path	[1]['$'][5]['$'][1]	['$'][1]	[1]['$'][5]
2	kvg:0798d-HzFst	kvg:0798d-HzFst-s13	path	[1]['$'][5]['$'][2]	['$'][2]	[1]['$'][5]
*/

CREATE OR REPLACE FUNCTION group_attributes(
    stroke_group OBJECT
    )
RETURNS OBJECT
AS
$$
OBJECT_CONSTRUCT(
    'element', stroke_group['@kvg:element'],
    'number', stroke_group['@kvg:number'],
    'original', stroke_group['@kvg:original'],
    'part', stroke_group['@kvg:part'],
    'partial', stroke_group['@kvg:partial'],
    'phon', stroke_group['@kvg:phon'],
    'position', stroke_group['@kvg:position'],
    'radical', stroke_group['@kvg:radical'],
    'radicalForm', stroke_group['@kvg:radicalForm'],
    'tradForm', stroke_group['@kvg:tradForm'],
    'variant', stroke_group['@kvg:variant']
    )
$$;

CREATE OR REPLACE FUNCTION group_attributes(
    stroke_group OBJECT
    )
RETURNS OBJECT
AS
$$
OBJECT_CONSTRUCT(
    'element', stroke_group['@kvg:element'],
    'number', stroke_group['@kvg:number'],
    'original', stroke_group['@kvg:original'],
    'part', stroke_group['@kvg:part'],
    'partial', stroke_group['@kvg:partial'],
    'phon', stroke_group['@kvg:phon'],
    'position', stroke_group['@kvg:position'],
    'radical', stroke_group['@kvg:radical'],
    'radicalForm', stroke_group['@kvg:radicalForm'],
    'tradForm', stroke_group['@kvg:tradForm'],
    'variant', stroke_group['@kvg:variant']
    )
$$;

CREATE OR REPLACE FUNCTION stroke_attributes(
    stroke OBJECT
    )
RETURNS OBJECT
AS
$$
OBJECT_CONSTRUCT(
    'd', stroke['@d'],
    'type', stroke['@kvg:type']
    )
$$;

select * from StrokePath;

select * from StrokePath where node_tag = 'g';

create view StrokeGroup 
as
select
     *
from StrokePath 
where node_tag = 'g'
    ;


drop table if exists StrokePath;
create table StrokePath as 
    (
    select 
         seq as xml_id
        ,r.node_id              as svg_paths_id
        ,x.value['@id']         as node_id
        ,x.value['@']           as node_tag
        ,case x.value['@']
            when 'g' then group_attributes(x.value)
            when 'path' then stroke_attributes(x.value)
         end as node_attributes
        ,x.path                 as node_address
        ,coalesce(
             '[''$'']['||x.index||']'
            ,'['''||x.key||''']'
            )                   as final_address_component
        -- length(final_address_component) is overstated at the first-level child, but that's OK because its parent is the SVG Paths node.
        ,left(
             x.path
            ,length(x.path) - length(final_address_component)
            )                   as parent_node_address
    from root_group_extractor r
    cross join lateral flatten(r.children, recursive=>true) as x
    where x.value['@id'] is not NULL
    order by svg_paths_id, parent_node_address
    );

select 
    * 
from root_group_extractor
    ;

CREATE OR REPLACE FUNCTION merge_attributes(parent OBJECT, child OBJECT)
RETURNS OBJECT
LANGUAGE JAVASCRIPT
AS
$$
    // Parent first, then child overwrites
    return {...PARENT, ...CHILD};
$$;


CREATE OR REPLACE FUNCTION parse_svg_style(style_string VARCHAR)
RETURNS OBJECT
LANGUAGE JAVASCRIPT
AS
$$
    if (!STYLE_STRING) return null;
    
    return STYLE_STRING
        .split(';')
        .filter(pair => pair.trim())
        .reduce((obj, pair) => {
            const [key, value] = pair.split(':');
            if (key && value) {
                obj[key.trim()] = value.trim();
            }
            return obj;
        }, {});
$$;

/* Closing in on the target:  a minimalist version of what we want. */
create or replace view kanji_drawing_extractor
as
select
     codepoint_str                  as encoded_kanji
    ,decode_kanji(encoded_kanji)    as kanji
    ,kvg_variant_name               as kanji_variant
    ,kvg['@']                       as root_tag
    ,kvg['@height']                 as height
    ,kvg['@width']                  as width
    ,kvg['@xmlns']                  as dflt_namespace
    ,coalesce(
        -- alternate spellings
         kvg['@viewBox']
        ,kvg['@viewbox']
        )                           as viewbox
    ,kvg['$']                       as children
from kvg_upload
where kvg['@'] = 'svg'
    ;



create or replace view kanji_paths_extractor
as
select
     x.value['@id']                             AS node_id
    ,d.children[x.index]                        as paths_header
    ,x.value['@style']                          as svg_style
    ,x.value['@kvg:element']                    as element
    ,paths_header['@']                          as paths_tag
    ,paths_header['$']                          as stroke_groups
from kanji_drawing_extractor as d
cross join lateral flatten(d.children) as x
where node_id like 'kvg:StrokePaths%'
    ;


select 
     strtok_to_array(svg_style, ':;')
    ,parse_svg_style(svg_style)
from kanji_paths_extractor
    ;

create or replace view kanji_paths_extractor
as
select
     x.value['@id']                             AS node_id
    ,d.children[x.index]                        as paths_header
    ,parse_svg_style(x.value['@style'])         as svg_style
    ,x.value['@kvg:element']                    as element
    ,paths_header['@']                          as paths_tag
    ,paths_header['$']                          as stroke_groups
from kanji_drawing_extractor as d
cross join lateral flatten(d.children) as x
where node_id like 'kvg:StrokePaths%'
    ;

select * from kanji_paths_extractor;


create or replace view root_group_extractor
as
select
     p.stroke_groups['@id']                         as node_id
    ,p.stroke_groups['@']                           as node_tag
    ,p.stroke_groups['$']                           as children
from kanji_paths_extractor p
    ;

create or replace view path_node_extractor
as
select
     p.paths_header['@id']                         as node_id
    ,p.paths_header['@']                           as node_tag
    ,p.paths_header                                as node
from kanji_paths_extractor p
    ;


select
    *
from path_node_extractor
order by node_id
    ;

drop table if exists StrokePath;
create table StrokePath as 
    (
    select 
         seq as xml_id
        ,r.node_id              as svg_paths_id
        ,x.value['@id']         as node_id
        ,x.value['@']           as node_tag
        ,case x.value['@']
            when 'g' then group_attributes(x.value)
            when 'path' then stroke_attributes(x.value)
         end as node_attributes
        ,x.path                 as node_address
        -- CAVEAT:  'flatten' omits the explict array index 0 when there is exactly one child element. 
        --          Viz. the pedantic ['$'][0] becomes simply ['$'] in this case. --> see g6/s8 on 07980-Kaisho for an example.
        --          I don't believe that this matters for KanjiVG but it's worth noting on other sources. Is the behavior doc'd anywhere?
        ,coalesce(
             '[''$'']['||x.index||']'
            ,'['''||x.key||''']'
            )                   as final_address_component
        -- length(final_address_component) is overstated at the first-level child, but that's OK because its parent is the SVG Paths node.
        -- this issue goes away if I reroot up a level to the StrokePaths node --> but that's more trouble than it's worth.
        ,left(
             x.path
            ,length(x.path) - length(final_address_component)
            )                   as parent_node_address
        ,x.index as sort_order
    from root_group_extractor r  
    cross join lateral flatten(r.children, recursive=>true) as x
    where x.value['@id'] is not NULL
    order by svg_paths_id, parent_node_address
    );


-- kvg:StrokePaths_07980-Kaisho
select 
    *
from StrokePath
where svg_paths_id = 'kvg:07980-Kaisho'
order by node_id
    ;

/*
         x.value['@id']                     as id_attr
        ,NULL                               as parent_id_attr
        --
        ,x.value['@kvg:element']            as kanji_element
        ,x.value['@kvg:position']           as position
        ,x.value['@']                       as child_tag
        ,x.value['$']                       as child_groups
        ,1                                  as depth
    from root_group_extractor r
    CROSS JOIN TABLE(flatten_child_groups(r.child_groups)) AS x
    where x.value['@'] in ('path', 'g')

 */

CREATE OR REPLACE FUNCTION merge_attributes(parent OBJECT, child OBJECT)
RETURNS OBJECT
LANGUAGE JAVASCRIPT
AS
$$
    // Parent first, then child overwrites
    return {...PARENT, ...CHILD};
$$;

WITH RECURSIVE stroke_group_tree 
AS 
    (
    -- BASIS: children of the root stroke group
    select 
         'StrokePaths' as owner
        ,StrokePath.*
        ,node_attributes as full_attributes
        ,coalesce(node_attributes['position'], '') as effective_position
        ,1 as depth
    from StrokePath
    where   parent_node_address = ''
        -- and svg_paths_id = 'kvg:07980-Kaisho' 

    UNION ALL

    -- INDUCTIVE STEP: children of groups found so far
    select 
         right(parent.node_id, len(parent.node_id) - len(path.svg_paths_id) - 1)  as owner
        ,path.* 
        ,merge_attributes(parent.full_attributes, path.node_attributes) as full_attributes
        ,parent.effective_position || coalesce('-'||path.node_attributes['position'], '') as effective_position
        ,parent.depth + 1 as depth
    from stroke_group_tree parent
    inner join StrokePath path
        on  path.xml_id = parent.xml_id
        and path.svg_paths_id = parent.svg_paths_id
        and path.parent_node_address = parent.node_address
    where   parent.depth < 10       -- cheap guard
        AND parent.node_tag = 'g'   -- only groups, a/k/a the 'g' tags, have children
    )
select 
     full_attributes['element']         as element
    ,full_attributes['element'] 
     || case when full_attributes['part'] is not null then 'P' else '' end 
     || case when full_attributes['number'] is not null then 'N' else '' end 
                                        as effective_element
    ,effective_position
    ,full_attributes['type'] as stroke_type
    ,full_attributes['d'] as path
    ,substring(
         node_id
        ,length(svg_paths_id) + 3
        )::integer                      as seq_number
    ,svg_paths_id 
     || '-' || 
     case node_tag
        when 'g' then 'g'
        when 'path' then 's'
     end
     || trim(seq_number::varchar)       as reconstructed_node_id
    ,node_id = reconstructed_node_id    as seq_number_OK
    --,stroke_group_tree.*
from stroke_group_tree
where node_tag = 'path'
order by element, effective_position, stroke_type -- node_address
    ;

    ---> s8 is interesting:  it's a singleton, so the [0] offset for it into ['$'] get suppressed.  
    ---> how does that work with a singleton group in the parent/child address calculations? 

select kvg from kvg_upload where codepoint_str = '07980' and kvg_variant_name = 'Kaisho';

-- why isn't the "亠" element top-top and the "回" element top-bottom?  --> everything under one position should be part of the same thing?  Because they're different elements in the same position!
-- wheras "示" is one element divided into two groups that are *not* elements.
-- This has to have something to do with the radicals.
<svg height="109" viewBox="0 0 109 109" width="109" xmlns="http://www.w3.org/2000/svg">
  <g id="kvg:StrokePaths_07980-Kaisho" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">
    <g id="kvg:07980-Kaisho" kvg:element="禀">
      <g id="kvg:07980-Kaisho-g1" kvg:element="㐭" kvg:position="top">
        <g id="kvg:07980-Kaisho-g2" kvg:element="亠">
          <path d="M51.57,8.25c0.98,0.53,2.58,2.56,2.58,3.61c0,3.86-0.31,3.13-0.13,6.4" id="kvg:07980-Kaisho-s1" kvg:type="㇑a"></path>
          <path d="M19.83,20.19c1.73,0.34,3.26,0.72,5.25,0.48c11.86-1.43,47.16-3.18,60.99-3.88c2.03-0.1,3.07,0.04,4.59,0.61" id="kvg:07980-Kaisho-s2" kvg:type="㇐"></path>
        </g>
        <g id="kvg:07980-Kaisho-g3" kvg:element="回">
          <g id="kvg:07980-Kaisho-g4" kvg:element="囗" kvg:part="1">
            <path d="M29.2,27.78c0.68,0.63,1.25,1.8,1.42,2.59C32,36.5,33,41.25,35.31,52.5" id="kvg:07980-Kaisho-s3" kvg:type="㇑"></path>
            <path d="M31.54,28.79c13.09-1.11,38.69-3.29,46.89-3.29c1.87,0,2.59,1.05,2.38,2.31c-1.02,5.98-1.88,13.64-3.92,21.72" id="kvg:07980-Kaisho-s4" kvg:type="㇕a"></path>
          </g>
          <g id="kvg:07980-Kaisho-g5" kvg:element="口">
            <path d="M44.45,34.21c0.29,0.17,0.58,0.3,0.71,0.51c0.99,1.64,2.19,5.73,3.04,8.67" id="kvg:07980-Kaisho-s5" kvg:type="㇑"></path>
            <path d="M46.23,34.9c5.86-0.85,14.35-1.8,17.71-2.01c1.23-0.08,1.96,0.47,1.79,0.93c-0.73,1.91-1.58,4.22-2.66,6.86" id="kvg:07980-Kaisho-s6" kvg:type="㇕b"></path>
            <path d="M48.37,42.24c4.25-0.42,10.52-0.94,15.93-1.32" id="kvg:07980-Kaisho-s7" kvg:type="㇐b"></path>
          </g>
          <g id="kvg:07980-Kaisho-g6" kvg:element="囗" kvg:part="2">
            <path d="M35.95,50.25c11.3-0.75,29.5-1.81,41.45-2.4" id="kvg:07980-Kaisho-s8" kvg:type="㇐a"></path>
          </g>
        </g>
      </g>
      <g id="kvg:07980-Kaisho-g7" kvg:element="示" kvg:position="bottom" kvg:radical="general">
        <g id="kvg:07980-Kaisho-g8" kvg:position="top">
          <path d="M34.85,60.19c0.99,0.37,2.8,0.48,3.78,0.37c6.29-0.65,28.63-2.52,35.29-2.62c1.65-0.03,2.63,0.18,3.45,0.37" id="kvg:07980-Kaisho-s9" kvg:type="㇐"></path>
          <path d="M19.08,72.78c1.64,0.59,4.65,0.7,6.29,0.59c12.38-0.86,42.03-3.53,62.01-3.56c2.73,0,4.38,0.28,5.74,0.57" id="kvg:07980-Kaisho-s10" kvg:type="㇐"></path>
        </g>
        <g id="kvg:07980-Kaisho-g9" kvg:position="bottom">
          <path d="M54.86,73.97c0.07,0.37,1.42,1.92,1.42,4.27c0,4.51-0.25,13.05-0.25,16.89c0,8.15-3.5,2.93-6.74,0.19" id="kvg:07980-Kaisho-s11" kvg:type="㇚"></path>
          <path d="M35.48,83.05c0.05,0.39,0.1,1.01-0.1,1.57c-1.21,3.3-9.96,9.76-19.45,14.2" id="kvg:07980-Kaisho-s12" kvg:type="㇒"></path>
          <path d="M69.4,82.06c6.67,2.45,17.57,9.79,19.24,13.59" id="kvg:07980-Kaisho-s13" kvg:type="㇔"></path>
        </g>
      </g>
    </g>
  </g>
  <g id="kvg:StrokeNumbers_07980-Kaisho" style="font-size:8;fill:#808080">
    <text transform="matrix(1 0 0 1 44.50 9.50)">1</text>
    <text transform="matrix(1 0 0 1 12.50 20.50)">2</text>
    <text transform="matrix(1 0 0 1 23.75 36.50)">3</text>
    <text transform="matrix(1 0 0 1 35.75 26.50)">4</text>
    <text transform="matrix(1 0 0 1 40.50 40.33)">5</text>
    <text transform="matrix(1 0 0 1 47.50 33.50)">6</text>
    <text transform="matrix(1 0 0 1 50.50 40.50)">7</text>
    <text transform="matrix(1 0 0 1 38.50 47.50)">8</text>
    <text transform="matrix(1 0 0 1 28.50 61.50)">9</text>
    <text transform="matrix(1 0 0 1 16.50 70.95)">10</text>
    <text transform="matrix(1 0 0 1 45.50 81.88)">11</text>
    <text transform="matrix(1 0 0 1 24.50 84.50)">12</text>
    <text transform="matrix(1 0 0 1 61.50 88.50)">13</text>
  </g>
</svg>
