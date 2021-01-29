drop table if exists feedback;
    create table feedback (
        id integer PRIMARY KEY AUTOINCREMENT,
        date text not null,
        time text not null,
        classCode text not null,
        studentCode text not null,
        emoji integer not null,
        elaborateNumber integer not null,
        elaborateText text not null
    );

drop table if exists account;
  create table account (
        professorName text not null ,
        schoolName text not null,
        departmentName text not null,
        classId text not null,
        sectionName text not null,
        classCode integer not null,
        entryId integer PRIMARY KEY AUTOINCREMENT,
		username text not null,
        foreign key(username) references professor_login(username)
        );

drop table if exists professor_login;
    create table professor_login(
        username text not null PRIMARY KEY,
        password text not null
    );
