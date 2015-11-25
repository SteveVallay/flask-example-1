drop table if exists user;
create table user (
    id integer primary key autoincrement,
    username text unique not null,
    password text not null
);
drop table if exists otmap;
create table otmap (
    date text not null,
    otsrc text  not null,
    otdst text  not null,
    primary key (date,otdst)
);


