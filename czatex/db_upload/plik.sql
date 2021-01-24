GRANT ALL ON api.* TO 'root'@'%' identified by '1';
create table files (id int not null auto_increment primary key, user varchar(256) not null, name varchar(256) not null, localname varchar(256) not null);
