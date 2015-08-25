SELECT upper(body) FROM note WHERE
(
(upper(body) LIKE '%GUN%' AND upper(body) ~ '\m(SHOT|HAND)?GUNS?\M') OR
(upper(body) LIKE '%RIFLE%' AND upper(body) ~ 'RIFLES?') OR
(upper(body) LIKE '%REVOLVER%') OR
(upper(body) LIKE '%PISTOL%')
)
AND NOT
(
(upper(body) ~ 'NO (SHOT|HAND)?GUNS?') OR
(upper(body) ~ 'TOY (GUN|RIFLE|SHOTGUN|PISTOL|HANDGUN)')
);