
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'db_admin') THEN
        CREATE ROLE db_admin WITH LOGIN PASSWORD 'caracas123';
        ALTER ROLE db_admin CREATEDB;
    END IF;
END
$$;

create table if not exists public.league
(
    league_id        varchar(128) not null
        primary key,
    country_id       varchar(17),
    league_logo      varchar(128),
    league_name      varchar(128),
    league_name_i18n varchar(1024),
    sport_id         varchar(128)
);


alter table public.league
    owner to db_admin;

create table if not exists public.news
(
    news_id      varchar(128) not null
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
    player_id       varchar(128) not null
        primary key,
    country_id      varchar(17),
    player_dob      date,
    player_name     varchar(255),
    player_photo    varchar(128),
    player_position varchar(128)
);

alter table public.player
    owner to db_admin;

create table if not exists public.season
(
    season_id        varchar(128) not null
        primary key,
    season_name      varchar(35),
    season_end       date,
    season_start     date,
    league_id        varchar(128) not null
        constraint fks8kd4aueryljws3a8kj228jvm
            references public.league,
    season_name_i18n varchar(1024)
);

alter table public.season
    owner to db_admin;

create table if not exists public.sport
(
    sport_id        varchar(128) not null
        primary key,
    is_active       boolean,
    desc_i18n       varchar(1024),
    logo            varchar(128),
    sport_mode      varchar(17)
        constraint sport_sport_mode_check
            check ((sport_mode)::text = ANY
                   (ARRAY [('BOTH'::character varying)::text, ('BY_TEAM'::character varying)::text, ('INDIVIDUAL'::character varying)::text])),
    name_i18n       varchar(1024),
    score_name      varchar(70),
    name            varchar(70),
    featured        boolean,
    score_name_i18n varchar(1024)
);

alter table public.sport
    owner to db_admin;

create table if not exists public.stadium
(
    stadium_id varchar(128) not null
        primary key,
    capacity   integer,
    name_i18n  varchar(1024),
    name       varchar(128),
    photo      varchar(128)
);

alter table public.stadium
    owner to db_admin;

create table if not exists public.match
(
    match_id      varchar(128) not null
        primary key,
    country_id    varchar(17),
    end_time      time(6),
    match_date    date,
    name          varchar(128),
    place         varchar(128),
    start_time    time(6),
    league_id     varchar(128),
    stadium_id    varchar(128)
        constraint fkojlcqppbrrr1l8kd4b8ta35sp
            references public.stadium
            on delete cascade,
    tournament_id varchar(128),
    rounds        varchar(40),
    season_id     varchar(128),
    statistic     varchar(4000),
    status        varchar(17)
);

comment on column public.match.status is 'SCHEDULED, IN_PROGRESS, COMPLETED, CANCELED, POSTPONE';

alter table public.match
    owner to db_admin;

create table if not exists public.team
(
    team_id    varchar(128) not null
        primary key,
    country_id varchar(17),
    team_desc  varchar(255),
    team_logo  varchar(70),
    team_name  varchar(128),
    sport_id   varchar(128) not null
        constraint fkk1sdogt0khby5wtn58a2j1rdn
            references public.sport
);

alter table public.team
    owner to db_admin;

create table if not exists public.league_team
(
    instance_id   varchar(128) not null
        primary key,
    team_meta     varchar(1024),
    team_position integer,
    league_id     varchar(128) not null
        constraint fk42nqg93tcmnm42c9jjvl4nr4k
            references public.league,
    season_id     varchar(128) not null
        constraint fkjaeynp5h4dwswmu65ad73sqcy
            references public.season,
    team_id       varchar(128) not null
        constraint fkwwjm5nxr1jrlklf5l0aqum7k
            references public.team
);

alter table public.league_team
    owner to db_admin;

create table if not exists public.match_detail
(
    match_detail_id varchar(128) not null
        primary key,
    home            boolean,
    visitor         boolean,
    match_id        varchar(128)
        constraint fkd9wrmrjlb1sydqo42dmpb1xxo
            references public.match,
    team_id         varchar(128)
        constraint fk5u2jk9e91vv1s31vidgjpnw2v
            references public.team
);

alter table public.match_detail
    owner to db_admin;

create table if not exists public.score_entity
(
    score_id        varchar(128)     not null
        primary key,
    points          double precision not null,
    match_detail_id varchar(128)
        constraint fk6dpior2ifpl309rmt20x2qowo
            references public.match_detail
);

alter table public.score_entity
    owner to db_admin;

