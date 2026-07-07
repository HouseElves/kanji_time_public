    /*
    <svg xmlns="http://www.w3.org/2000/svg" width="109" height="109" viewBox="0 0 109 109">
    <g id="kvg:StrokePaths_05cfa-Kaisho" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">
    <g id="kvg:05cfa-Kaisho" kvg:element="峺">
    ... stuff ...
    </g>
    <g id="kvg:StrokeNumbers_05cfa-Kaisho" style="font-size:8;fill:#808080">
    */
INSERT INTO KanjiDrawing
    (
     id             -- CHAR(5) NOT NULL
    ,variant        -- kanji_variant NOT NULL DEFAULT ''
    ,kanji_drawn    -- CHAR(1) NOT NULL
    ,width          -- SMALLINT
    ,height         -- SMALLINT
    ,line_style     -- TEXT
    ,text_style     -- TEXT
    )
VALUES
    (
     '05cfa'        -- parsed from id="kvg:StrokePaths_05cfa-Kaisho" on the first <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokePaths_05cfa-Kaisho" on the first <g> element under <svg>
    ,'峺'           -- from kvg:element="峺" on the 1st <g> element under StrokePaths
    ,109            -- from width="109" on the <svg> element 
    ,109            -- from height="109" on the <svg> element
    ,'fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;'
                    -- from style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;" on the 1st <g> element under <svg> (StrokePaths)
    ,'font-size:8;fill:#808080;'
                    -- from style="font-size:8;fill:#808080" on the 2n <g> element under <svg> (StrokeNumbers)
    );
/*
    <g id="kvg:05cfa-Kaisho-g1" kvg:element="山" kvg:position="left" kvg:radical="general">
*/
INSERT INTO KanjiStrokeGroup
    (
     KanjiDrawing_id                -- CHAR(5)
    ,KanjiDrawing_variant           -- kanji_variant NOT NULL DEFAULT ''
    ,idx                            -- SMALLINT NOT NULL
    ,kanji_element                  -- CHAR(1) NOT NULL
    ,position                       -- group_position
    ,radical                        -- radical_class
    )
VALUES 
    -- Extracted from attributes on <g> elements with id attribute ending in gN, N is an integer.
    (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-g1"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-g1"
    ,1                  -- parsed from id="kvg:05cfa-Kaisho-g1"
    ,'山'               -- from kvg:element="山" 
    ,'left'             -- from kvg:position="left"
    ,'general'          -- from kvg:radical="general"
    );
/* 
    <g id="kvg:05cfa-Kaisho-g2" kvg:element="更" kvg:position="right">
        <g id="kvg:05cfa-Kaisho-g3" kvg:element="日">
        <g id="kvg:05cfa-Kaisho-g4" kvg:element="乂">
            <g id="kvg:05cfa-Kaisho-g5" kvg:element="丿">
*/
INSERT INTO KanjiStrokeGroup
    (
     KanjiDrawing_id                -- CHAR(5)
    ,KanjiDrawing_variant           -- kanji_variant NOT NULL DEFAULT ''
    ,idx                            -- SMALLINT NOT NULL
    ,KanjiStrokeGroup_idx_parent    -- SMALLINT
    ,kanji_element                  -- CHAR(1) NOT NULL
    ,position                       -- group_position
    )
VALUES 
    -- Extracted from attributes on <g> elements with id attribute ending in gN, N is an integer.
    (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-g2"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-g2"
    ,2                  -- parsed from id="kvg:05cfa-Kaisho-g2"
    ,NULL               -- no open <g> element with id of the form "...-gN", N an integer
    ,'更'               -- from kvg:element="更" 
    ,'right'            -- from kvg:position="right"
    )
,   (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-g3"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-g3"
    ,3                  -- parsed from id="kvg:05cfa-Kaisho-g3"
    ,2                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'日'               -- from kvg:element="日" 
    ,'right'            -- INHERITED from the parent group
    )
,   (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-g4"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-g4"
    ,4                  -- parsed from id="kvg:05cfa-Kaisho-g4"
    ,2                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'乂'               -- from kvg:element="乂" 
    ,'right'            -- INHERITED from the parent group
    )
,   (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-g5"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-g5"
    ,5                  -- parsed from id="kvg:05cfa-Kaisho-g5"
    ,4                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'丿'               -- from kvg:element="丿" 
    ,'right'            -- INHERITED from the parent group
    )
    ;
