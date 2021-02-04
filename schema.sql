
drop table if exists professor_login;
    create table professor_login(
        username text not null PRIMARY KEY,
        password text not null
    );
	

drop table if exists feedback;
    create table feedback (
        id integer PRIMARY KEY AUTOINCREMENT,
        date text not null,
        time text not null,
        classCode text not null,
        studentCode text not null,
        emoji integer not null,
        elaborateNumber integer not null,
        elaborateText text not null,
        inClass text not null,
        -- inClass binary not null,
    );

	
drop table if exists account;
  create table account (
        professorName text not null ,
        schoolName text not null,
        departmentName text not null,
        classId text not null,
        classCode integer not null,
        entryId integer PRIMARY KEY AUTOINCREMENT,
		username text not null,
        classSize text not null,
		days text not null,
		classStart text not null,
		classEnd text not null,
        foreign key(username) references professor_login(username)
        );


drop table if exists schedule;
    create table schedule(
        username text not null,
		classCode text not null PRIMARY KEY,
        sDays text not null,
        sClassStart text not null,
        sClassEnd text not null,
        foreign key(username) references professor_login(username)
    )
