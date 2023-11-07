insert into exercise (id,title,text,complexity) values
    (1,"Tom the cat","Tom the cat was a nice fellow. Shame that he passed his entrance exams poorly",2.0),
    (2,"Matt the cat","Matt the cat was a nice fellow. Shame that he passed his entrance exams well",2.5),
    (3,"Bob the dog","Bob likes sticks. Bob go woof-woof. Bob go bark. Bo chase bike. Bob chika-bow-wow",1.0),
    (4,"Brian the dog","Brian like jokes. Brian go woof-woof,hooman go ha-ha. Brian like stick. Brian chase stick. Brian ean stick.",1.5),
    (5,"Finn the human","Finn is unimagenably sad and stressed. Finn's got a thesis to write. Finn doesn't have a thesis advisor.",9000.0);


insert into account (id_account,email,password,is_user,is_super_admin) values
    (1,"a@gmail.com","qwerty",true,false),
    (2,"b@gmail.com","asdfgh",true,false),
    (3,"c@gmail.com","123456",false,false),
    (4,"d@gmail.com","zxcvbn",false,false),
    (5,"e@gmail.com","uiop[]",false,true);

insert into account (id_account,password,is_user,is_super_admin) values
    (1,"qwerty",true,false),
    (2,"asdfgh",true,false),
    (3,"123456",false,false),
    (4,"zxcvbn",false,false),
    (5,"uiop[]",false,true);

insert into user (id_user,id_account,username,proficiency) values
    (1,1,"UserNameqwerty",null),
    (2,2,"UserNameasdfgh",2.0),
    (3,3,"UserName123456",3.3),
    (4,4,"UserNamezxcvbn",4.0),
    (5,5,"UserNameuiop[]",5.0);
