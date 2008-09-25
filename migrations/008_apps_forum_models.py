from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `forum_category` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(100) NOT NULL UNIQUE,
        `position` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `forum_forum` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `category_id` integer NOT NULL,
        `name` varchar(150) NOT NULL UNIQUE,
        `slug` varchar(50) NOT NULL UNIQUE,
        `description` varchar(200) NOT NULL,
        `position` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `forum_forum` ADD CONSTRAINT category_id_refs_id_fd95a89 FOREIGN KEY (`category_id`) REFERENCES `forum_category` (`id`);
""", """
    CREATE TABLE `forum_topic` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `forum_id` integer NOT NULL,
        `title` varchar(150) NOT NULL,
        `user_id` integer NOT NULL,
        `created_at` datetime NOT NULL,
        `updated_at` datetime NOT NULL,
        `hits` integer NOT NULL,
        `sticky` bool NOT NULL,
        `post_count` integer NOT NULL,
        `last_reply_at` datetime NULL,
        `last_reply_author_id` integer NULL,
        `locked` bool NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `forum_topic` ADD CONSTRAINT forum_id_refs_id_5f7ba639 FOREIGN KEY (`forum_id`) REFERENCES `forum_forum` (`id`);
""", """
    ALTER TABLE `forum_topic` ADD CONSTRAINT user_id_refs_id_649b8bac FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `forum_topic` ADD CONSTRAINT last_reply_author_id_refs_id_649b8bac FOREIGN KEY (`last_reply_author_id`) REFERENCES `auth_user` (`id`);
""", """
    CREATE TABLE `forum_post` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `topic_id` integer NOT NULL,
        `body` longtext NOT NULL,
        `user_id` integer NOT NULL,
        `created_at` datetime NOT NULL,
        `updated_at` datetime NOT NULL,
        `ip_address` char(15) NULL,
        `is_removed` bool NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `forum_post` ADD CONSTRAINT topic_id_refs_id_9b35c97 FOREIGN KEY (`topic_id`) REFERENCES `forum_topic` (`id`);
""", """
    ALTER TABLE `forum_post` ADD CONSTRAINT user_id_refs_id_2b14eec2 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `forum_post`;
""", """
    DROP TABLE `forum_topic`;
""", """
    DROP TABLE `forum_forum`;
""", """
    DROP TABLE `forum_category`;
"""])
