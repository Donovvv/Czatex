GRANT ALL ON api.* TO 'root'@'%' identified by '1';
create table chat (id int not null auto_increment primary key, user varchar(256) not null, file varchar(256), message varchar(256) not null);
