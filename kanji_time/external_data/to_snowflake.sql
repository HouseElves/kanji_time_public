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
select top 2
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

CREATE TABLE kanji_variant_metadata 
    (
     kanji_variant_value     VARCHAR PRIMARY KEY
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
