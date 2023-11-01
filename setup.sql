drop table doExercise;
drop table user;
drop table account;
drop table exercise;

create table exercise(
    id integer primary key,
    title varchar not null,
    text varchar not null,
    complexity float default 0.0
);

create table account(
    id_account primary key,
    password varchar not null,
    is_user boolean,
    is_super_admin boolean not null
);

create table user(
    id_user primary key,
    id_account references account(id_account),
    username varchar,
    proficiency float
);

create table doExercise(
    id_exercise references exercise(id),
    id_user references user(id_user),
    time_spent int,
    position int,
    completion float
);