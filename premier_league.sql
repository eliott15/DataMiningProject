CREATE TABLE `match_results` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `web_id` int,
  `date` varchar(255),
  `season` varchar(255),
  `competition` varchar(255),
  `home_team` varchar(255),
  `home_team_id` int,
  `away_team` varchar(255),
  `away_team_id` int,
  `stadium` varchar(255),
  `home_score` int,
  `away_score` int
);

CREATE TABLE `match_general_stats` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `match_id` int,
  `referee` varchar(255),
  `attendance` varchar(255),
  `kick_off` varchar(255),
  `HT_Score` varchar(255),
  `home_goals` varchar(255),
  `Home_RC_events` varchar(255),
  `away_goals` varchar(255),
  `away_RC_events` varchar(255),
  `home_assists` varchar(255),
  `away_assists` varchar(255),
  `king_of_the_match` varchar(255)
);

CREATE TABLE `match_advanced_stats` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `match_id` int,
  `home_possession` double,
  `away_possession` double,
  `home_shots_on_target` int,
  `away_shots_on_target` int,
  `home_shots` int,
  `away_shots` int,
  `home_touches` int,
  `away_touches` int,
  `home_passes` int,
  `away_passes` int,
  `home_tackles` int,
  `away_tackles` int,
  `home_clearances` int,
  `away_clearances` int,
  `home_corners` int,
  `away_corners` int,
  `home_offsides` int,
  `away_offsides` int,
  `home_yellow_cards` int,
  `away_yellow_cards` int,
  `home_red_cards` int,
  `away_red_cards` int,
  `home_fouls_conceded` int,
  `away_fouls_conceded` int
);

CREATE TABLE `players` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `season` varchar(255),
  `club` varchar(255),
  `club_id` int,
  `name` varchar(255),
  `number` int,
  `position` varchar(255),
  `nationality` varchar(255),
  `appearances` int,
  `clean_sheets` int,
  `goals` int,
  `assists` int
);

CREATE TABLE `teams_general` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `club` varchar(255),
  `season` varchar(255),
  `stadium` varchar(255),
  `matches_played` int,
  `wins` int,
  `losses` int,
  `goals` int,
  `goals_conceded` int,
  `clean_sheets` int
);

CREATE TABLE `teams_attack` (
  `id` int,
  `club` varchar(255),
  `season` varchar(255),
  `goals` int,
  `goals_per_match` int,
  `shots` int,
  `shots_on_target` int,
  `shooting_accuracy` varchar(255),
  `penalties_scored` int,
  `big_chances_created` int,
  `hit_woodwork` int
);

CREATE TABLE `teams_play` (
  `id` int,
  `club` varchar(255),
  `season` varchar(255),
  `passes` int,
  `passes_per_match` varchar(255),
  `pass_accuracy` varchar(255),
  `crosses` int,
  `cross_accuracy` varchar(255)
);

CREATE TABLE `teams_defence` (
  `id` int,
  `club` varchar(255),
  `season` varchar(255),
  `clean_sheets` int,
  `goals_conceded` int,
  `goals_conceded_per_match` varchar(255),
  `saves` int,
  `tackles` int,
  `tackle_success` varchar(255),
  `blocked_shots` int,
  `interceptions` int,
  `clearances` int,
  `headed_clearance` int,
  `duels_won` int,
  `errors_leading_to_goal` int,
  `own_goals` int
);

CREATE TABLE `teams_discipline` (
  `id` int,
  `club` varchar(255),
  `season` varchar(255),
  `yellow_cards` int,
  `red_cards` int,
  `fouls` int,
  `offsides` int
);

CREATE TABLE `match_weather` (
    `id` int PRIMARY KEY AUTO_INCREMENT,
    `match_id` int,
    `date` varchar(255),
    `city` varchar(255),
    `kick_off` varchar(255),
    `temperature` double,
    `humidity` double,
    `precipitation_mm` double,
    `wind_speed_km_h` double
);

ALTER TABLE `match_results` ADD FOREIGN KEY (`home_team_id`) REFERENCES `teams_general` (`id`);

ALTER TABLE `match_results` ADD FOREIGN KEY (`away_team_id`) REFERENCES `teams_general` (`id`);

CREATE INDEX web_id_index ON match_results(web_id);

ALTER TABLE `match_general_stats` ADD FOREIGN KEY (`match_id`) REFERENCES `match_results` (`web_id`);

ALTER TABLE `match_weather` ADD FOREIGN KEY (`match_id`) REFERENCES `match_results` (`web_id`);

ALTER TABLE `match_advanced_stats` ADD FOREIGN KEY (`match_id`) REFERENCES `match_results` (`web_id`);

ALTER TABLE `players` ADD FOREIGN KEY (`club_id`) REFERENCES `teams_general` (`id`);

ALTER TABLE `teams_attack` ADD FOREIGN KEY (`id`) REFERENCES `teams_general` (`id`);

ALTER TABLE `teams_play` ADD FOREIGN KEY (`id`) REFERENCES `teams_general` (`id`);

ALTER TABLE `teams_defence` ADD FOREIGN KEY (`id`) REFERENCES `teams_general` (`id`);

ALTER TABLE `teams_discipline` ADD FOREIGN KEY (`id`) REFERENCES `teams_general` (`id`);

ALTER TABLE match_results ADD CONSTRAINT uc1 UNIQUE (web_id);

ALTER TABLE match_general_stats ADD CONSTRAINT uc2 UNIQUE (match_id);

ALTER TABLE match_advanced_stats ADD CONSTRAINT uc3 UNIQUE (match_id);

ALTER TABLE players ADD CONSTRAINT uc4 UNIQUE (season, club_id, name);

ALTER TABLE teams_general ADD CONSTRAINT uc5 UNIQUE (club, season);

ALTER TABLE `teams_attack` ADD CONSTRAINT uc6 UNIQUE (`id`);

ALTER TABLE `teams_play` ADD CONSTRAINT uc7 UNIQUE (`id`);

ALTER TABLE `teams_defence` ADD CONSTRAINT uc8 UNIQUE (`id`);

ALTER TABLE `teams_discipline` ADD CONSTRAINT uc9 UNIQUE (`id`);

ALTER TABLE match_weather ADD CONSTRAINT uc10 UNIQUE (match_id);