/*
    <g id="kvg:05cfa-Kaisho-g1" kvg:element="山" kvg:position="left" kvg:radical="general">
        <path id="kvg:05cfa-Kaisho-s1" kvg:type="㇑a" d="M24.6,17.25c0.63,0.35,2.09,2.62,2.09,3.33c0,7.36,0.26,41.88,0.26,51.32"/>
        <path id="kvg:05cfa-Kaisho-s2" kvg:type="㇄a" d="M12.79,47.83c0.69,0.39,1.44,2.02,1.38,2.8c-0.39,5.38-0.37,14.58-1.75,22.67c-0.3,1.76,0.2,2.16,1.89,1.77c9.6-2.25,13.97-2.73,25.63-4.97"/>
        <path id="kvg:05cfa-Kaisho-s3" kvg:type="㇑" d="M40.17,42.55c0.69,0.39,1.38,2.88,1.38,3.67c0,6.05-0.8,16.29-1.45,26.07"/>
    </g>
*/
INSERT INTO KanjiStroke
    (
     KanjiDrawing_id        -- CHAR(5)
    ,KanjiDrawing_variant   -- kanji_variant NOT NULL DEFAULT ''
    ,idx                    -- SMALLINT NOT NULL
    ,KanjiStrokeGroup_idx   -- SMALLINT NOT NULL
    ,type                   -- kanji_stroke_type NOT NULL
    ,d                      -- TEXT NOT NULL
    )
VALUES 
    -- Extracted from attributes on <path> elements with id attribute ending in sM, M is an integer.
    (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-s1"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-s1"
    ,1                  -- parsed from id="kvg:05cfa-Kaisho-s1"
    ,1                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'㇑a'               -- from kvg:type="㇑a"
    ,'M24.6,17.25c0.63,0.35,2.09,2.62,2.09,3.33c0,7.36,0.26,41.88,0.26,51.32'
                        -- from d="M24.6,17.25c0.63,0.35,2.09,2.62,2.09,3.33c0,7.36,0.26,41.88,0.26,51.32"
    )
,   (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-s2"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-s2"
    ,2                  -- parsed from id="kvg:05cfa-Kaisho-s2"
    ,1                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'㇄a'               -- from kvg:type="㇄a"
    ,'M12.79,47.83c0.69,0.39,1.44,2.02,1.38,2.8c-0.39,5.38-0.37,14.58-1.75,22.67c-0.3,1.76,0.2,2.16,1.89,1.77c9.6-2.25,13.97-2.73,25.63-4.97'
                        -- from d="M12.79,47.83c0.69,0.39,1.44,2.02,1.38,2.8c-0.39,5.38-0.37,14.58-1.75,22.67c-0.3,1.76,0.2,2.16,1.89,1.77c9.6-2.25,13.97-2.73,25.63-4.97"
    )
,   (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-s3"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-s3"
    ,3                  -- parsed from id="kvg:05cfa-Kaisho-s3"
    ,1                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'㇑'               -- from kvg:type="㇑"
    ,'M40.17,42.55c0.69,0.39,1.38,2.88,1.38,3.67c0,6.05-0.8,16.29-1.45,26.07'
                        -- from d="M40.17,42.55c0.69,0.39,1.38,2.88,1.38,3.67c0,6.05-0.8,16.29-1.45,26.07"
    );
/*
    <g id="kvg:05cfa-Kaisho-g2" kvg:element="更" kvg:position="right">
        <path id="kvg:05cfa-Kaisho-s4" kvg:type="㇐" d="M46.82,18.65c0.97,0.48,2.75,0.61,3.71,0.48c6.17-0.83,27.08-3.46,36.91-3.6c1.62-0.02,2.58,0.23,3.39,0.47"/>
        <g id="kvg:05cfa-Kaisho-g3" kvg:element="日">
            <path id="kvg:05cfa-Kaisho-s5" kvg:type="㇑"  d="M47.23,31.91c0.52,0.76,1.05,1.7,1.05,2.72s3.64,25.11,3.81,26.12"/>
            <path id="kvg:05cfa-Kaisho-s6" kvg:type="㇕a" d="M49.15,33.14c2.96-0.13,37.24-3.75,39.93-3.9c2.25-0.13,3.54,1.16,2.89,4.97c-1.02,5.99-1.46,10.48-4.48,23.75"/>
            <path id="kvg:05cfa-Kaisho-s7" kvg:type="㇐a" d="M50.12,45.78c6.75-1.18,18.64-1.74,25.45-2.41c2.04-0.2,4.07-0.39,5.99-0.56"/>
            <path id="kvg:05cfa-Kaisho-s8" kvg:type="㇐a" d="M52.27,58.89c11.52-1.55,23.23-2.64,35.47-3.08"/>
        </g>
        <g id="kvg:05cfa-Kaisho-g4" kvg:element="乂">
            <g id="kvg:05cfa-Kaisho-g5" kvg:element="丿">
                <path id="kvg:05cfa-Kaisho-s9" kvg:type="㇒" d="M68.75,20c0.75,1.5,0.71,2.75,0.71,4.93c0,34.57-0.71,61.57-30.46,73.61"/>
            </g>
            <path id="kvg:05cfa-Kaisho-s10" kvg:type="㇏" d="M49.72,67.75C57.25,70,78,89.25,92.32,94.67c2.6,0.98,4.5,1.95,6.93,2.33"/>
        </g>
    </g>
*/
INSERT INTO KanjiStroke
    (
     KanjiDrawing_id        -- CHAR(5)
    ,KanjiDrawing_variant   -- kanji_variant NOT NULL DEFAULT ''
    ,idx                    -- SMALLINT NOT NULL
    ,KanjiStrokeGroup_idx   -- SMALLINT NOT NULL
    ,type                   -- kanji_stroke_type NOT NULL
    ,d                      TEXT NOT NULL
    )
