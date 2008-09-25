from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `weblog_entry` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `title` varchar(100) NOT NULL,
        `slug` varchar(50) NOT NULL UNIQUE,
        `author_id` integer NOT NULL,
        `summary` longtext NOT NULL,
        `content` longtext NOT NULL,
        `published` bool NOT NULL,
        `created` datetime NOT NULL,
        `modified` datetime NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    -- The following references should be added but depend on non-existent tables:
""", """
    -- ALTER TABLE `weblog_entry` ADD CONSTRAINT author_id_refs_id_146484d5 FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `weblog_entry`;
"""])
