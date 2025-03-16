create table if not exists public.league
(
    league_id        varchar(17) not null
        primary key,
    country_id       varchar(17),
    league_logo      varchar(70),
    league_name      varchar(70),
    league_name_i18n varchar(255),
    sport_id         varchar(17)
);

alter table public.league
    owner to db_admin;

create table if not exists public.news
(
    news_id      varchar(17) not null
        primary key,
    news_content varchar(30000),
    image        varchar(70),
    published    timestamp(6),
    news_summary varchar(8196),
    news_tags    varchar(600),
    title        varchar(600)
);

alter table public.news
    owner to db_admin;

create table if not exists public.player
(
    player_id       varchar(17) not null
        primary key,
    country_id      varchar(17),
    player_dob      date,
    player_name     varchar(70),
    player_photo    varchar(70),
    player_position varchar(128)
);

alter table public.player
    owner to db_admin;

create table if not exists public.season
(
    season_id        varchar(17) not null
        primary key,
    season_name      varchar(35),
    season_end       date,
    season_start     date,
    league_id        varchar(17) not null
        constraint fks8kd4aueryljws3a8kj228jvm
            references public.league,
    season_name_i18n varchar(255)
);

alter table public.season
    owner to db_admin;

create table if not exists public.sport
(
    sport_id        varchar(17) not null
        primary key,
    is_active       boolean,
    desc_i18n       varchar(255),
    logo            varchar(70),
    sport_mode      varchar(17)
        constraint sport_sport_mode_check
            check ((sport_mode)::text = ANY
                   (ARRAY [('BOTH'::character varying)::text, ('BY_TEAM'::character varying)::text, ('INDIVIDUAL'::character varying)::text])),
    name_i18n       varchar(255),
    score_name      varchar(70),
    name            varchar(70),
    featured        boolean,
    score_name_i18n varchar(255)
);

alter table public.sport
    owner to db_admin;

create table if not exists public.stadium
(
    stadium_id varchar(17) not null
        primary key,
    capacity   integer,
    name_i18n  varchar(255),
    name       varchar(128),
    photo      varchar(70)
);

alter table public.stadium
    owner to db_admin;

create table if not exists public.match
(
    match_id      varchar(17) not null
        primary key,
    country_id    varchar(17),
    end_time      time(6),
    match_date    date,
    name          varchar(70),
    place         varchar(128),
    start_time    time(6),
    league_id     varchar(17),
    stadium_id    varchar(17)
        constraint fkojlcqppbrrr1l8kd4b8ta35sp
            references public.stadium
            on delete cascade,
    tournament_id varchar(17),
    rounds        varchar(40),
    season_id     varchar(17),
    statistic     varchar(4000),
    status        varchar(17)
);

alter table public.match
    owner to db_admin;

create table if not exists public.team
(
    team_id    varchar(17) not null
        primary key,
    country_id varchar(17),
    team_desc  varchar(255),
    team_logo  varchar(70),
    team_name  varchar(128),
    sport_id   varchar(17) not null
        constraint fkk1sdogt0khby5wtn58a2j1rdn
            references public.sport
);

alter table public.team
    owner to db_admin;

create table if not exists public.league_team
(
    instance_id   varchar(40) not null
        primary key,
    team_meta     varchar(255),
    team_position integer,
    league_id     varchar(17) not null
        constraint fk42nqg93tcmnm42c9jjvl4nr4k
            references public.league,
    season_id     varchar(17) not null
        constraint fkjaeynp5h4dwswmu65ad73sqcy
            references public.season,
    team_id       varchar(17) not null
        constraint fkwwjm5nxr1jrlklf5l0aqum7k
            references public.team
);

alter table public.league_team
    owner to db_admin;

create table if not exists public.match_detail
(
    match_detail_id varchar(255) not null
        primary key,
    home            boolean,
    visitor         boolean,
    match_id        varchar(17)
        constraint fkd9wrmrjlb1sydqo42dmpb1xxo
            references public.match,
    team_id         varchar(17)
        constraint fk5u2jk9e91vv1s31vidgjpnw2v
            references public.team
);

alter table public.match_detail
    owner to db_admin;

create table if not exists public.score_entity
(
    score_id        varchar(17)      not null
        primary key,
    points          double precision not null,
    match_detail_id varchar(17)
        constraint fk6dpior2ifpl309rmt20x2qowo
            references public.match_detail
);

alter table public.score_entity
    owner to db_admin;

create table if not exists public.team_players_entity
(
    player_meta varchar(255),
    season_id   varchar(17) not null
        constraint fkh0a065ra217hajcrw429cueq1
            references public.season,
    team_id     varchar(17) not null
        constraint fk91sdygsi6rxsivpcxjwfut803
            references public.team,
    player_id   varchar(17) not null
        constraint fkr42bm4vlwicexlqtxjxaexgs9
            references public.player,
    primary key (player_id, season_id, team_id)
);

alter table public.team_players_entity
    owner to db_admin;

create table if not exists public.tournament
(
    tournament_id   varchar(17) not null
        primary key,
    country_id      varchar(17),
    desc_i18n       varchar(1024),
    end_date        date,
    logo            varchar(70),
    name_i18n       varchar(255),
    season_id       varchar(17),
    start_date      date,
    tournament_year integer
);

alter table public.tournament
    owner to db_admin;

create table if not exists public.country
(
    country_id        varchar(17) not null,
    country_name      varchar(70) not null,
    country_name_i18n varchar(255),
    country_logo      varchar(70)
);

alter table public.country
    owner to db_admin;