VALUES 
    -- Extracted from attributes on <path> elements with id attribute ending in sM, M is an integer.
    (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-s4"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-s4"
    ,4                  -- parsed from id="kvg:05cfa-Kaisho-s4"
    ,2                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'㇐'               -- from kvg:type="㇐"
    ,'M46.82,18.65c0.97,0.48,2.75,0.61,3.71,0.48c6.17-0.83,27.08-3.46,36.91-3.6c1.62-0.02,2.58,0.23,3.39,0.47'
                        -- from d="M46.82,18.65c0.97,0.48,2.75,0.61,3.71,0.48c6.17-0.83,27.08-3.46,36.91-3.6c1.62-0.02,2.58,0.23,3.39,0.47"
    )
 ,  (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-s5"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-s5"
    ,5                  -- parsed from id="kvg:05cfa-Kaisho-s5"
    ,3                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'㇑'               -- from kvg:type="㇑"
    ,'M47.23,31.91c0.52,0.76,1.05,1.7,1.05,2.72s3.64,25.11,3.81,26.12'
                        -- from d="M47.23,31.91c0.52,0.76,1.05,1.7,1.05,2.72s3.64,25.11,3.81,26.12"
    )
 ,  (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-s6"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-s6"
    ,6                  -- parsed from id="kvg:05cfa-Kaisho-s6"
    ,3                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'㇕a'               -- from kvg:type="㇕a"
    ,'M49.15,33.14c2.96-0.13,37.24-3.75,39.93-3.9c2.25-0.13,3.54,1.16,2.89,4.97c-1.02,5.99-1.46,10.48-4.48,23.75'
                        -- from d="M49.15,33.14c2.96-0.13,37.24-3.75,39.93-3.9c2.25-0.13,3.54,1.16,2.89,4.97c-1.02,5.99-1.46,10.48-4.48,23.75"
    )
 ,  (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-s7"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-s7"
    ,7                  -- parsed from id="kvg:05cfa-Kaisho-s7"
    ,3                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'㇐a'               -- from kvg:type="㇐a"
    ,'M50.12,45.78c6.75-1.18,18.64-1.74,25.45-2.41c2.04-0.2,4.07-0.39,5.99-0.56'
                        -- from d="M50.12,45.78c6.75-1.18,18.64-1.74,25.45-2.41c2.04-0.2,4.07-0.39,5.99-0.56"
    )
 ,  (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-s8"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-s8"
    ,8                  -- parsed from id="kvg:05cfa-Kaisho-s8"
    ,3                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'㇐a'               -- from kvg:type="㇐a"
    ,'M52.27,58.89c11.52-1.55,23.23-2.64,35.47-3.08'
                        -- from d="M52.27,58.89c11.52-1.55,23.23-2.64,35.47-3.08"
    )
,  (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-s9"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-s9"
    ,9                  -- parsed from id="kvg:05cfa-Kaisho-s9"
    ,5                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'㇒'               -- from kvg:type="㇒"
    ,'M68.75,20c0.75,1.5,0.71,2.75,0.71,4.93c0,34.57-0.71,61.57-30.46,73.61'
                        -- from d="M68.75,20c0.75,1.5,0.71,2.75,0.71,4.93c0,34.57-0.71,61.57-30.46,73.61"
    )
,  (
     '05cfa'            -- parsed from id="kvg:05cfa-Kaisho-s10"
    ,'Kaisho'           -- parsed from id="kvg:05cfa-Kaisho-s10"
    ,10                  -- parsed from id="kvg:05cfa-Kaisho-s10"
    ,4                  -- from most recent open <g> element with id of the form "...-gN", N an integer
    ,'㇏'               -- from kvg:type="㇏"
    ,'M49.72,67.75C57.25,70,78,89.25,92.32,94.67c2.6,0.98,4.5,1.95,6.93,2.33'
                        -- from d="M49.72,67.75C57.25,70,78,89.25,92.32,94.67c2.6,0.98,4.5,1.95,6.93,2.33"
    );
