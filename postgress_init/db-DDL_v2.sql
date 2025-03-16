create table league
(
    league_id        varchar(40) not null
        primary key,
    league_country   varchar(80),
    league_logo      varchar(70),
    league_name      varchar(35),
    league_name_i18n varchar(255),
    sport_id   varchar(40)
);

alter table league
    owner to wohhu;

create table news
(
    news_id      varchar(40) not null
        primary key,
    news_content varchar(40000),
    image        varchar(255),
    published    timestamp(6),
    news_summary varchar(8196),
    news_tags    varchar(600),
    title        varchar(600)
);

alter table news
    owner to wohhu;

create table player
(
    player_id       varchar(40) not null
        primary key,
    player_country  varchar(40),
    player_dob      date,
    player_name     varchar(70),
    player_photo    varchar(128),
    player_position varchar(80)
);

alter table player
    owner to wohhu;

CREATE TABLE season (
    season_id    VARCHAR(40) NOT NULL PRIMARY KEY,
    season_name  VARCHAR(35),
    season_end   DATE,
    season_start DATE,
    league_id    VARCHAR(40) NOT NULL,
    CONSTRAINT fk_league_id
        FOREIGN KEY (league_id)
        REFERENCES league (league_id)
);

alter table season
    owner to wohhu;

create table sport
(
    sport_id   varchar(40) not null
        primary key,
    is_active  boolean,
    desc_i18n  varchar(1024),
    logo       varchar(128),
    sport_mode varchar(17)
        constraint sport_sport_mode_check
            check ((sport_mode)::text = ANY
                   ((ARRAY ['BOTH'::character varying,
                    'BY_TEAM'::character varying,
                    'INDIVIDUAL'::character varying])::text[])),
    name_i18n  varchar(255),
    point_name varchar(70),
    name varchar(70)
);

alter table sport
    owner to wohhu;

create table stadium
(
    stadium_id varchar(255) not null
        primary key,
    capacity   integer,
    country    varchar(40),
    desc_i18n  varchar(1024),
    name       varchar(255),
    photo      varchar(255)
);

alter table stadium
    owner to wohhu;

create table tournament
(
    tournament_id   varchar(255) not null
        primary key,
    team_country    varchar(40),
    desc_i18n       varchar(1024),
    end_date        date,
    logo            varchar(128),
    name_i18n       varchar(255),
    season          varchar(40),
    start_date      date,
    tournament_year integer
);

alter table tournament
    owner to wohhu;

CREATE TABLE team (
    team_id       VARCHAR(40) NOT NULL PRIMARY KEY,
    team_country  VARCHAR(60),
    team_desc     VARCHAR(255),
    team_logo     VARCHAR(128),
    team_name     VARCHAR(128),
    sport_id      VARCHAR(40) NOT NULL,
    CONSTRAINT fk_sport_id
        FOREIGN KEY (sport_id)
        REFERENCES sport (sport_id)
);

alter table team
    owner to wohhu;

CREATE TABLE league_team (
    instance_id   VARCHAR(40) NOT NULL PRIMARY KEY,
    team_meta     VARCHAR(255),
    team_position INTEGER,
    league_id     VARCHAR(40) NOT NULL,
    season_id     VARCHAR(40) NOT NULL,
    team_id       VARCHAR(40) NOT NULL,
    CONSTRAINT fk_league_id
        FOREIGN KEY (league_id)
        REFERENCES league (league_id),
    CONSTRAINT fk_season_id
        FOREIGN KEY (season_id)
        REFERENCES season (season_id),
    CONSTRAINT fk_team_id
        FOREIGN KEY (team_id)
        REFERENCES team (team_id)
);

alter table league_team
    owner to wohhu;

CREATE TABLE match (
    match_id      VARCHAR(255) NOT NULL PRIMARY KEY,
    match_country VARCHAR(80),
    end_time      TIME(6),
    match_date    DATE,
    name          VARCHAR(70),
    place         VARCHAR(128),    
    start_time    TIME(6),
    league_id     VARCHAR(40),
    rounds        VARCHAR(40),
    season_id     VARCHAR(40),
    status        VARCHAR(40),
    statistic     VARCHAR(1600),
    
    CONSTRAINT fk_league_team
        FOREIGN KEY (league_id)
        REFERENCES league_team (instance_id),
    stadium_id    VARCHAR(255),
    CONSTRAINT fk_stadium
        FOREIGN KEY (stadium_id)
        REFERENCES stadium (stadium_id)
);

alter table match
    owner to wohhu;

CREATE TABLE match_detail (
    match_detail_id VARCHAR(255) NOT NULL PRIMARY KEY,
    home            BOOLEAN,
    visitor         BOOLEAN,
    match_id        VARCHAR(255),
    team_id         VARCHAR(40),
    CONSTRAINT fk_match
        FOREIGN KEY (match_id)
        REFERENCES match (match_id),
    CONSTRAINT fk_team
        FOREIGN KEY (team_id)
        REFERENCES team (team_id)
);

alter table match_detail
    owner to wohhu;

CREATE TABLE score_entity (
    score_id        VARCHAR(40)      NOT NULL PRIMARY KEY,
    points          DOUBLE PRECISION NOT NULL,
    match_detail_id VARCHAR(255),
    CONSTRAINT fk_match_detail
        FOREIGN KEY (match_detail_id)
        REFERENCES match_detail (match_detail_id)
);

alter table score_entity
    owner to wohhu;
    
CREATE TABLE team_players_entity (
    player_meta VARCHAR(255),
    season_id   VARCHAR(40) NOT NULL,
    team_id     VARCHAR(40) NOT NULL,
    player_id   VARCHAR(40) NOT NULL,
    PRIMARY KEY (player_id, season_id, team_id),
    CONSTRAINT fk_season
        FOREIGN KEY (season_id)
        REFERENCES season (season_id),
    CONSTRAINT fk_team
        FOREIGN KEY (team_id)
        REFERENCES team (team_id),
    CONSTRAINT fk_player
        FOREIGN KEY (player_id)
        REFERENCES player (player_id)
);


alter table team_players_entity
    owner to wohhu;

