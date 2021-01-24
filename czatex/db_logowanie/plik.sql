GRANT ALL ON api.* TO 'root'@'%' identified by '1';
create table users (id int not null auto_increment primary key, login varchar(256) not null, pass varchar(256) not null);
