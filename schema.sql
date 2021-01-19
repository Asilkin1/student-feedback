drop table if exists feedback;
    create table feedback (
        id integer primary key autoincrement,
        date text not null,
        time text not null,
        classCode text not null,
        studentCode text not null,
        emoji integer not null,
        elaborateNumber integer not null,
        elaborateText text not null
    );