from dmigrations.mysql import migrations as m
import datetime
migration = m.AddColumn('forum', 'forum', 'posting_help', 'longtext NOT NULL')