/* 
<g id="kvg:StrokeNumbers_05cfa-Kaisho" style="font-size:8;fill:#808080">
    <text transform="matrix(1 0 0 1 15.50 17.85)">1</text>
    <text transform="matrix(1 0 0 1 5.66 44.85)">2</text>
    <text transform="matrix(1 0 0 1 32.71 40.50)">3</text>
    <text transform="matrix(1 0 0 1 45.50 15.50)">4</text>
    <text transform="matrix(1 0 0 1 39.50 36.50)">5</text>
    <text transform="matrix(1 0 0 1 50.50 30.50)">6</text>
    <text transform="matrix(1 0 0 1 53.50 42.50)">7</text>
    <text transform="matrix(1 0 0 1 55.50 55.50)">8</text>
    <text transform="matrix(1 0 0 1 61.50 26.53)">9</text>
    <text transform="matrix(1 0 0 1 44.44 74.46)">10</text>
</g>
*/
INSERT INTO KanjiStrokeAnnotation
    (
     KanjiDrawing_id        -- CHAR(5) 
    ,KanjiDrawing_variant   -- kanji_variant
    ,KanjiStroke_idx        -- SMALLINT 
    ,svg_transform          -- TEXT
    ,annotation             -- TEXT
    )
VALUES
    -- extracted from <text> elements
    (
     '05cfa'        -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,1              -- IMPLICIT in ordering (gross) or from tag content (even more gross)
    ,'matrix(1 0 0 1 15.50 17.85)'
                    -- from transform="matrix(1 0 0 1 15.50 17.85)"
    ,'1'            -- from tag content
    )
,   (
     '05cfa'        -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,2              -- IMPLICIT in ordering (gross) or from tag content (even more gross)
    ,'matrix(1 0 0 1 5.66 44.85)'
                    -- from transform="matrix(1 0 0 1 5.66 44.85)"
    ,'2'            -- from tag content
    )
,   (
     '05cfa'        -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,3              -- IMPLICIT in ordering (gross) or from tag content (even more gross)
    ,'matrix(1 0 0 1 32.71 40.50)'
                    -- from transform="matrix(1 0 0 1 32.71 40.50)"
    ,'3'            -- from tag content
    )
,   (
     '05cfa'        -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,4              -- IMPLICIT in ordering (gross) or from tag content (even more gross)
    ,'matrix(1 0 0 1 45.50 15.50)'
                    -- from transform="matrix(1 0 0 1 45.50 15.50)"
    ,'4'            -- from tag content
    )
,   (
     '05cfa'        -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,5              -- IMPLICIT in ordering (gross) or from tag content (even more gross)
    ,'matrix(1 0 0 1 39.50 36.50)'
                    -- from transform="matrix(1 0 0 1 39.50 36.50)"
    ,'5'            -- from tag content
    )
,   (
     '05cfa'        -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,6              -- IMPLICIT in ordering (gross) or from tag content (even more gross)
    ,'matrix(1 0 0 1 50.50 30.50)'
                    -- from transform="matrix(1 0 0 1 50.50 30.50)"
    ,'6'            -- from tag content
    )
,   (
     '05cfa'        -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,7              -- IMPLICIT in ordering (gross) or from tag content (even more gross)
    ,'matrix(1 0 0 1 53.50 42.50)'
                    -- from transform="matrix(1 0 0 1 53.50 42.50)"
    ,'7'            -- from tag content
    )
,   (
     '05cfa'        -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,8              -- IMPLICIT in ordering (gross) or from tag content (even more gross)
    ,'matrix(1 0 0 1 55.50 55.50)'
                    -- from transform="matrix(1 0 0 1 55.50 55.50)"
    ,'8'            -- from tag content
    )
,   (
     '05cfa'        -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,9              -- IMPLICIT in ordering (gross) or from tag content (even more gross)
    ,'matrix(1 0 0 1 61.50 26.53)'
                    -- from transform="matrix(1 0 0 1 61.50 26.53)"
    ,'9'            -- from tag content
    )
,   (
     '05cfa'        -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,'Kaisho'       -- parsed from id="kvg:StrokeNumbers_05cfa-Kaisho" on the second <g> element under <svg>
    ,10             -- IMPLICIT in ordering (gross) or from tag content (even more gross)
    ,'matrix(1 0 0 1 44.44 74.46)'
                    -- from transform="matrix(1 0 0 1 44.44 74.46)"
    ,'10'           -- from tag content
    );