create table if not exists public.team_players_entity
(
    player_meta varchar(1024),
    season_id   varchar(128) not null
        constraint fkh0a065ra217hajcrw429cueq1
            references public.season,
    team_id     varchar(128) not null
        constraint fk91sdygsi6rxsivpcxjwfut803
            references public.team,
    player_id   varchar(128) not null
        constraint fkr42bm4vlwicexlqtxjxaexgs9
            references public.player,
    primary key (player_id, season_id, team_id)
);

alter table public.team_players_entity
    owner to db_admin;

create table if not exists public.tournament
(
    tournament_id   varchar(128) not null
        primary key,
    country_id      varchar(17),
    desc_i18n       varchar(1024),
    end_date        date,
    logo            varchar(128),
    name_i18n       varchar(1024),
    season_id       varchar(128),
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

create table if not exists public.wohhu_params
(
    name          varchar(35) not null
        constraint wohhu_params_pk
            primary key,
    config_params oid
);

comment on table public.wohhu_params is 'Wohhu configuration parameters';

comment on column public.wohhu_params.name is 'Name of the configuration paramater';

comment on column public.wohhu_params.config_params is 'Configuration parameters';

alter table public.wohhu_params
    owner to db_admin;

create table if not exists public.pool
(
    pool_id                varchar(128) not null
        constraint pools_pk
            primary key,
    user_id                varchar(128) not null,
    pool_name              varchar(255) not null,
    pool_type              varchar(17)  not null,
    sport_id               varchar(128) not null
        constraint pool_sport_sport_id_fk
            references public.sport,
    pool_close_date        timestamp    not null,
    bet_type               varchar(17)  not null,
    ads_flag               boolean,
    ads_discount           numeric,
    ads_max_codes          integer,
    ads_percentage         numeric,
    bet_cost               numeric      not null,
    bet_rule               varchar(17)  not null,
    bet_currency           varchar(17)  not null,
    pool_guaranteed_amount numeric,
    pool_creation_fee      numeric      not null,
    pool_total_amount      numeric      not null,
    pool_image             varchar(128),
    pool_status            varchar(17)  not null,
    created_at             timestamp,
    updated_at             timestamp,
    pool_creation_fee_pct  numeric
);

comment on table public.pool is 'Table of pools';

comment on column public.pool.user_id is 'Owner of the pool';

comment on column public.pool.pool_name is 'Name of the bet';

comment on column public.pool.pool_type is 'Pool type: PUBLIC or PRIVATE';

comment on column public.pool.sport_id is 'Id of the sport';

comment on column public.pool.pool_close_date is 'Max date to allow registration of users';

comment on column public.pool.bet_type is 'Prize type: FIXED or VARIABLE';

comment on column public.pool.ads_flag is 'Flag to activate ads';

comment on column public.pool.bet_cost is 'Minimum bet';

comment on column public.pool.bet_rule is 'Rule: WITH_SCORE or WITHOUT_SCORE';

comment on column public.pool.pool_guaranteed_amount is 'Amount reserved when prize type is FIXED';

comment on column public.pool.pool_creation_fee is 'Creation fee';

comment on column public.pool.pool_total_amount is 'Total amount paid at creation (creation fee + guaranteedAmount)';

comment on column public.pool.pool_image is 'path to the image';

comment on column public.pool.pool_status is 'Status: CREATED, ACTIVE, AWARDED, PAID, DELETED';

alter table public.pool
    owner to db_admin;

create table if not exists public.pool_prize
(
    pool_id      varchar(128) not null
        constraint pool_prize_pools_pool_id_fk
            references public.pool
            on delete cascade,
    position     integer      not null,
    prize_amount numeric      not null,
    constraint pool_prize_pk
        primary key (position, pool_id)
);

comment on table public.pool_prize is 'Prizes of the pool';

comment on column public.pool_prize.pool_id is 'Reference to the pool';

comment on column public.pool_prize.position is 'Position of the prize (1, 2, 3 ...)';

comment on column public.pool_prize.prize_amount is 'Amount for FIXED prize or Percentage if VARIABLE';

alter table public.pool_prize
    owner to db_admin;

create table if not exists public.pool_registration
(
    pool_id             varchar(128) not null
        constraint pool_registration_pools_pool_id_fk
            references public.pool
            on delete cascade,
    user_id             varchar(128) not null,
    username            varchar(255) not null,
    user_email          varchar(255),
    registration_date   timestamp    not null,
    registration_status varchar(70),
    country_code        varchar(3),
    country_name        varchar(255),
    user_full_name      varchar(255),
    user_mobile         varchar(70),
    ip_address          varchar(70),
    constraint pool_registration_pk
        primary key (user_id, pool_id)
);

comment on table public.pool_registration is 'Registration of users to the pool';

comment on column public.pool_registration.pool_id is 'Reference to the pool';

comment on column public.pool_registration.user_id is 'Id of the registered user';

comment on column public.pool_registration.registration_status is 'Status of the registration: REGISTERED, ACTIVE or CANCELLED';

alter table public.pool_registration
    owner to db_admin;

create table if not exists public.pool_match
(
    pool_id         varchar(128) not null
        constraint pool_match_pool_pool_id_fk
            references public.pool
            on delete cascade,
    match_id        varchar(128) not null
        constraint pool_match_match_match_id_fk
            references public.match,
    weight          numeric,
    match_status    varchar(17)  not null,
    league_id       varchar(128)
        constraint pool_match_league_league_id_fk
            references public.league,
    league_name     varchar(128),
    league_logo     varchar(128),
    tournament_id   varchar(128)
        constraint pool_match_tournament_tournament_id_fk
            references public.tournament,
    tournament_name varchar(70),
    torunament_logo varchar(128),
    start_time      timestamp    not null,
    match_name      varchar(128) not null,
    constraint pool_match_pk
        primary key (pool_id, match_id)
);

comment on table public.pool_match is 'Relation between pool and match';

comment on column public.pool_match.weight is 'Weight of the match in the pool';

alter table public.pool_match
    owner to db_admin;

create table if not exists public.bet
(
    bet_id     varchar(128) not null
        constraint bet_pk
            primary key,
    pool_id    varchar(128) not null
        constraint bet_pool_pool_id_fk
            references public.pool,
    match_id   varchar(128) not null
        constraint bet_match_match_id_fk
            references public.match,
    user_id    varchar(128) not null,
    created_at timestamp    not null,
    updated_at timestamp,
    bet_amount numeric      not null,
    bet_status varchar(255) not null,
    ip_address varchar(70)
);

comment on table public.bet is 'Bets';

comment on column public.bet.bet_status is 'CREATED, PAID, REJECTED';

alter table public.bet
    owner to db_admin;

create table if not exists public.bet_results
(
    points integer      not null,
    reason varchar(17)  not null,
    bet_id varchar(128) not null
        constraint bet_results_bet_bet_id_fk
            references public.bet
            on delete cascade,
    constraint bet_results_pk
        primary key (bet_id, reason)
);

comment on table public.bet_results is 'Ranking of the pools';

comment on column public.bet_results.reason is 'RESULT, SCORE, DIFFERENCE';

alter table public.bet_results
    owner to db_admin;

create table if not exists public.pool_ranking
(
    pool_id        varchar(128) not null
        constraint pool_ranking_pk
            primary key
        constraint pool_ranking_pool_pool_id_fk
            references public.pool,
    user_id        varchar(128) not null,
    username       varchar(255) not null,
    user_full_name varchar(255),
    ranking        integer      not null,
    points         integer      not null,
    prize          numeric
);

comment on table public.pool_ranking is 'Ranking of the pool ';

comment on column public.pool_ranking.pool_id is 'Reference to the pool';

comment on column public.pool_ranking.user_id is 'User';

comment on column public.pool_ranking.ranking is 'Ranking in the pool';

comment on column public.pool_ranking.points is 'Accumulated points';

comment on column public.pool_ranking.prize is 'Prize - if nay';

alter table public.pool_ranking
    owner to db_admin;

create table if not exists public.bet_detail
(
    bet_id          varchar(128) not null
        constraint bet_detail_bet_bet_id_fk
            references public.bet
            on delete cascade,
    team_id         varchar(128)
        constraint bet_detail_team_team_id_fk
            references public.team,
    bet_result      varchar(35)  not null,
    bet_score       integer,
    player_id       varchar(128)
        constraint bet_detail_player_player_id_fk
            references public.player,
    bet_detail_id   varchar(128) not null
        constraint bet_detail_pk
            primary key,
    team_name       varchar(128),
    team_logo       varchar(128),
    team_country    varchar(70),
    player_name     varchar(255),
    player_photo    varchar(128),
    player_countryn varchar(70)
);

comment on column public.bet_detail.bet_result is 'Result of this team: WIN, DRAW, LOSE';

comment on column public.bet_detail.bet_score is 'Score in case of pool WITH_SCORE';

alter table public.bet_detail
    owner to db_admin;

