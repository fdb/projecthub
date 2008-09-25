from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `django_flatpage` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `url` varchar(100) NOT NULL,
        `title` varchar(200) NOT NULL,
        `content` longtext NOT NULL,
        `enable_comments` bool NOT NULL,
        `template_name` varchar(70) NOT NULL,
        `registration_required` bool NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `django_flatpage_sites` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `flatpage_id` integer NOT NULL,
        `site_id` integer NOT NULL,
        UNIQUE (`flatpage_id`, `site_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `django_flatpage_sites` ADD CONSTRAINT flatpage_id_refs_id_3f17b0a6 FOREIGN KEY (`flatpage_id`) REFERENCES `django_flatpage` (`id`);
""", """
    ALTER TABLE `django_flatpage_sites` ADD CONSTRAINT site_id_refs_id_4e3eeb57 FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`);
"""], sql_down=["""
    DROP TABLE `django_flatpage_sites`;
""", """
    DROP TABLE `django_flatpage`;
"""])
