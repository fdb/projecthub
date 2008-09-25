from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `django_admin_log` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `action_time` datetime NOT NULL,
        `user_id` integer NOT NULL,
        `content_type_id` integer NULL,
        `object_id` longtext NULL,
        `object_repr` varchar(200) NOT NULL,
        `action_flag` smallint UNSIGNED NOT NULL,
        `change_message` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    -- The following references should be added but depend on non-existent tables:
""", """
    -- ALTER TABLE `django_admin_log` ADD CONSTRAINT user_id_refs_id_c8665aa FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
""", """
    -- ALTER TABLE `django_admin_log` ADD CONSTRAINT content_type_id_refs_id_288599e6 FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
"""], sql_down=["""
    DROP TABLE `django_admin_log`;
"""])
