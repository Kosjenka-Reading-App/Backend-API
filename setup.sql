drop table if exists exercise_category;
drop table if exists doExercise;
drop table if exists user;
drop table if exists account;
drop table if exists exercise;
drop table if exists category;

create table exercise(
    id integer primary key,
    title varchar not null,
    text varchar not null,
    complexity float default 0.0
);

create table account(
    id_account integer primary key,
    email varchar not null,
    password varchar not null,
    account_category integer
);

create table user(
    id_user integer primary key,
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

create table category(
    category varchar primary key
);

create table exercise_category(
    exercise_id integer not null references exercise(id),
    category varchar not null references category(category)
)
