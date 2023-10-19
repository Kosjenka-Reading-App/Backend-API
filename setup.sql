create table exercise(
    id integer primary key,
    title varchar not null,
    text varchar not null,
    category varchar not null,
    complexity float default 0.0
);